import os
import sys
import logging
import docker
import py2neo
from linetimer import CodeTimer
from atexit import register
from Configs import getConfig
import datetime

config = getConfig()
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(getattr(logging, config.LOG_LEVEL))

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.append(os.path.normpath(SCRIPT_DIR))

from motherlode.data_sources_registry import DataSourcesRegistry


docker_client = docker.DockerClient(base_url=config.DOCKER_DEAMON_BASE_URL)


def get_graph():
    if config.NEO4J_USER is not None:
        return py2neo.Graph(
            config.NEO4J_URL, password=config.NEO4J_PASSWORD, user=config.NEO4J_USER
        )
    else:
        return py2neo.Graph(config.NEO4J_URL)


def create_log_node(dataloader_name, image):
    n = py2neo.Node("LoadingLog")
    reg_data = docker_client.images.get_registry_data(image.tags[0])
    n["loader"] = dataloader_name
    n["dockerhub_image_name"] = image.tags[0].split(":")[0]
    n["dockerhub_image_tag"] = image.tags[0].split(":")[1]
    n["dockerhub_image_hash"] = reg_data.id
    n["dockerhub_short_image_hash"] = reg_data.short_id
    n["loading_finished_at"] = str(datetime.datetime.now(tz=None))
    tx = get_graph().begin()
    tx.create(n)
    tx.commit()


def get_log_nodes(dataloader_name, image):
    return list(
        py2neo.NodeMatcher(get_graph()).match(
            "LoadingLog",
            dockerhub_image_name=image.tags[0].split(":")[0],
            dockerhub_image_tag=image.tags[0].split(":")[1],
            dockerhub_image_hash=docker_client.images.get_registry_data(
                image.tags[0]
            ).id,
        )
    )


def exit_func():
    # Clean up containers
    for datasource in get_sorted_data_sources(DataSourcesRegistry):
        name = "ML_{}".format(datasource["name"])
        clean_up_container(name)


register(exit_func)


def create_log_dir():
    os.makedirs(config.LOADING_LOGS_DIRECTORY, exist_ok=True)


def clean_up_container(name):
    try:
        c = docker_client.containers.get(name)
        log.warning("Get rid of old {}".format(name))
        try:
            c.kill()
        except docker.errors.APIError:
            pass
        try:
            c.remove()
        except docker.errors.APIError:
            pass
    except docker.errors.NotFound:
        pass


def get_sorted_data_sources(datasources_unsorted):
    """Returns the data sources sorted by dependencies and filters out datasources not relevant for the current environment
    
    """
    sorted_datasources = []
    try:
        current_env = os.environ["ENV"]
    except:
        current_env = "DEV"
    if config.DATALOADER_LIST:
        # filter out non listed datasources
        datasources_unsorted = [
            datasource
            for datasource in datasources_unsorted
            if datasource["name"] in config.DATALOADER_LIST
        ]
    if config.DATALOADER_SINGLE:
        datasources_unsorted = [
            datasource
            for datasource in datasources_unsorted
            if datasource["name"] == config.DATALOADER_SINGLE
        ]
        return datasources_unsorted

    def add_data_source(datasource):
        for index, dep in enumerate(datasource["dependencies"]):
            add_data_source(
                next(item for item in datasources_unsorted if item["name"] == dep)
            )
        if (
            next(
                (
                    item
                    for item in sorted_datasources
                    if item["name"] == datasource["name"]
                ),
                None,
            )
            is None
            and current_env not in datasource["exlude_in_env"]
        ):
            sorted_datasources.append(datasource)

    for datasource in datasources_unsorted:
        add_data_source(datasource)
    return sorted_datasources


def pull_image(image_name, force=True):
    log.info("Pull image '{}'...".format(image_name))
    if force:
        log.info("... pull forced, removing old image")
        try:
            docker_client.images.remove(image_name)
        except docker.errors.ImageNotFound:
            pass
    docker_client.images.pull(image_name, tag="latest")
    log.info("...image '{}' pulled.".format(image_name))


def absolute_volume_path(volumes):
    absolute_volumes = {}
    for vol, mount in volumes.items():
        if vol.startswith("."):
            absolute_volumes[os.path.abspath(vol)] = mount
    return absolute_volumes


def run_datasource_containers():

    create_log_dir()
    # gather env vars
    env_vars = {}
    try:
        env_vars["ENV"] = os.environ["ENV"]
    except:
        env_vars["ENV"] = "DEV"
    if config.NEO4J_URL is not None:
        env_vars["GC_NEO4J_URL"] = config.NEO4J_URL
    if config.NEO4J_USER is not None:
        env_vars["GC_NEO4J_USER"] = config.NEO4J_USER
    if config.NEO4J_PASSWORD is not None:
        env_vars["GC_NEO4J_PASSWORD"] = config.NEO4J_PASSWORD
    env_vars.update(config.OTHER_ENV_IN_DOCKER_CONTAINERS.items())

    log.info("force pull? {}".format(config.DOCKER_FORCE_FRESH_PULL))

    sorted_datasources = get_sorted_data_sources(DataSourcesRegistry)
    # iniitalize load status list; we use this to determine whether all prerequisites have been met for loading a datasource
    load_status = {ds["name"]: None for ds in sorted_datasources}
    log.info("load_status: {}".format(load_status))

    for datasource in sorted_datasources:
        envs = env_vars.copy()
        if "envs" in datasource:
            envs.update(datasource["envs"])
        log.info("###########################".format(datasource["dockerimage"]))
        container_name = "ML_{}".format(datasource["name"])
        log.info(
            "[{}]: checking dependencies: {}".format(
                datasource["name"], datasource["dependencies"]
            )
        )
        # check whether all dependencies are satisfied
        all_deps_fulfilled = True
        for dep in datasource["dependencies"]:
            if load_status[dep] != 0:
                log.warning("dependency {} not fulfilled, skipping.".format(dep))
                all_deps_fulfilled = False
        if not all_deps_fulfilled:
            continue
        log.info("Run Datasource container '{}'...".format(datasource["dockerimage"]))

        clean_up_container(container_name)
        pull_image(datasource["dockerimage"], config.DOCKER_FORCE_FRESH_PULL)

        image = docker_client.images.get(datasource["dockerimage"])
        image_docker_hub_id_short = docker_client.images.get_registry_data(
            image.tags[0]
        ).short_id
        log.info(
            "'{}' using image '{}'".format(image.tags[0], image_docker_hub_id_short)
        )
        log.info("  envs: {}".format(envs))

        log_nodes = get_log_nodes(datasource["name"], image)
        timer = CodeTimer("Timer", unit="m", silent=True)
        with timer:
            if log_nodes and not config.FORCE_RERUN_PASSED_DATALOADERS:
                # we skip this dataloader as it allready did a run
                log.info(
                    "[{}]: Skip Dataloader. Did already run at {}".format(
                        datasource["name"], log_nodes[0]["loading_finished_at"]
                    )
                )
                continue

            container = docker_client.containers.run(
                image,
                environment=envs,
                detach=True,
                name=container_name,
                volumes=absolute_volume_path(datasource["volumes"]),
                auto_remove=True,
            )
            log_file_path = os.path.join(
                config.LOADING_LOGS_DIRECTORY, "{}.log".format(datasource["name"])
            )
            for l in container.logs(
                stream=True, timestamps=True, follow=True, stderr=True, stdout=True
            ):
                log.info("[{}]: {}".format(datasource["name"], l.decode()))
                log_file = open(log_file_path, "a")
                log_file.write(l.decode())
                log_file.close()
            res = container.wait()

        log_file = open(log_file_path, "a")
        log_file.write("================================================")
        log_file.write("EXITED with status: {}".format(res["StatusCode"]))
        log_file.write("TIME TOOK: {} minutes".format(timer.took))
        log_file.close()
        log.info("[{}]: Finished with Exit Code:".format(res["StatusCode"]))
        if res["StatusCode"] != 0 and not config.CONTINUE_WHEN_ONE_DATALOADER_FAILS:
            log.error("[{}]: Cancel Motherlode:".format(datasource["name"]))
            exit(res["StatusCode"])
        elif res["StatusCode"] == 0:
            create_log_node(dataloader_name=datasource["name"], image=image)
        load_status[datasource["name"]] = res["StatusCode"]


if __name__ == "__main__":
    run_datasource_containers()
    # print(config.NEO4J_URL)

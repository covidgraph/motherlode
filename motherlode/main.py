import os
import sys
import logging
import docker
import py2neo
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
    n["loader"] = dataloader_name
    n["dockerhub_image_name"] = image.tags[0]
    n["dockerhub_image_hash"] = image.id
    n["loading_finished_at"] = str(datetime.datetime.now(tz=None))
    tx = get_graph().begin()
    tx.create(n)
    tx.commit()


def get_log_nodes(dataloader_name, image):
    return list(
        py2neo.NodeMatcher(get_graph()).match(
            "LoadingLog",
            dockerhub_image_name=image.tags[0],
            dockerhub_image_hash=image.id,
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
        c.remove()
    except docker.errors.NotFound:
        pass


def get_sorted_data_sources(datasources_unsorted):
    """Returns the data sources sorted by dependecies and filters out non environemnt relevant datasources
    
    """
    sorted_datasources = []
    try:
        current_env = os.environ["ENV"]
    except:
        current_env = "DEV"

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


def pull_image(image_name):
    log.info("Pull image '{}'...".format(image_name))
    docker_client.images.pull(image_name)
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

    for datasource in get_sorted_data_sources(DataSourcesRegistry):

        envs = env_vars.copy()
        if "envs" in datasource:
            envs.update(datasource["envs"])
        log.info("###########################".format(datasource["dockerimage"]))
        container_name = "ML_{}".format(datasource["name"])
        log.info("Run Datasource container '{}'...".format(datasource["dockerimage"]))

        clean_up_container(container_name)
        pull_image(datasource["dockerimage"])
        image = docker_client.images.get(datasource["dockerimage"])
        log.info("'{}' using image '{}'".format(datasource["dockerimage"], image.id))
        log_nodes = get_log_nodes(datasource["name"], image)
        if log_nodes and not config.FORCE_RERUN_PASSED_DATALOADERS:
            # we skip this dataloader as it allready did a run
            log.info(
                "[{}]: Skip Dataloader. Did allready run at {}".format(
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
        log_file.write("EXITED with status: {}".format(res))
        log_file.close()
        log.info("[{}]: Finished with Exit Code:".format(res["StatusCode"]))
        if res["StatusCode"] != 0 and not config.CONTINUE_WHEN_ONE_DATALOADER_FAILS:
            log.error("[{}]: Cancel Motherlode:".format(datasource["name"]))
            exit(res["StatusCode"])
        else:
            create_log_node(dataloader_name=datasource["name"], image=image)


if __name__ == "__main__":
    run_datasource_containers()
    # print(config.NEO4J_URL)

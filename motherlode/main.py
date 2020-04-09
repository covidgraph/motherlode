import os
import sys
import logging
import docker
from atexit import register
from Configs import getConfig

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


def exit_func():
    # Clean up containers
    for datasource in get_sorted_data_sources(DataSourcesRegistry):
        name = "ML_{}".format(datasource["name"])
        clean_up_container(name)


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


register(exit_func)


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


def pull_images():
    for datasource in get_sorted_data_sources(DataSourcesRegistry):
        log.info("Pull image '{}'...".format(datasource["dockerimage"]))
        docker_client.images.pull(datasource["dockerimage"])
        log.info("...image '{}' pulled.".format(datasource["dockerimage"]))


def run_datasource_containers():

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
    if config.NEO4J_PW is not None:
        env_vars["GC_NEO4J_PASSWORD"] = config.NEO4J_PW
    env_vars.update(config.OTHER_ENV_IN_DOCKER_CONTAINERS.items())

    for datasource in get_sorted_data_sources(DataSourcesRegistry):
        log.info("###########################".format(datasource["dockerimage"]))
        container_name = "ML_{}".format(datasource["name"])
        log.info("Run Datasource container '{}'...".format(datasource["dockerimage"]))
        clean_up_container(container_name)
        container = docker_client.containers.run(
            datasource["dockerimage"],
            environment=env_vars,
            detach=True,
            name=container_name,
        )
        for l in container.logs(
            stream=True, timestamps=True, follow=True, stderr=True, stdout=True
        ):
            log.info("[{}]: {}".format(datasource["name"], l.decode()))


if __name__ == "__main__":
    pull_images()
    run_datasource_containers()
    # print(config.NEO4J_URL)

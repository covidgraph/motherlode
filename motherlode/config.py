import os
from Configs import ConfigBase
import py2neo


class DEFAULT(ConfigBase):
    LOG_LEVEL = "INFO"
    LOADING_LOGS_DIRECTORY = "log"
    # Always create a DEFAULT class and use it as the base class for other environments classes
    NEO4J_URL = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "test"

    CONTINUE_WHEN_ONE_DATALOADER_FAILS = True

    # Motherlode will create nodes in the Neo4j DB with the label :LoadingLog every time a dataloader runs.
    # If a dataloader already did a run, a reload is usally not necessary and Motherlode will skip the dataloader.
    # If a dataloader image has changed and therefore has a new containerimage ID, it is treated as a "new" dataloader and motherlode will run it again.
    # If you want to rerun all dataloaders that already did run (and did not change their ID), set FORCE_RERUN_PASSED_DATALOADERS to True
    FORCE_RERUN_PASSED_DATALOADERS = False

    OTHER_ENV_IN_DOCKER_CONTAINERS = {}

    # this can be used to overwrite registry dataloader sequence. if you want to only run a certain dataloader for example
    DATALOADER_LIST = None
    # similar to DATALOADER_LIST but only to run a single dataloader. overrides DATALOADER_LIST
    DATALOADER_SINGLE = None

    # DOCKER_DEAMON_BASE_URL = "tcp://127.0.0.1:1234"
    DOCKER_DEAMON_BASE_URL = "unix://var/run/docker.sock"

    # setting this to false will allow re-use of cached Docker images (useful mainly for quicker debugging of master load script)
    DOCKER_FORCE_FRESH_PULL = True


# All following config classes inherit from DEFAULT
class PROD(DEFAULT):
    pass


class DEV(DEFAULT):
    pass


class LOCAL(DEFAULT):
    pass
    # DATALOADER_LIST = ["CORD19"]

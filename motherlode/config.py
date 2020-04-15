import os
from Configs import ConfigBase
import py2neo


class DEFAULT(ConfigBase):
    LOG_LEVEL = "INFO"
    LOADING_LOGS_DIRECTORY = "log"
    # Always create a DEFAULT class and use it as the base class for other environments classes
    NEO4J_URL = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PW = "test"  #

    CONTINUE_WHEN_ONE_DATALOADER_FAILS = False

    # Motherlode will create nodes in the Neo4j DB with the label :LoadingLog every time a dataloader runs.
    # If a dataloader allready did a run, a reload is usally not necessary and Motherlode will skip the dataloader.
    # If a dataloader image has changed and therefore has a new containerimage ID, its treated as "new" dataloader and motherlode will run it again.
    # If you want to rerun all dataloaders that allready did run (and did not changed its ID), set FORCE_RERUN_PASSED_DATALOADERS to True
    FORCE_RERUN_PASSED_DATALOADERS = False

    OTHER_ENV_IN_DOCKER_CONTAINERS = {"DATA_BASE_DIR": "FCUK"}

    # DOCKER_DEAMON_BASE_URL = "tcp://127.0.0.1:1234"
    DOCKER_DEAMON_BASE_URL = "unix://var/run/docker.sock"

    def get_graph(self):
        if self.NEO4J_USER is not None:
            return py2neo.Graph(
                self.NEO4J_URL, password=self.NEO4J_PASSWORD, user=self.NEO4J_USER
            )
        else:
            return py2neo.Graph(self.NEO4J_URL)


# All following config classes inherit from DEFAULT
class PROD(DEFAULT):
    pass


class DEV(DEFAULT):
    pass


class LOCAL(DEFAULT):
    pass

from Configs import ConfigBase


class DEFAULT(ConfigBase):
    LOG_LEVEL = "INFO"
    # Always create a DEFAULT class and use it as the base class for other environments classes
    NEO4J_URL = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PW = "test"  #

    OTHER_ENV_IN_DOCKER_CONTAINERS = {}

    # DOCKER_DEAMON_BASE_URL = "tcp://127.0.0.1:1234"
    DOCKER_DEAMON_BASE_URL = "unix://var/run/docker.sock"


# All following config classes inherit from DEFAULT
class PROD(DEFAULT):
    pass


class DEV(DEFAULT):
    pass

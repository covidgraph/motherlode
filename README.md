# Motherlode
**THIS README IS WIP**

Pipeline for running all dataloader scripts for covidgraph in a controlled manner.

Maintainer: Tim Bleimehl @tim.bleimehl:meet.dzd-ev.de https://github.com/motey


# What?

covidgraph.org is a project with the aim to build a knowledge graph around data concerning covid-19. For details go to https://covidgraph.org

The graph is fed by many independent scripts or scripts that are building on each other (called **dataloaders** here)

Motherlode helps to run these dataloaders in the correct sequence.

Scope of Motherlode is

* Resolving dependencies of dataloaders

* Keep track of which dataloaders are already fed in the graph

* Keep track of versions of the dataloaders (and rerun if updated)

# How?

## Run the Pipeline

Copy the `.env.template` to `.env`

`cp .env.template .env`

Edit the `.env` to match your Neo4j setup.

e.g. if your run your database localy

```
NEO4J={"host":"localhost","user":"neo4j","password":"neo"}
# legacy parameters.
# this is the old format, to provide the neo4j access data.
NEO4J_LECAGY_PARAMS="{'GC_NEO4J_URL':'localhost','GC_NEO4J_USER':'neo4j','GC_NEO4J_PASSWORD':'neo'}" 
``` 

Pull the latest pipeline docker image

`docker-compose pull`

Run the pipeline

`docker-compose up -d`

To see what is happening, you can monitor logs with

`docker-compose logs -f`

## Pipeline definition

Have a look at pipeline.yaml which is the pipeline definition. based on [copili](https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/tree/master/copili) and [motherlode](https://git.connect.dzd-ev.de/dzdtools/motherlode) written by the DZD

## Dataloaders / Pipeline Members

The format Motherlode accepts dataloaders is only as docker images from a registry (e.g. [DockerHub](https://hub.docker.com/))
Motherlode will run these images as containers an handle over some ENV variables to help dataloaders to connect to the database. 

For details have a look in at the dataloader template which comes as a python dataloader example: https://github.com/covidgraph/data_template

## Verify Pipeline runs

You can see which pipelinemembers had a run with checking the logging node in neo4j.

```
MATCH (n:`_PipelineLogNode`) RETURN n
``` 

The property `exit_code` should be `0` to verify that a loader run without any errors.

If the `exit_code` is not `0` have a look into the loaders log file in `./log`


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


## Pipeline

Have a look at pipeline.yaml which is the pipeline definition. based on [copili](https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/tree/master/copili) and [motherlode](https://git.connect.dzd-ev.de/dzdtools/motherlode) written by the DZD

## Dataloaders / Pipeline Members

The format Motherlode accepts dataloaders is only as docker images from a registry (e.g. [DockerHub](https://hub.docker.com/))
Motherlode will run these images as containers an handle over some ENV variables to help dataloaders to connect to the database. 

For details have a look in at the dataloader template which comes as a python dataloader example: https://github.com/covidgraph/data_template

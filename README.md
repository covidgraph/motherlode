# Motherlode
**THIS README IS WIP**

Pipeline for running all dataloader scripts for covidgraph in a controlled manner.

Maintainer: Tim Bleimehl @tim.bleimehl:meet.dzd-ev.de https://github.com/motey

# TL; DR
Run the complete pipeline against your own DB:
* ```cp env/DEFAULT.env env/myconf.env```
* change the DB connection in env/myconf.env
* run
```
ENV=myconf python main.py
```


# What?

covidgraph.org is a project with the aim to build a knowledge graph around data concerning covid-19. For details go to https://covidgraph.org

The graph is fed by many independent scripts or scripts that are building on each other (called **dataloaders** here)

Motherlode helps to run these dataloaders in the correct sequence.

Scope of Motherlode is

* Resolving dependencies of dataloaders

* Keep track of which dataloaders are already fed in the graph

* Keep track of versions of the dataloaders (and rerun if updated)

# How?

## Dataloaders

The format Motherlode accepts dataloaders is only as docker images from a registry (DockerHub only atm)
Motherlode will run these images as containers an handle over some ENV variables to help dataloaders to connect to the database. 

For details have a look in at the dataloader template which comes as a python dataloader example: https://github.com/covidgraph/data_template

## Mechanism

### Docker handling

Motherlode uses the [Docker SDK for python](https://docker-py.readthedocs.io/en/stable/) to manage the images and containers

### Registry

There is a file in the repo that serves as registry for dataloader at https://github.com/covidgraph/motherlode/blob/master/motherlode/data_sources_registry.py 


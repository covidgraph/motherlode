

DataSourcesRegistry = [
    {"name": "CORD19","dockerimage": "covidgraph/data-cord19", "dependencies": [],"exlude_in_env":["PROD"]},
    {
        "name": "JHU",
        "dockerimage": "covidgraph/data_jhu_population",
        "dependencies": [],
        "exlude_in_env":[]
    },
]
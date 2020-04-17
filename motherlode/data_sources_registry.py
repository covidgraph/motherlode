

DataSourcesRegistry = [
    {
        "name": "CORD19",
        "dockerimage": "covidgraph/data-cord19",
        "dependencies": [],
        "exlude_in_env": ["PROD"],
        "envs": {"CONFIGS_PAPER_BATCH_SIZE":"500", "NO_OF_PROCESSES":"16"},
        "volumes": {'./dataset/CORD19': {'bind': '/app/dataset', 'mode': 'rw'}}
    },
    {
        "name": "JHU",
        "dockerimage": "covidgraph/data_jhu_population",
        "dependencies": [],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {}
    },
    {
        "name": "TEXT_FRAGGER",
        "dockerimage": "covidgraph/graph-processing_fragmentize_text",
        "dependencies": ["CORD19"],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {}
    },
    {
        "name": "CELLMAP",
        "dockerimage": "covidgraph/data_cellmap",
        "dependencies": [],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {}
    }
]
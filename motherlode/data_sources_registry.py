

DataSourcesRegistry = [
    {
        "name": "CORD19",
        "dockerimage": "covidgraph/data-cord19",
        "dependencies": [],
        "exlude_in_env": ["PROD"],
        "envs": {"CONFIGS_PAPER_BATCH_SIZE":"200", "CONFIGS_NO_OF_PROCESSES":"25"},
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
    },
    {
        "name": "CELLMAP_ANNOTATION",
        "dockerimage": "covidgraph/cellmap_data_annotation",
        "dependencies": ['CELLMAP'],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {}
    }
]
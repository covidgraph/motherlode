



DataSourcesRegistry = [
    {
        "name": "JHU",
        "dockerimage": "covidgraph/data_jhu_population",
        "dependencies": [],
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
    },
    {
        "name": "LENS_PATENT_DATA",
        "dockerimage": "covidgraph/data-lens-org-covid19-patents",
        "dependencies": [],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {'./dataset/LENS_PATENT_DATA': {'bind': '/app/dataset', 'mode': 'rw'}}
    },
    {
        "name": "CORD19",
        "dockerimage": "covidgraph/data-cord19",
        "dependencies": [],
        "exlude_in_env": [],
        "envs": {"CONFIGS_PAPER_BATCH_SIZE":"300", "CONFIGS_NO_OF_PROCESSES":"25"},
        "volumes": {'./dataset/CORD19': {'bind': '/app/dataset', 'mode': 'rw'}}
    },
    {
        "name": "TEXT_FRAGGER",
        "dockerimage": "covidgraph/graph-processing_fragmentize_text",
        "dependencies": ["CORD19","LENS_PATENT_DATA"],
        "exlude_in_env": [],
        "envs": {},
        "volumes": {}
    },
]
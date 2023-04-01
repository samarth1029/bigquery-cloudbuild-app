bigquery-cloudbuild-app: execute queries and fetch results from Google BigQuery
==============================

This package can be used from within other python packages, or as a standalone CLI service to get data from bigquery table.

![Tests](https://github.com/bigquery-cloudbuild-app/actions/workflows/deploy_sandbox.yaml/badge.svg?branch=develop)

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

# Usage

### Calling The API

After cloning the repository, one is first required to provide their service account credentials for gcp as GOOGLE_APPLICATION_CREDENTIALS in the .env file.
The API endpoint can be called as shown below to fetch results:

```
url = "https://bigquery-cloudbuild-f7q24pru5q-ey.a.run.app/bigquery_operation_results"
headers = {"Content-type": "application/json"}
_dict = {
"query": f'''
        SELECT * FROM `project_name.dataset_name.table_name`        
        ''',
"gbq_table_id": "project_name.dataset_name.table_name",
}
_response = requests.post(url, headers=headers, json=_dict)
_result = _response.json()
```

### Requirements
#### Python - v3.9 minimum

## Setup for usage
### For using from other python packages
To use bigquery-cloudbuild-app as an imported package from another python project:
1. install `bigquery-cloudbuild-app` in the current project's virtual environment by importing the wheel distribution. E.g.:
   ```shell
   # if the wheel package is in the current folder
   $ pip install bigquery_cloudbuild_app-0.1.0-py2.py3-none-any.whl
   
   # if the wheel package is in another location
   $ pip install <path to bigquery_cloudbuild_app.whl>
   ```
### For using a standalone package
1. Set up a virtual environment (or conda environment). Although not mandatory, it is highly
   recommended separating each project's python environment. To create a virtual environment
   in the project directory itself with the native Python environment manager `venv`:
    ```bash
    $ cd /path/to/project/directory
    $ python3 -m venv .venv #sets up a new virtual env called .venv
    ```
   Next, to activate the virtual environment (say `.venv`):
    ```bash
    $ source .venv/Scripts/activate
    ```

# Testing

Tests are added in the `tests` dir.
1. To run all tests simply run:
   ```bash 
   $ pytest 
   ```
2. To run all the tests from one directory, use the directory as a parameter to pytest:
   ```bash
   $ pytest tests/my-directory
   ```
3. To run all tests in a file , list the file with the relative path as a parameter to pytest:
   ```bash
   $ pytest tests/my-directory/test_demo.py
   ```
4. To run a set of tests based on function names, the -k option can be used
   For example, to run all functions that have _raises in their name:
   ````shell
   $ pytest -v -k _raises
   ````

"""
utils for working with files: importing, reading, writing etc.
"""
import configparser
import csv
import io
import json
from pathlib import Path
import os
from datetime import datetime
import pandas as pd

from typing import Union


def import_file(full_path_to_module: str) -> object:
    """

    :param full_path_to_module:
    :return:
    """
    try:
        module_dir, module_file = os.path.split(full_path_to_module)
        module_name, module_ext = os.path.splitext(module_file)
        save_cwd = os.getcwd()
        os.chdir(module_dir)
        module_obj = __import__(module_name)
        module_obj.__file__ = full_path_to_module
        globals()[module_name] = module_obj
        os.chdir(save_cwd)
    except Exception as e:
        raise ImportError(e) from e
    return module_obj


def get_value_from_config_file(file_path: str, key: str) -> str:
    """
    get value for key in config file whose path is passed. Delimiter = ":" or "="
    :param file_path: filepath of the config_file
    :param key: key whose value is required
    :return: value for the key passed
    """
    with open(file_path, "r") as f:
        config_string = "[dummy_section]\n" + f.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    return config.get("dummy_section", key)


def get_write_data_file_name(
        file_path: str = None, file_name_prefix: str = None, file_ext: str = ".csv"
) -> str:
    """
    get file name for file to be written on disk
    :param file_path: where the data file is saved (w.r.t. OUTPUT_DATA_BASE_DIR)
    :param file_name_prefix: additional prefix for filename
    :param file_ext: file extension
    :return: str: full file_path
    """
    output_data_base_dir = os.path.join(get_project_path(path_id="data"), "JSON")
    file_path = output_data_base_dir + file_path if file_path else output_data_base_dir
    if not os.path.exists(file_path):
        os.makedirs(file_path)  # Create a new directory as it does not exist
    file_name = f"{file_name_prefix}_" if file_name_prefix else ""
    file_name += get_timestamp_string(datetime.now()) + file_ext
    return os.path.join(file_path, file_name)


def get_timestamp_string(
        timestamp: datetime = datetime.now(), string_format: str = "%Y%m%d_%H%M%S%f"
):
    return timestamp.strftime(string_format)


def save_data_as_file(
        file_type: str,
        data_to_write,
        filename_prefix: str,
        file_subdir: str,
        api_name: str = None,
) -> str:
    file_ext = f".{file_type}"
    file_path = get_write_data_file_name(
        file_path=file_subdir,
        file_name_prefix=filename_prefix,
        file_ext=file_ext,
    )
    if file_type == "json" and isinstance(data_to_write, dict):
        with open(file_path, "w") as fp:
            json.dump(data_to_write, fp, indent=4)
    elif file_type == "json" and isinstance(data_to_write, pd.DataFrame):
        json_string = data_to_write.to_json(orient="records")
        with open(file_path, "w") as fp:
            json.dump(json.loads(json_string), fp, indent=4)
    elif file_type == "csv" and isinstance(data_to_write, pd.DataFrame):
        data_to_write.to_csv(path_or_buf=file_path, index=False)
    else:
        print("something went wrong. No file write possible.")
        return ""
    print(f"{api_name or ''} {file_type} file saved at {file_path}")
    return file_path


def csv_to_json_content(content: str, key: str = "data") -> str:
    """
    converts csv content to json string, automatically recognising the delimiter
    :param content: str|csv content
    :param key: str|key used for creating dict for json
    :return: str|json string
    """
    delimiter = csv.Sniffer().sniff(io.StringIO(content).readline()).delimiter

    return json.dumps(
        {
            key: json.loads(
                pd.read_table(io.StringIO(content), delimiter=delimiter).to_json(
                    orient="records"
                )
            )
        },
        indent=4,
    )


def string_to_json_content(content: str, key: str = "data") -> str:
    """
    converts dict content to json string, pretty-printing it
    :param content: dict| content
    :param key: str|key used for creating dict for json
    :return: str|json string
    """

    return json.dumps(
        {key: json.loads(content)},
        indent=4,
    )


def get_raw_data_json_file_paths(raw_data_file_paths: list[str]) -> list:
    """
    return list of file-paths of json files from given list
    :param raw_data_file_paths:
    :return:
    """
    json_file_paths = [_path for _path in raw_data_file_paths if ".json" in _path]
    if not json_file_paths:
        print("WARNING: No json file found for upload. Exiting")
    return json_file_paths


def get_data_from_json_file(file_path: str) -> dict:
    """
    get raw data from json file in file-path
    :param file_path: str
    :return: dict | raw-data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        return json_data
    except FileNotFoundError as e:
        raise e


def get_filename_from_path(file_path: str) -> str:
    """
    get filename from json file
    :param file_path: str | file_path of json file
    :return: filename
    """
    return Path(file_path).stem


def get_project_path(
        path_id: Union[Path, str] = None, as_string: bool = True
) -> Union[Path, str]:
    """
    return the absolute path of passed path-id in project:
    * "root" or None: project-root /path/to/project-dir
    * "app": app-dir: {/path/to/project-root}/app
    * "config": config-dir : {/path/to/app-dir}/config
    * "data": data-dir : {/path/to/project-root}/data
    :param path_id:  str | (optional) identifier for path, options: root [default], app, data, tests, config
    :param as_string: bool | return result as string?
    :return: Path or str
    """
    project_root = Path(__file__).parent.parent.parent
    app_root = Path(__file__).parent.parent
    if not path_id or path_id == "root":
        path_id = project_root
    if isinstance(path_id, str):
        if path_id == "app":
            path_id = app_root
        elif path_id == "config":
            path_id = Path.joinpath(app_root, "config")
        elif path_id == "data":
            path_id = Path.joinpath(project_root, "data")
        elif path_id == "tests":
            path_id = Path.joinpath(project_root, "tests")
    return str(path_id) if as_string else path_id


def get_config_filename(file_id: str) -> str:
    """
    get the name of a config file for given file-id:
    * "MAPPING_CONFIG_FILE": json_key_mapping.json
    * "COUNTRY_CURRENCY_CODES": country_currency_codes.json
    :param file_id:  str | identifier for config-file, options listed above
    :return: str
    """

    if isinstance(file_id, str):
        if file_id == "COUNTRY_CURRENCY_CODES":
            return "country_currency_codes.json"
        elif file_id == "MAPPING_CONFIG_FILE":
            return "json_key_mapping.json"


def get_config_filepath(file_id: str) -> str:
    """
    get the path of a config file for given file-id:
    * "MAPPING_CONFIG_FILE": json_key_mapping.json
    * "COUNTRY_CURRENCY_CODES": country_currency_codes.json
    :param file_id:  str | identifier for config-file, options listed above
    :return: str
    """
    return os.path.join(
        get_project_path("config"),
        get_config_filename(file_id=file_id),
    )


def get_data_from_config_file(file_id: str) -> dict:
    """
    get the data from a config file for given file-id:
    * "MAPPING_CONFIG_FILE": json_key_mapping.json
    * "COUNTRY_CURRENCY_CODES": country_currency_codes.json
    :param file_id:  str | identifier for config-file, options listed above
    :return: str
    """
    _file_path = get_config_filepath(file_id=file_id)
    return get_data_from_json_file(file_path=_file_path)


if __name__ == "__main__":
    print([{_id: get_project_path(_id, True)} for _id in ["root", "app", "data"]])
    raw_data_dir = os.path.join(get_project_path("data"), "raw")
    test_file_name = "_bBEsUyu6ZNcLPbxAcGAxXZRF9io_7gckOD2En3Oz_k_MAN_EU_listFinancialEventsByGroupId_1661175810016_20220822_154334142242.json"
    _filedata = get_data_from_json_file(os.path.join(raw_data_dir, test_file_name))
    print(_filedata)
    _filename = get_filename_from_path(os.path.join(raw_data_dir, test_file_name))
    print(_filename)

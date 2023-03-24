"""
utils for GBQQ-usage
"""
import re
import json
from google.cloud import bigquery


def get_mapping_json_string_from_mssql_string(
    mssql_schema_string: str, do_camel_case: bool = True
) -> str:
    """
    return a mapping json string corresponding to a (multi-line) mssql schema string
    the mssql schema string is taken from create script for specific table.
    E.g.:
            [inc_id] [bigint] IDENTITY(1,1) NOT NULL,
            [Karton Typ] [nvarchar](255) NULL,
            [Produkt Typ] [nvarchar](255) NULL,
            [Farbe] [nvarchar](255) NULL,
            [Größe] [nvarchar](255) NULL,
    would be converted to:
            "incId": "inc_id:INT64",
            "kartonTyp": "Karton Typ:STRING",
            "produktTyp": "Produkt Typ:STRING",
            "farbe": "Farbe:STRING",
            "groesse": "Größe:STRING",
    :param mssql_schema_string:
    :param do_camel_case: bool | should the GBQ table columns be camel-case
    :return:
    """
    _list = mssql_schema_string.splitlines()
    print(_list)
    _mapping = {}
    for text in _list:
        if match := re.findall(r"\[([^]]+)]", text):
            _mapping_key = (
                camel_case(replace_special_characters_in_string(match[0]))
                if do_camel_case
                else replace_special_characters_in_string(match[0])
            )
            _mapping[_mapping_key] = f"{match[0]}:{convert_to_gbq_data_type(match[1])}"
    return json.dumps(_mapping, ensure_ascii=False, indent=4)


def replace_special_characters_in_string(str_with_char: str) -> str:
    """
    replace special characters not accepted in GBQ table col names
    :param str_with_char: str | string with unaccepted characters
    :return: str
    """
    return (
        str_with_char.replace("ü", "ue")
        .replace("ö", "oe")
        .replace("ä", "ae")
        .replace("Ü", "Ue")
        .replace("Ö", "Oe")
        .replace("Ä", "Ae")
        .replace("ß", "ss")
        .replace(" ", "_")
        .replace(",", "_")
        .replace(".", "_")
        .replace("/", "or")
    )


def camel_case(string: str) -> str:
    """
    convert given string to camel case
    :param string: str | normal string to be camel-cased
    :return: str | camel-case string
    """
    string = (
        re.sub(r"((?<=[a-z])(?=[A-Z]))|[^a-zA-Z]", " ", string).title().replace(" ", "")
    )
    return "".join([string[0].lower() + string[1:]])


def convert_to_gbq_data_type(data_type: str) -> str:
    """
    convert mssql data-type to gbq data-type
    If not found in mapping, MSSQL data-type is returned
    :param data_type: str | mssql server data-type
    :return: str | GBQ data-type
    """
    return {
        "int": "INT64",
        "bigint": "INT64",
        "smallint": "INT64",
        "varchar": "STRING",
        "nvarchar": "STRING",
        "decimal": "FLOAT64",
        "float": "FLOAT64",
        "bool": "BOOLEAN",
        "date": "DATE",
        "datetime": "TIMESTAMP",
    }.get(data_type, data_type)


def get_gbq_schema_from_json(
    table_name_key: str = None, schema_name_key: str = None
) -> list:
    """
    get schema for GBQ table based on table-name or schema-name as key
    :param table_name_key: str | table-name to be used as key
    :param schema_name_key: str | schema-name to be used as key
    :return: list | GBQ table schema as list of Schema-fields
    """
    bigquery_schema_list = []
    from app.utils.file_utils import (
        get_data_from_json_file,
        get_config_filepath,
    )

    _mapping_config_file = get_config_filepath("MAPPING_CONFIG_FILE")

    if not (
        json_data := get_data_from_json_file(
            file_path=get_config_filepath("MAPPING_CONFIG_FILE")
        )
    ):
        raise "mapping config file not found!"
    try:
        _key_map = (
            json_data.get(table_name_key.upper())
            or (json_data.get(schema_name_key.upper()) if schema_name_key else None)
        )

        if _key_map:
            if _db_col_mapping := _key_map.get("db_col_to_json_mapping"):
                bigquery_schema_list.extend(
                    bigquery.SchemaField(_key, _val.split(":")[-1])
                    for _key, _val in _db_col_mapping.items()
                )
    except AttributeError as e:
        print(f"{e}, returning empty schema")
    return bigquery_schema_list


def update_write_disposition(
    job_config: bigquery.LoadJobConfig, write_disposition: str = None
) -> bigquery.LoadJobConfig:
    """
    update config param write_disposition for given GBQ job
    :param job_config:
    :param write_disposition:
    :return:
    """
    if write_disposition and write_disposition == "overwrite":
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    else:
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    return job_config


if __name__ == "__main__":
    mssql_script_str = """
        [inc_id] [bigint] IDENTITY(1,1) NOT NULL,
        [Karton Typ] [nvarchar](255) NULL,
        [Produkt Typ] [nvarchar](255) NULL,
    """

    mapping = get_mapping_json_string_from_mssql_string(mssql_script_str)
    print(mapping)

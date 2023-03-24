import json
from tabulate import tabulate
import pandas as pd


def add_missing_dummy_columns(d, columns):
    missing_cols = set(columns) - set(d.columns)
    for c in missing_cols:
        d[c] = 0


def flatten_list(unflattened_list):
    if any(isinstance(i, list) for i in unflattened_list):
        return [item for sublist in unflattened_list for item in sublist]
    else:
        return unflattened_list


def clean_dict_text(dict_to_clean: dict) -> dict:
    """
    replace problematic characters in dict
    :param dict_to_clean: dict with problematic characters
    :return: dict with replaced char
    """
    # convert to string
    string_to_clean = json.dumps(dict_to_clean)

    return json.loads(
        string_to_clean.replace("\\–", "–")
        .replace("\\â", "â")
        .replace("\\’", "’")
        .replace("\\\\xf6", "ö")
        .replace("\\\\xfc", "ü")
        .replace("\\…", "…")
        .replace("\\\\xe4", "ä")
        .replace("\\ ", " ")
        .replace("\\\\xe9", "é")
        .replace("\\\\xf4", "ô")
        .replace("\\\\xe8", "è")
        .replace("\\‘", "‘")
        .replace('"GB_VOEC"', '""')
        .replace("GB_VOEC", '""')
    )


def clean_invalid_fields_from_list_of_dicts(
    data_to_clean: list, valid_fields: list
) -> list:
    """
    remove key-value pairs in dicts from a list of dicts, if key is not in list of valid fields
    :param data_to_clean: list| of dicts containing data from invalid fields
    :param valid_fields: list| of valid fields
    :return: list| of dicts containing valid fields
    """
    try:
        for _dict in data_to_clean:
            if isinstance(_dict, dict):
                for key in _dict.copy():
                    if key not in valid_fields:
                        del _dict[key]
        return data_to_clean
    except Exception as e:
        print(e)


def flatten_nested_dict(nested_dict: dict, sep: str = ".") -> dict:
    """
    flatten a nested_dict and use provided separator
    :param nested_dict: dict|nested_dict
    :param sep: str|separator to be used to separate nested keys
    :return: dict|flattened dict
    """
    from pandas.io.json._normalize import nested_to_record

    return nested_to_record(nested_dict, sep=sep)


def pretty_print_df(dataframe: pd.DataFrame) -> dict:
    """
    pretty print a df in pssql=-tabular form
    :param dataframe:
    :return: dict| with info of status of pretty_print_df
    """
    try:
        print(tabulate(dataframe, headers="keys", tablefmt="psql"))
        return {
            "msg": "success",
            "code": 202,
            "errors": None,
        }
    except Exception as e:
        print(f"Exception {e} occurred.")
        return {"msg": "failed", "code": 400, "errors": e}

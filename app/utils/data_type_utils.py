"""
utils to work with/on different data-types including interconversions
"""
from __future__ import annotations
from tabulate import tabulate
import pandas as pd
# from app.models.fin_attribute import FinAttribute
import re
from typing import Iterable, Generator


def flatten(items: Iterable) -> Generator:
    """Yield items from any nested iterable; returns a generator."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes, dict)):
            yield from flatten(x)
        else:
            yield x


def flatten_list(items) -> list:
    if not isinstance(items, Iterable):
        items = list(items)
    return list(flatten(items))


def diff_list_of_dicts(list_1, list_2):
    """
    given 2 list of dicts with similar keys, returns the difference between the 2 lists
    :param list_1:
    :param list_2:
    :return:
    """
    pairs = zip(list_1, list_2)
    return [(x, y) for x, y in pairs if x != y]


def get_list_of_dicts(list_of_objects: list) -> list[dict]:
    """
    given a list of objects, return a list of dicts with object-attributes as keys
    :param list_of_objects:
    :return: list[dict]
    """
    return [_list_item.__dict__ for _list_item in list_of_objects]


def get_flattened_list_of_dicts(unflattened_list: list) -> list:
    """
    return a flattened list of dicts from a nested list of objects
    :param unflattened_list: list | nested list of objects
    :return: list
    """
    flattened_list = flatten_list(items=unflattened_list)
    return [_list_item.__dict__ for _list_item in flattened_list]


def check_and_get_attr(class_obj: any, attrs: str | list[str]) -> any:
    """
    check if class_obj has any of the given attributes and return it
    if multiple attrs are passed, then the first attr has highest prio
    :param class_obj: obj in which attrs are checked
    :param attrs: str or list[str] | order is important
    :return:
    """
    if isinstance(attrs, str):
        attrs = [attrs]
    return next(
        (getattr(class_obj, attr) for attr in attrs if hasattr(class_obj, attr)),
        None,
    )


def get_any(dict_to_check: dict, key: str) -> any:
    """
    return value from dict if any of the dict-keys and key have intersection, e.g.:
    for dict_to_check =
            {'ChargeType': 'Principal', 'ChargeAmount': {'CurrencyCode': 'EUR', 'CurrencyAmount': 27.72}}
        and key = "ItemChargeAmount"
        dict =
            {'CurrencyCode': 'EUR', 'CurrencyAmount': 27.72}
        is returned
    :param dict_to_check: dict | dict whose keys are checked iteratively
    :param key: str | key which is checked
    :return: any | matching dict-values if found, else None
    """
    matching_dict_values_list = [
        dict_to_check.get(_key) for _key in dict_to_check if key in _key
    ] or [dict_to_check.get(_key) for _key in dict_to_check if _key in key]
    if len(matching_dict_values_list) > 1:
        print(f"Multiple matching values found: {matching_dict_values_list}")
    return matching_dict_values_list[0] if matching_dict_values_list else None


def camel_case_split(camel_case_string: str) -> list:
    """
    split camel case string into list of individual strings
    :param camel_case_string: str
    :return:
    """

    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", camel_case_string)


def get_by_path(nested_dict: dict, key_list: list):
    """
    Access a nested object in root by item sequence.
    :param nested_dict:
    :param key_list:
    :return:
    """
    from functools import reduce  # forward compatibility for Python 3
    import operator

    try:
        return reduce(operator.getitem, key_list, nested_dict)
    except (TypeError, KeyError):
        return None


def snake_to_camel_case(camel_case_str: str) -> str:
    result = camel_case_str.replace("_", " ").title()
    return result.replace(" ", "")


def pretty_print_df(dataframe: pd.DataFrame) -> dict:
    """

    :param dataframe:
    :return:
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


def fix_special_characters_in_json_keys(
    data_to_update: dict | list[dict] | pd.DataFrame,
) -> list[dict]:
    if isinstance(data_to_update, (dict, list)):
        if isinstance(data_to_update, dict):
            data_to_update = [data_to_update]
        _df = pd.DataFrame(data_to_update)
    else:
        _df = data_to_update
    _df.rename(columns=lambda x: replace_special_characters_in_string(x), inplace=True)
    return _df.to_dict(orient="records")


def replace_special_characters_in_string(str_with_char: str) -> str:
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
    )


def string_to_list_of_strings(string: str) -> list:
    """
    convert a string to list of strings:
    * "x" -> ["x]
    * "['x','y','z']" -> ["x", "y", "z"]
    * "['x','y',' z']" -> ["x", "y", "z"]
    :param string: str | string to be converted to list
    :return: list | of strings
    """
    import ast

    if "[" not in string or "]" not in string:
        return (
            [_item.strip() for _item in string.split(",")]
            if "," in string
            else [string]
        )
    string = ast.literal_eval(string)
    return [_item.strip() for _item in string]


def string_or_list_to_quoted_string_list(string_or_list: str | list) -> str:
    """
    convert a string to list of strings:
    * "x" -> '["x"]'
    * "["x","y","z"]" -> '["x","y","z"]'
    * "['x','y',' z']" -> '["x","y","z"]'
    :param string_or_list: str | string to be converted to list
    :return: list | of strings
    """
    _list_string = string_to_list_of_strings(string_or_list)
    _string = ",".join(f'"{_string}"' for _string in _list_string)
    return f'[{_string}]'


if __name__ == "__main__":
    _flat = flatten_list([1, 2, [3, 4], 5, "6", {"abc": 123}])
    print(_flat)

    assert string_to_list_of_strings(string='["x","y"," z"]') == ["x", "y", "z"]
    assert string_to_list_of_strings(string='x') == ["x"]
    assert string_to_list_of_strings(string='["x","y"," z"]') == ["x", "y", "z"]
    assert string_to_list_of_strings(string="x,y, z") == ["x", "y", "z"]


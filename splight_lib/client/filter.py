from typing import Any, Tuple, Dict


def value_filter(name: str, value: Any, item: Tuple[str, Dict]):
    satisfied = False
    if "__icontains" in name:
        variable_name = name.split("__")[0]
        satisfied = value in item[1].get(variable_name, None)
    elif "__in" in name:
        variable_name = name.split("__in")[0]
        satisfied = item[1].get(variable_name, None) in value
    else:
        satisfied = item[1].get(name, None) == value
    return satisfied

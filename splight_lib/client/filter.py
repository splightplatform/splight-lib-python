from typing import Any, Dict, Tuple


def value_filter(name: str, value: Any, item: Dict):
    satisfied = False
    if "__icontains" in name:
        variable_name = name.split("__")[0]
        satisfied = value in item.get(variable_name, None)
    elif "__in" in name:
        variable_name = name.split("__in")[0]
        satisfied = item.get(variable_name, None) in value
    else:
        satisfied = item.get(name, None) == value
    return satisfied


def value_filter_on_tuple(name: str, value: Any, item: Tuple[str, Dict]):
    return value_filter(name=name, value=value, item=item[1])

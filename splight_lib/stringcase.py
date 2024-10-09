def camelcase(string: str) -> str:
    """Convert string into camel case.

    Parameters
    ----------
    string: str
        String to convert.

    Returns
    -------
    str Camel case string.
    """
    if string == "":
        return string

    string = string.replace("_", "-")
    lst = string.split("-")
    for i in range(len(lst)):
        if i == 0:
            continue
        else:
            lst[i] = lst[i].capitalize()

    return "".join(lst)

# Splight Python SDK

![snyk_code](https://github.com/splightplatform/splight-lib-python/blob/gh-pages/snyk_code.svg?raw=True)
![snyk_dependencies](https://github.com/splightplatform/splight-lib-python/blob/gh-pages/snyk_dependencies.svg?raw=True)

---

## Installation

A release version can be installed using `pip` with

```bash 
pip install --upgrade splight-lib
```

or if you want one particular version you can use
```bash 
pip install splight-lib==x.y.z
```

### For Development

This library uses `uv` as package manager. In order to install `uv` you can 
use the command
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then to insall the library you can use the command in development mode you 
can use

```bash
uv sync
```

and for running a python interpreter within the environment you can use

```bash
uv run python
```


#### Managing versions

The package is managed using `poetry` so we should use this tool for handling
versioning. In particular, the repository contains a `Makefile` that contains 
the commands for updating the splight-lib versions. So, if you need to update
the version you should use the command

```bash
make update-version scope=<scope>
```
where scope can be `major`, `minor` or `patch`.

## Tests

```
make test
```

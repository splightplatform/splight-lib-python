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

To install the library in development mode you need to have `poetry` installed
```bash
pip install poetry==1.7.0
```

Then to insall the library you can use the command

```bash
poetry install
```

#### Managing versions

The package is managed using `poetry` so we should use this tool for handling
versioning. In particular, the repository contains a `Makefile` that contains 
the commands for updating the splight-lib versions. So, if you need to update
the version you should use the command

```bash
make update-version scope=<scope>
```
where scope can be `mayor`, `minor` or `patch`.

## Tests

```
make test
```

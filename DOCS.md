# Splight Library Python

The official **Splight** python library.

## Table of Contents  
- [Splight Library Python](#splight-library-python)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
    - [Requirements](#requirements)
  - [Usage](#usage)
    - [Splight API resources](#splight-api-resources)
    - [Splight Components](#splight-components)

## Description

The *Splight Python library* provides access to the Splight API from applications 
written in the Python language. It includes a user frendly interface for 
insteracting with different API resources and also defines the interface for 
creating and developing existing and new components that can be executed in the 
Splight Platform.

## Installation

You can install the library with pip
```sh
pip install --upgrade splight-lib
```

### Requirements

- Python 3.8+.

## Usage

In order to start using the library you need to configure it, there are two options 
for configuring it, one is based on environment variables and the second one is 
based on explicit parameters.

For using the configuration based on env vars, you need to create the variables
```sh
export SPLIGHT_ACCESS_ID=<your_access_id>
export SPLIGHT_SECRET_KEY=<your_secret_key>
````

Then, from python interpreter you can use
```python
from splight_lib.settings import settings

print(settings)
```

The second option is passing the variables values explicitly when creating the 
settings object

```python
from splight_lib.settings import SplightSettings

settings = SplightSettings(
    SPLIGHT_ACCESS_ID=<your_access_id>,
    SPLIGHT_SECRET_KEY=<your_secret_key>
)
```

### Splight API resources

The following snippet shows how to interact with API resources
```python
from splight_lib.models import Asset

all_assets = Asset.list()
print(all_assets)

single_asset = Asset.retrieve(<some_id>)
print(single_asset)

new_asset = Asset(
    namen="my-new-asset"
)
new_asset.save()
print(new_asset.id)
```

The same approach can be used for all the resources. The available resources are shown in 
the following table

| API Resource    |
|-----------------|
| Alert           |
| Asset           |
| Attribute       |
| Component       |
| ComponentObject |
| File            |
| Secret          |
| SetPoint        |
| Query           |

### Splight Components

One of the main features of the library is to develop new components that can run in the
**Splight** Platform. 

A *Component* is a process that runs in the **Splight** Platform for example for data 
processing, or data ingestion, etc. The scope of each *Component* is defined by the user that 
created the component. For creating a *Component* in Python you need to create at least two
files, one is the `spec.json` file which defines configurations for the component and a 
`main.py` file for coding the component's logics.

In the following example you can see the base structure of a component
```python
import random
from time import sleep

import typer

from splight_lib.component import SplightBaseComponent
from splight_lib.execution import Task
from splight_lib.logging import getLogger
from splight_lib.models import Asset


app = typer.Typer()


class MyComponent(SplightBaseComponent):
    def __init__(self, component_id: str):
        super().__init__(component_id)
        self._asset = Asset.retrieve(self.input.asset)
        self._attribute = self._asset.attributes[0]
        self._prediction_class = self.output.Predictions

    def start(self):
        self.execution_engine.start(
            Task(
                handler=self._get_random_number,
                args=(),
                period=self.input.period
            )
        )
        
    def _get_random_number(self):
        value = random.random()
        preds = Predictions(
            asset=self._asset,
            attribute=self._attribute,
            value=value,
        )
        preds.save()
        self._logger.(f"\nValue = {value}\n")
        

@app.command()
def main(
    component_id: str = typer.Option(...)
):
    logger = getLogger("MyComponent")
    component = MyComponent(
        component_id=component_id
    )
    try:
        component.start()
    except Exception as exc:
        logger.exception(exc, tags="EXCEPTION")
        component.stop()


if __name__ == "__main__":
    app()
```

Where the class `MyComponent` inherit from `SplightBaseComponent` which is the object
that defines a component and loads all the configuration defined in the `spec.json` file. 
For the above example, the `spec.json` file can be
```json
{
    "name": "MyComponent",
    "version": "1.0.0",
    "component_type": "algorithm",
    "tags": [],
    "privacy_policy": "public",
    "custom_types": [],
    "input": [
        {
            "name": "asset",
            "description": "Some Asset",
            "type": "Asset",
            "required": true,
            "value": null
        },
        {
            "name": "period",
            "description": "Period in second",
            "type": "float",
            "required": false,
            "value": 3600
        },
        {
            "name": "username",
            "description": "Username",
            "type": "str",
            "required": true,
            "value": ""
        }
    ],
    "output": [
        {
            "name": "Predictions",
            "fields": [
                {
                    "name": "value",
                    "type": "float"
                },
                {
                    "name": "asset",
                    "type": "Asset",
                    "filterable": true
                },
                {
                    "name": "attribute",
                    "type": "Attribute",
                    "filterable": true
                }
            ]
        }
    ]
}
```
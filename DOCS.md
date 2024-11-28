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
written in the Python language. It includes a user-friendly interface for 
interacting with different API resources and also defines the interface for 
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

In order to start using the library you need to configure it. There are two options 
for configuring it, one is based on environment variables and the second one is 
based on explicit parameters.

To set up using environment variables, you need to create the variables
```sh
export SPLIGHT_ACCESS_ID=<your_access_id>
export SPLIGHT_SECRET_KEY=<your_secret_key>
```

Then, from python interpreter you can use
```python
from splight_lib.settings import settings

print(settings)
```

The second option is passing the variable values explicitly when creating the 
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

One of the main uses of the library is to develop new components. 
A *Component* is a process that runs in the **Splight** Platform, for example, 
to do data processing, data ingestion, and more. The scope of each *Component* 
is defined by its developer and problem to be solved. 

To create a *Component* (in Python as an example), you need to write at least t
wo files: `spec.json` and `main.py`. 
- `spec.json`: defines the component interface
- `main.py`: contains the actual implementation of the algorithm

An important concept for creating and developing a *Component* is the "Routine". 
The easiest way to understand a Routine is thinking that a routine is task 
that takes some input, do a processing, and returns an output, where the 
input and output can be a list of asset/attributes pairs. The routines are 
defined in the `spec.json` file and are configured in the **Splight** Platform, 
then can be used in the component. 

Anyway, a routine not always is mapped to a simple task, depending on the 
component responsibility, could be convenient to group some routines into 
a single task for performance purposes, for example the case in which you want 
to read some information from a Rest API.

In the following code, we demonstrate a basic component that have
a routine defined in the spect that takes one Data Address (asset/attribute pair)
and writes the result in another Data Address.

Let start with spec definition for the component.
```JSON
{
    "name": "MyComponent",
    "version": "1.0.0",
    "component_type": "algorithm",
    "tags": ["tag1", "tag2"],
    "privacy_policy": "public",
    "custom_types": [],
    "routines": [
        {
            "name": "MyRoutine",
            "max_instances": 500,
            "config": [
                {
                    "name": "param1",
                    "description": "Some Description",
                    "type": "str"
                }
            ],
            "input": [
                {
                    "name": "input_value",
                    "description": "Some Description",
                    "value_type": "Number"
                }
            ],
            "output": [
                {
                    "name": "output_value",
                    "description": "Some Description",
                    "value_type": "Number"
                }
            ]
        }
    ],
    "input": [
        {
            "name": "period",
            "description": "Period in second",
            "type": "float",
            "required": false,
            "value": 3600
        }
    ]
}
```

The code for the component can be something like:

```python
import random
from time import sleep

import typer

from splight_lib.component import SplightBaseComponent
from splight_lib.execution import Task
from splight_lib.logging import getLogger
from splight_lib.models import Asset, Number


app = typer.Typer()


class MyComponent(SplightBaseComponent):
    def __init__(self, component_id: str):
        super().__init__(component_id)
        self._routine = self.routines.MyRoutine.list()[0]
        self._logger = getLogger("Component")

    def start(self):
        task = Task(
            target=self._get_random_number,
            period=self.input.period,
            targe_args=(),
        )
        self.execution_engine.add_task(task)
        self.execution_engine.start()
        
    def _get_random_number(self):
        # Read Data Address from the engine
        current_value = Number.get(
            asset=self._routine.input.input_value.asset,
            attribute=self._routine.input.input_value.attribute,
            limit_=1,
        )
        self._logger.info(f"Old value {current_value.value}")

        value = random.random()
        preds = Number(
            asset=self._routine.output.output_value.asset,
            attribute=self._routine.output.output_value.attribute,
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

Where the class `MyComponent` inherits from `SplightBaseComponent` which is the object
that defines a component and loads all the configuration defined in the `spec.json` file. 

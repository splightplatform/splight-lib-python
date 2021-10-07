![Coverage](https://bitbucket.org/<account>/<repository>/downloads/status.svg)

# Splight Library
Elements to build components. Language defined to sync BE and Worker tasks.

- **Connectors**: Data connectors. There is 1:1 relation between assets instances and connections
- **Assets**: Virtual unit that represents a physical device inside the electrical network.
- **Networks**: Set of Assets
- **DO Components (interface only)**: Single-purpose computacional unit. Its output should be useful to generate dashboards, raise alerts and bring predictions. 

## How to install

For development
- `python setup.py develop`

For productive envs.
- `python setup.py install`

## Tests
```
pytest splight_lib/tests
```

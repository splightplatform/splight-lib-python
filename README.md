![Coverage](https://bitbucket.org/<account>/<repository>/downloads/status.svg)

# Splight Library
Elements to build components. Language defined to sync BE and Worker tasks.

- **Asset**: Node to define a graph
- **Attribute**: Available property for node
- **ValueMapping**: Map an asset property to a static value
- **ReferenceMapping**: Map an asset property to another asset property
- **ClientMapping**: Map an asset property to a dynamic value read from a ClientConnector
- **ServerMapping**: Map an asset property to a dynamic value to be written in a ServerConnector

## How to install

For development
- `python setup.py develop`

For productive envs.
- `python setup.py install`

## Tests
```
pytest splight_lib/tests
```

# Splight Communication

## Types of communication
- External (_default_: Kafka)
- Internal (_default_: ZMQ)

## Message structure
We use JSON with the following structure:


``` 
{
    'action': <ACTION: Action>,
    'variables': [<VARIABLES: Variable>]
    ]
}
```

### Action (str):
- `update`: Apply action to datalake in order to update information about a particular asset
- `write`: Apply action to device writting in foreign protocols
- `subscribe`: Apply action to device to subscribe for changes in a set of variables
- `unsubscribe`: Apply action to device to subscribe for changes in a set of variables

### Variable
```
{
    'variables': [
        'path': <PATH: Path>
        'args': <ARGS: Args>
    ]
}
```

### Path (str)
This is just a str to map the variable in device.
For Hodor the only path values admitted are `reverse_proxy` and `proxy` to setup the instance.
For IOComponents this is modified in runtime and this keys can be different for each one. 
For DOComponents there is no communication at this point. 

### Args (dict)
This is an unstructered dictionary but most cases follow the _value_ structure 
```
{
    'value': [
            {
                'from': {
                    'ip': ,
                    'port': ,
                },
                'to': {
                    'ip': ,
                    'port': ,
                }
            }
        ]
}
```

```
{
    'value': 5
}
```


## Examples

- NETComponent

```
{
    'action': 'write',
    'variables': [
        'path': 'reverse_proxy'
        'args': {
            'value': [
                    {
                        'from': {
                            'ip': ,
                            'port': ,
                        },
                        'to': {
                            'ip': ,
                            'port': ,
                        }
                    }
                ]
        }
    ]
}
```

- IOComponent
```
{
    'action': 'update',
    'variables': [
        {
            'path': 'i35'
            'args': {
                'value': 5
            }
        },
    ]
}
```

```
{
    'action': 'subscribe',
    'variables': [
        {
            'path': 'i35'
            'args': {
                'interval': 5
                'interval_unit': 's'
            }
        },
    ]
}
```
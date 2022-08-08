# Remote Splight

This module's goal is to provide a simple interface for interact with the 
Splight API.

## Database

Example 
```python
from pydantic import BaseModel
from remote_splight_lib.database import DatabaseClient
from remote_splight_lib.auth import SplightAuthToken
from splight_models import Attribute, Asset


class AttributeValue(BaseModel):
    value: float
    
    
url = "https://integrationapi.splight-ae.com/"
access_key = "my-own-access-key"
secret_key = "my-own-secret-key"
token = SplightAuthToken(access_key, secret_key)
client = DatabaseClient(url, token=token)

attribute = Attribute(name="random-attribute")
created_attr = client.save("attribute", data=attribute)

asset = Asset(name="asset", description="Some Description")
created_asset = client.save("asset", data=asset)

value = client.endpoint(
    "post",
    path="/asset/{id}/set/{attr_id}/",
    path_params={
        "id": created_asset["id"], 
        "attr_id": created_attr["id"]
    },
    data=AttributeValue(value=2)
)
```

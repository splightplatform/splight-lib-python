# Remote Splight Lib

## Usage

```python
from remo

url = "https://integrationapi.splight-ae.com"
access_key = "splight_access_key"
secret_key = "splight_secret_key"
token = SplightAPIToken(access_key, secret_key)
client = SplightAPIClient(url, auth_token=token)
```

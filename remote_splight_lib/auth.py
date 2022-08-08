
class SplightAuthToken:
    def __init__(self, access_key: str, secret_key: str):
        self._token = f"Splight {access_key} {secret_key}"

    @property
    def header(self):
        return {"Authorization": self._token}

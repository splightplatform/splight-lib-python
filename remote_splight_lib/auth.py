from uplink.auth import ApiTokenHeader


class SplightAPIToken(ApiTokenHeader):
    _header = "Authorization"

    def __init__(self, spl_access_key, spl_secret_key):
        self._token = f"Splight {spl_access_key} {spl_secret_key}"

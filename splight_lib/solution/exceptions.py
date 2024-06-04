class MissingInstanceEnvVar(Exception):
    def __init__(self, env_var: str):
        super().__init__(f"Missing environment variable: {env_var}")


class MissingInstanceId(Exception):
    def __init__(self):
        super().__init__("Missing instance id")

class MissingInstanceEnvVar(Exception):
    def __init__(self, env_var: str):
        super().__init__(f"Missing environment variable: {env_var}")

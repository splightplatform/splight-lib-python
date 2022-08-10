from pydantic import BaseSettings


class SplightRemoteSettings(BaseSettings):
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ae.com"
    SPLIGHT_ACCESS_ID: str
    SPLIGHT_SECRET_KEY: str

settings = SplightRemoteSettings()

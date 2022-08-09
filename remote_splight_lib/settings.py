from pydantic import BaseSettings


class SplightRemoteSettings(BaseSettings):
    SPLIGHT_PLATFORM_API_HOST: str = "https://integrationapi.splight-ae.com"
    SPLIGHT_ACCESS_KEY: str
    SPLIGHT_SECRET_KEY: str


settings = SplightRemoteSettings()

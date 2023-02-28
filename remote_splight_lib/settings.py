from pydantic import BaseSettings, Field


class SplightRemoteSettings(BaseSettings):
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ae.com"
    SPLIGHT_ACCESS_ID: str = Field(
        ..., env=["SPLIGHT_ACCESS_ID", "SPLIGHT_AUTH_ACCESS_ID"]
    )
    SPLIGHT_SECRET_KEY: str = Field(
        ..., env=["SPLIGHT_SECRET_KEY", "SPLIGHT_AUTH_SECRET_KEY"]
    )


settings = SplightRemoteSettings()

from pydantic import BaseSettings, Field


class SplightRemoteSettings(BaseSettings):
    # TODO: Unify env variables accross all the platform/lib/components
    SPLIGHT_PLATFORM_API_HOST: str = Field(
        "https://api.splight-ae.com",
        env=["SPLIGHT_PLATFORM_API_HOST", "SPLIGHT_API_HOST"],
    )
    SPLIGHT_ACCESS_ID: str = Field(
        ..., env=["SPLIGHT_ACCESS_ID", "SPLIGHT_AUTH_ACCESS_ID"]
    )
    SPLIGHT_SECRET_KEY: str = Field(
        ..., env=["SPLIGHT_SECRET_KEY", "SPLIGHT_AUTH_SECRET_KEY"]
    )


settings = SplightRemoteSettings()

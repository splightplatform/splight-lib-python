from enum import Enum

from pydantic import BaseSettings


class ProviderSchemas(str, Enum):
    HTTP = "http"
    HTTPS = "https"


class SplightBlockchainConfig(BaseSettings):
    """Configuration for the Splight Blockchai module."""
    SCHEMA: ProviderSchemas = ProviderSchemas.HTTP
    PROVIDER: str = "34.229.23.244"
    PORT: int = 8545

    SPLIGHT_ADDRESS: str
    SPLIGHT_PRIVATE_KEY: str


blockchain_config = SplightBlockchainConfig()

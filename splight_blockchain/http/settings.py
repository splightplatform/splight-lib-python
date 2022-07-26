import os
from pydantic import BaseSettings


class SplightBlockchainConfig(BaseSettings):
    """Configuration for the Splight Blockchai module."""
    BLOCKCHAIN_RPC_URL: str = os.getenv("BLOCKCHAIN_RPC_URL", "https://chain.splight-ae.com")
    BLOCKCHAIN_CHAIN_ID: int = os.getenv("BLOCKCHAIN_CHAIN_ID", 1337)
    BLOCKCHAIN_PRIVATE_KEY: str = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

blockchain_config = SplightBlockchainConfig()

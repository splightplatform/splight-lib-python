from dataclasses import dataclass


@dataclass
class SmartContract:
    address: str
    abi: str

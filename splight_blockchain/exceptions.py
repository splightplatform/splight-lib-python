
class ProviderConnectionError(Exception):
    def __init__(self):
        self._msg = "Unable to connect to provider"

    def __str__(self) -> str:
        return self._msg


class TransactionNotAllowed(Exception):
    def __init__(self, transaction_name: str):
        self._msg = f"Transaction \"{transaction_name}\" is not allowed"

    def __str__(self) -> str:
        return self._msg


class LoadContractError(Exception):
    def __init__(self, address: str, contract_json: str):
        self._msg = (
            f"An error occurred loading contract {address} from "
            f"file {contract_json}"
        )

    def __str__(self) -> str:
        return self._msg

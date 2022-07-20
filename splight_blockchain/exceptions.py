class TransactionError(Exception):
    def __init__(self, tx_hash: str):
        self._msg = f"An error occurred during transaction {tx_hash}"

    def __str__(self) -> str:
        return self._msg


class FunctionCallError(Exception):
    def __init__(self, name: str):
        self._msg = f"An error occured calling function {name}"

    def __str__(self) -> str:
        return self._msg


class ProviderConnectionError(Exception):
    def __init__(self):
        self._msg = "Unable to connect to provider"

    def __str__(self) -> str:
        return self._msg


class ContractNotLoaded(Exception):
    def __init__(self):
        self._msg = "Smart Contract not loaded yet"

    def __str__(self) -> str:
        return self._msg


class FunctionTransactError(Exception):
    def __init__(self, method: str):
        self._msg = f"Method {method} not defined in smart contract"

    def __str__(self) -> str:
        return self._msg

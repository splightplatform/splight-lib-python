class AuthenticationError(Exception):
    def __init__(self, url: str, status_code: int):
        self._msg = (
            f"An error ocurred during authentication with status "
            f"code {status_code}"
        )

    def __str__(self) -> str:
        return self._msg


class SignatureVerificationError(Exception):
    def __init__(self, message, sig_header, http_body=None):
        super(SignatureVerificationError, self).__init__(message)
        self.sig_header = sig_header
        self._message = message
        self.http_body = http_body

    def __repr__(self):
        return f"{self.message} {self.http_body}"

    def __str__(self):
        return self._message

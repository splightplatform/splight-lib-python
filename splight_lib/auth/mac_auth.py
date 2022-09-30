import six
import hmac
import time
from hashlib import sha256
from splight_lib.auth.exceptions import SignatureVerificationError


def utf8(value):
    if six.PY2 and isinstance(value, six.text_type):
        return value.encode("utf-8")
    else:
        return value


class HmacSignature(object):
    EXPECTED_SCHEME = "v1"
    DEFAULT_TOLERANCE = 300

    def __init__(self, secret="", *args, **kwargs):
        self.secret = secret
        super().__init__(*args, **kwargs)

    @staticmethod
    def _compute_signature(payload, secret):
        mac = hmac.new(
            secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=sha256,
        )
        return mac.hexdigest()

    def compute_header_signature(self, payload: str):
        """
        Compute headers signature using hmac auth method.
        """
        timestamp = int(time.time())
        signed_payload = "%d.%s" % (timestamp, payload.decode("ascii"))
        mac_hexdigest = self._compute_signature(signed_payload, self.secret)
        return f"t={timestamp},{self.EXPECTED_SCHEME}={mac_hexdigest}"

    @staticmethod
    def _get_timestamp_and_signatures(header, scheme):
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = int([i[1] for i in list_items if i[0] == "t"][0])
        signatures = [i[1] for i in list_items if i[0] == scheme]
        return timestamp, signatures

    @classmethod
    def verify_header(cls, payload, header, secret, tolerance=DEFAULT_TOLERANCE):
        if hasattr(payload, "decode"):
            payload = payload.decode("utf-8")

        try:
            timestamp, signatures = cls._get_timestamp_and_signatures(
                header, cls.EXPECTED_SCHEME
            )
        except Exception:
            raise SignatureVerificationError(
                "Unable to extract timestamp and signatures from header",
                header,
                payload,
            )

        if not signatures:
            raise SignatureVerificationError(
                "No signatures found with expected scheme "
                "%s" % cls.EXPECTED_SCHEME,
                header,
                payload,
            )

        signed_payload = "%d.%s" % (timestamp, payload)
        expected_sig = cls._compute_signature(signed_payload, secret)
        if not any(hmac.compare_digest(utf8(expected_sig), utf8(s)) for s in signatures):
            raise SignatureVerificationError(
                "No signatures found matching the expected signature for "
                "payload",
                header,
                payload,
            )

        if tolerance and timestamp < time.time() - tolerance:
            raise SignatureVerificationError(
                "Timestamp outside the tolerance zone (%d)" % timestamp,
                header,
                payload,
            )

        return True

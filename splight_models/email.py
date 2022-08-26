from enum import Enum

class EmailType(Enum):
    """
    When adding a new type, remember to
    validate it as a sender in email service (SendGrid)
    """

    INFO = 'info'
    CONTACT_FORM = 'contact-form'
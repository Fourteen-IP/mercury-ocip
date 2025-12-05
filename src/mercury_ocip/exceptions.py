"""
Mercury exceptions
"""

import attr


@attr.s(slots=True, frozen=True)
class MError(Exception):
    """Base Exception raised by Mercury.

    Attributes:
        message: Why something failed
        context: BWKS Type/ Command that failed
    """

    message: str = attr.ib(default="An error occurred in unknown project name")
    context: object = attr.ib(default=None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"


@attr.s(slots=True, frozen=True)
class MErrorResponse(MError):
    """
    Exception raised when an ErrorResponse is received and decoded.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorTimeOut(MError):
    """
    Exception raised when nothing is head back from the server.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorUnknown(MError):
    """
    Exception raised when life becomes too much for the software.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorAPISetup(MError):
    """
    Exception raised when life becomes too much for the software.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorAttributeMissing(MError):
    """
    Exception raised when a required attribute is missing.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorUnexpectedAttribute(MError):
    """
    Exception raised when additional elements passed to __init__
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorSocketInitialisation(MError):
    """
    Exception raised when the TCP socket fails to initiate.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorSocketTimeout(MError):
    """
    Exception raised when the TCP socket fails to initiate.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorSendRequestFailed(MError):
    """
    Exception raised when a requester send request command fails.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorClientInitialisation(MError):
    """
    Exception raised when the SOAP Client fails to initiate.
    """

    pass


@attr.s(slots=True, frozen=True)
class MErrorFailedXMLConversion(MError):
    """
    Exception raised when Parser fails to translate XML data to a Dictionary.
    """

    pass

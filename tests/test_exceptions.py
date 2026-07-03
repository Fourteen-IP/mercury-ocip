"""Regression tests for exception ergonomics.

MError classes were previously attrs frozen=True, which broke Python's
exception machinery: re-raising through a contextmanager assigns
exc.__traceback__, which frozen __setattr__ rejected with
FrozenInstanceError — masking the real (e.g. BroadWorks) error.
"""

from contextlib import contextmanager

import pytest

from mercury_ocip.exceptions import MError, MErrorResponse


@contextmanager
def _tracked():
    """Mimics plugin/_tracked style wrappers: catch, act, re-raise."""
    try:
        yield
    except MErrorResponse:
        raise


def test_merror_survives_contextmanager_reraise():
    with pytest.raises(MErrorResponse) as excinfo:
        with _tracked():
            raise MErrorResponse(message="[Error 8349] Access Code already exists")

    assert "[Error 8349]" in str(excinfo.value)


def test_merror_dunders_are_assignable():
    e = MError(message="boom")
    e.__traceback__ = None  # what `raise` and contextlib need to do
    exc = MErrorResponse(message="inner")
    exc.__cause__ = e  # what `raise ... from ...` needs to do
    assert str(exc) == "MErrorResponse(inner)"


def test_merror_str_keeps_class_and_message():
    assert str(MErrorResponse(message="detail")) == "MErrorResponse(detail)"
    assert str(MError()) == "MError(An error occurred in unknown project name)"

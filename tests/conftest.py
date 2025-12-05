"""
shared fixtures for tests
"""

import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_dispatch_table():
    """Use real command classes from the SDK"""
    with (
        patch("mercury_ocip.client.BaseClient._dispatch_table") as mock_dis_table,
    ):

        def mock_table():
            return {
                "AuthenticationRequest": "AuthenticationRequest",
                "LoginRequest22V5": "LoginRequest22V5",
                "LoginRequest14sp4": "LoginRequest14sp4",
                "AuthenticationResponse": "AuthenticationResponse",
                "LoginResponse22V5": "LoginResponse22V5",
                "LoginResponse14sp4": "LoginResponse14sp4",
                "ErrorResponse": "ErrorResponse",
                "SuccessResponse": "SuccessResponse",
            }

        mock_dis_table.side_effect = mock_table
        yield mock_dis_table

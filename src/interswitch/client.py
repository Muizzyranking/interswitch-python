"""
Main Interswitch SDK client.
"""

from typing import Any, TypeVar

from pydantic import BaseModel

from interswitch.config import Config
from interswitch.http_client import HttpClient
from interswitch.interswitch_types import (
    BankAccountResponse,
    BVNBooleanResponse,
    BVNResponse,
    NINResponse,
)
from interswitch.token_manager import TokenManager

T = TypeVar("T", bound=BaseModel)


class InterswitchClient:
    """
    Main client for Interswitch API operations.
    """

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        base_url: str | None = None,
        token_url: str | None = None,
        token_expiry: int | None = None,
        request_timeout: int | None = None,
    ) -> None:
        """
        Initialize Interswitch client.
        """
        self.config = Config(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            token_url=token_url,
            token_expiry=token_expiry,
            request_timeout=request_timeout,
        )

        self.token_manager = TokenManager(self.config)
        self.http_client = HttpClient(self.config, self.token_manager)

    def verify_nin(self, nin: str) -> NINResponse:
        """
        Verify National Identification Number (NIN) and get full details.
        """
        endpoint = "/marketplace-routing/api/v1/verify/identity/nin/verify"
        data = {"id": nin}
        return self.http_client.post(endpoint=endpoint, response_model=NINResponse, data=data)

    def verify_bvn_full(self, bvn: str) -> BVNResponse:
        """
        Verify Bank Verification Number (BVN) and get full details.
        """
        endpoint = "/marketplace-routing/api/v1/verify/identity/bvn/verify"
        data = {"id": bvn}
        return self.http_client.post(endpoint=endpoint, response_model=BVNResponse, data=data)

    def verify_bvn_boolean(
        self,
        bvn: str,
        first_name: str,
        last_name: str,
        date_of_birth: str,
    ) -> BVNBooleanResponse:
        """
        Verify BVN with boolean match (yes/no verification).
        """
        endpoint = "/marketplace-routing/api/v1/verify/identity/bvn/boolean"
        data = {
            "id": bvn,
            "firstName": first_name,
            "lastName": last_name,
            "dateOfBirth": date_of_birth,
        }
        return self.http_client.post(
            endpoint=endpoint, response_model=BVNBooleanResponse, data=data
        )

    def verify_bank_account(self, account_number: str, bank_code: str) -> BankAccountResponse:
        """
        Verify bank account details.
        """
        endpoint = "/marketplace-routing/api/v1/verify/bank/account"
        data = {
            "accountNumber": account_number,
            "bankCode": bank_code,
        }
        return self.http_client.post(
            endpoint=endpoint, response_model=BankAccountResponse, data=data
        )

    def get_token_info(self) -> dict[str, Any]:
        """
        Get information about the current authentication token.

        Returns:
            Token information including expiry and permissions
        """
        return self.token_manager.get_token_info()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"InterswitchClient(base_url={self.config.base_url!r})"

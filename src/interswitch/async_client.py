from typing import Any, Literal

from interswitch.auth import AsyncTokenManager
from interswitch.config import Config
from interswitch.http_client import AsyncRequest
from interswitch.interswitch_types import APIResponse


class AsyncInterswitchClient:
    """
    Asynchronous client for Interswitch API operations.
    """

    def __init__(
        self,
        *,
        config: Config | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | None = None,
        token_url: str | None = None,
        token_expiry: int | None = None,
        request_timeout: int | None = None,
    ) -> None:
        self.config = config or Config(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            token_url=token_url,
            token_expiry=token_expiry,
            request_timeout=request_timeout,
        )

        self.token_manager = self._create_token_manager()
        self.http_client = self._create_http_client()

    def _create_token_manager(self) -> AsyncTokenManager:
        return AsyncTokenManager(self.config)

    def _create_http_client(self) -> AsyncRequest:
        return AsyncRequest(self.config, self.token_manager)

    # -------------------------------------------------------------------------
    # Identity Verification - Base APIs
    # -------------------------------------------------------------------------

    async def verify_nin(self, *, nin: str, first_name: str, last_name: str) -> APIResponse:
        endpoint = "/verify/identity/nin"
        data = {"firstName": first_name, "lastName": last_name, "nin": nin}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_nin_full(self, *, nin: str) -> APIResponse:
        endpoint = "/verify/identity/nin/verify"
        data = {"id": nin}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_bvn_full(self, *, bvn: str) -> APIResponse:
        endpoint = "/verify/identity/bvn/verify"
        data = {"id": bvn}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_bvn_boolean(self, *, bvn: str, first_name: str, last_name: str) -> APIResponse:
        endpoint = "/verify/identity/bvn"
        data = {"bvn": bvn, "firstName": first_name, "lastName": last_name}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_bank_account(self, *, account_number: str, bank_code: str) -> APIResponse:
        endpoint = "/verify/identity/account-number/resolve"
        data = {"accountNumber": account_number, "bankCode": bank_code}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_tin(self, *, tin: str) -> APIResponse:
        endpoint = "/verify/identity/tin"
        params = {"tin": tin}
        return await self.http_client.get(endpoint=endpoint, params=params)

    async def verify_drivers_license(self, *, license_id: str) -> APIResponse:
        endpoint = "/verify/identity/driver-license/verify"
        data = {"id": license_id}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def get_bank_list(self) -> APIResponse:
        endpoint = "/verify/identity/account-number/bank-list"
        return await self.http_client.get(endpoint=endpoint)

    async def verify_intl_passport(
        self, *, passport_number: str, last_name: str, date_of_birth: str
    ) -> APIResponse:
        endpoint = "/verify/identity/intl-passport-lookup"
        data = {
            "passport_number": passport_number,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
        }
        return await self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # AML, PEP & Biometrics
    # -------------------------------------------------------------------------

    async def verify_domestic_pep(self, *, full_name: str) -> APIResponse:
        endpoint = "/verify/identity/verification/domestic-pep"
        data = {"fullName": full_name}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_global_aml(
        self, *, query: str, entity_type: Literal["Business", "Person"]
    ) -> APIResponse:
        endpoint = "/verify/identity/verification/name/aml-checks"
        data = {"type": entity_type, "query": query}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def compare_faces(self, *, image1_url: str, image2_url: str) -> APIResponse:
        endpoint = "/verify/identity/face-comparison"
        data = {"image1": image1_url, "image2": image2_url}
        return await self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # Address Verification
    # -------------------------------------------------------------------------

    async def submit_physical_address(
        self,
        *,
        street: str,
        state_name: str,
        lga_name: str,
        landmark: str,
        city: str,
        applicant: dict[str, Any],
    ) -> APIResponse:
        endpoint = "/addresses"
        data = {
            "street": street,
            "stateName": state_name,
            "lgaName": lga_name,
            "landmark": landmark,
            "city": city,
            "applicant": applicant,
        }
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def get_physical_address(self, *, reference: str) -> APIResponse:
        endpoint = "/addresses"
        params = {"reference": reference}
        return await self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # SafeToken OTP
    # -------------------------------------------------------------------------

    async def generate_safetoken(self, *, token_id: str) -> APIResponse:
        endpoint = "/soft-token/generate"
        data = {"tokenId": token_id}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def send_safetoken(self, *, token_id: str, email: str, mobile_no: str) -> APIResponse:
        endpoint = "/soft-token/send"
        data = {"tokenId": token_id, "email": email, "mobileNo": mobile_no}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def verify_safetoken(self, *, token_id: str, otp: str) -> APIResponse:
        endpoint = "/soft-token/verify"
        data = {"tokenId": token_id, "otp": otp}
        return await self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # CAC Lookup
    # -------------------------------------------------------------------------

    async def lookup_cac(self, *, company_name: str) -> APIResponse:
        endpoint = "/verify/identity/cac-lookup"
        params = {"companyName": company_name}
        return await self.http_client.get(endpoint=endpoint, params=params)

    async def lookup_cac_directors(self, *, company_id: str) -> APIResponse:
        endpoint = "/verify/identity/cac-directors-lookup"
        params = {"companyId": company_id}
        return await self.http_client.get(endpoint=endpoint, params=params)

    async def lookup_cac_secretary(self, *, company_id: str) -> APIResponse:
        endpoint = "/verify/identity/cac-secretary-lookup"
        params = {"companyId": company_id}
        return await self.http_client.get(endpoint=endpoint, params=params)

    async def lookup_cac_shareholders(self, *, company_id: str) -> APIResponse:
        endpoint = "/verify/identity/cac-shareholders-lookup"
        params = {"companyId": company_id}
        return await self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # BVN Accounts Lookup & Credit History
    # -------------------------------------------------------------------------

    async def initiate_bvn_accounts_lookup(self, *, bvn: str) -> APIResponse:
        endpoint = "/verify/identity/initiate-bvn-accounts-lookup"
        data = {"bvn": bvn}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def request_bvn_accounts_otp(
        self, *, session_id: str, method: Literal["email", "sms"], phone_number: str = ""
    ) -> APIResponse:
        endpoint = "/verify/identity/bvn-accounts-lookup-request-otp"
        data = {"session_id": session_id, "method": method, "phone_number": phone_number}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def fetch_bvn_accounts_details(self, *, session_id: str, otp: str) -> APIResponse:
        endpoint = "/verify/identity/fetch-bvn-accounts-details"
        data = {"session_id": session_id, "otp": otp}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def lookup_credit_history(self, *, bvn: str) -> APIResponse:
        endpoint = "/verify/identity/credit-history-lookup"
        data = {"bvn": bvn}
        return await self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # BVN iGree
    # -------------------------------------------------------------------------

    async def initiate_bvn_igree(self, *, bvn: str) -> APIResponse:
        endpoint = "/verify/identity/initiate-bvn-igree"
        data = {"bvn": bvn}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def request_bvn_igree_otp(
        self, *, session_id: str, method: Literal["email", "sms"], phone_number: str = ""
    ) -> APIResponse:
        endpoint = "/verify/identity/bvn-igree-request-otp"
        data = {"session_id": session_id, "method": method, "phone_number": phone_number}
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def fetch_bvn_igree_details(self, *, session_id: str, otp: str) -> APIResponse:
        endpoint = "/verify/identity/fetch-bvn-igree-details"
        data = {"session_id": session_id, "otp": otp}
        return await self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # Value Added Services (VAS) / Bills Payment
    # -------------------------------------------------------------------------

    async def get_vas_billers(self) -> APIResponse:
        endpoint = "/vas/billers"
        return await self.http_client.get(endpoint=endpoint)

    async def get_vas_payment_item(self, *, biller_id: str) -> APIResponse:
        endpoint = "/vas/billers/payment-item"
        params = {"biller-id": biller_id}
        return await self.http_client.get(endpoint=endpoint, params=params)

    async def validate_vas_customer(self, *, customer_id: str, payment_code: str) -> APIResponse:
        endpoint = "/vas/validate-customer"
        data = [{"customerId": customer_id, "paymentCode": payment_code}]
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def pay_vas(
        self, *, customer_id: str, amount: float, reference: str, payment_code: str
    ) -> APIResponse:
        endpoint = "/vas/pay"
        data = {
            "customerId": customer_id,
            "amount": amount,
            "reference": reference,
            "paymentCode": payment_code,
        }
        return await self.http_client.post(endpoint=endpoint, data=data)

    async def get_vas_transactions(self, *, request_reference: str) -> APIResponse:
        endpoint = "/vas/transactions"
        params = {"request-reference": request_reference}
        return await self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def get_token_info(self) -> dict[str, Any]:
        return self.token_manager.get_token_info()

    async def aclose(self) -> None:
        """Close the underlying HTTPX async client."""
        await self.http_client.aclose()
        if hasattr(self.token_manager, "aclose"):
            await self.token_manager.aclose()  # type: ignore

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncInterswitchClient(base_url={self.config.base_url!r})"

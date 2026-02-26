from typing import Any, Literal

from interswitch.auth import TokenManager
from interswitch.config import Config
from interswitch.http_client import SyncRequest
from interswitch.interswitch_types import APIResponse


class InterswitchClient:
    """
    Main client for Interswitch API operations.
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

    def _create_token_manager(self) -> TokenManager:
        return TokenManager(self.config)

    def _create_http_client(self) -> SyncRequest:
        return SyncRequest(self.config, self.token_manager)

    # -------------------------------------------------------------------------
    # Identity Verification - Base APIs
    # -------------------------------------------------------------------------

    def verify_nin(self, *, nin: str, first_name: str, last_name: str) -> APIResponse:
        """Verify National Identification Number (NIN)."""
        endpoint = "/verify/identity/nin"
        data = {"firstName": first_name, "lastName": last_name, "nin": nin}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_nin_full(self, *, nin: str) -> APIResponse:
        """Verify National Identification Number (NIN) and get full details."""
        endpoint = "/verify/identity/nin/verify"
        data = {"id": nin}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_bvn_full(self, *, bvn: str) -> APIResponse:
        """Verify Bank Verification Number (BVN) and get full details."""
        endpoint = "/verify/identity/bvn/verify"
        data = {"id": bvn}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_bvn_boolean(self, *, bvn: str, first_name: str, last_name: str) -> APIResponse:
        """Verify BVN with boolean match (yes/no verification)."""
        endpoint = "/verify/identity/bvn"
        data = {"bvn": bvn, "firstName": first_name, "lastName": last_name}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_bank_account(self, *, account_number: str, bank_code: str) -> APIResponse:
        """Verify bank account details (resolve)."""
        endpoint = "/verify/identity/account-number/resolve"
        data = {"accountNumber": account_number, "bankCode": bank_code}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_tin(self, *, tin: str) -> APIResponse:
        """Verify Tax Identification Number (TIN)."""
        endpoint = "/verify/identity/tin"
        params = {"tin": tin}
        return self.http_client.get(endpoint=endpoint, params=params)

    def verify_drivers_license(self, *, license_id: str) -> APIResponse:
        """Verify driver's license."""
        endpoint = "/verify/identity/driver-license/verify"
        data = {"id": license_id}
        return self.http_client.post(endpoint=endpoint, data=data)

    def get_bank_list(self) -> APIResponse:
        """Get list of supported banks."""
        endpoint = "/verify/identity/account-number/bank-list"
        return self.http_client.get(endpoint=endpoint)

    def verify_intl_passport(
        self, *, passport_number: str, last_name: str, date_of_birth: str
    ) -> APIResponse:
        """Verify International Passport."""
        endpoint = "/verify/identity/intl-passport-lookup"
        data = {
            "passport_number": passport_number,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
        }
        return self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # AML, PEP & Biometrics
    # -------------------------------------------------------------------------

    def verify_domestic_pep(self, *, full_name: str) -> APIResponse:
        """Domestic Search AML Verification."""
        endpoint = "/verify/identity/verification/domestic-pep"
        data = {"fullName": full_name}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_global_aml(
        self, *, query: str, entity_type: Literal["Business", "Person"]
    ) -> APIResponse:
        """Global Search AML Verification."""
        endpoint = "/verify/identity/verification/name/aml-checks"
        data = {"type": entity_type, "query": query}
        return self.http_client.post(endpoint=endpoint, data=data)

    def compare_faces(self, *, image1_url: str, image2_url: str) -> APIResponse:
        """Perform facial comparison between two image URLs."""
        endpoint = "/verify/identity/face-comparison"
        data = {"image1": image1_url, "image2": image2_url}
        return self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # Address Verification
    # -------------------------------------------------------------------------

    def submit_physical_address(
        self,
        *,
        street: str,
        state_name: str,
        lga_name: str,
        landmark: str,
        city: str,
        applicant: dict[str, Any],
    ) -> APIResponse:
        """Submit physical address details for verification."""
        endpoint = "/addresses"
        data = {
            "street": street,
            "stateName": state_name,
            "lgaName": lga_name,
            "landmark": landmark,
            "city": city,
            "applicant": applicant,
        }
        return self.http_client.post(endpoint=endpoint, data=data)

    def get_physical_address(self, *, reference: str) -> APIResponse:
        """Fetch details of a submitted physical address verification."""
        endpoint = "/addresses"
        params = {"reference": reference}
        return self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # SafeToken OTP
    # -------------------------------------------------------------------------

    def generate_safetoken(self, *, token_id: str) -> APIResponse:
        """Generate a Safetoken OTP."""
        endpoint = "/soft-token/generate"
        data = {"tokenId": token_id}
        return self.http_client.post(endpoint=endpoint, data=data)

    def send_safetoken(self, *, token_id: str, email: str, mobile_no: str) -> APIResponse:
        """Generate and send a Safetoken OTP to user's email/mobile."""
        endpoint = "/soft-token/send"
        data = {"tokenId": token_id, "email": email, "mobileNo": mobile_no}
        return self.http_client.post(endpoint=endpoint, data=data)

    def verify_safetoken(self, *, token_id: str, otp: str) -> APIResponse:
        """Verify a Safetoken OTP."""
        endpoint = "/soft-token/verify"
        data = {"tokenId": token_id, "otp": otp}
        return self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # CAC Lookup
    # -------------------------------------------------------------------------

    def lookup_cac(self, *, company_name: str) -> APIResponse:
        """Perform CAC general lookup by company name."""
        endpoint = "/verify/identity/cac-lookup"
        params = {"companyName": company_name}
        return self.http_client.get(endpoint=endpoint, params=params)

    def lookup_cac_directors(self, *, company_id: str) -> APIResponse:
        """Perform CAC lookup for company directors."""
        endpoint = "/verify/identity/cac-directors-lookup"
        params = {"companyId": company_id}
        return self.http_client.get(endpoint=endpoint, params=params)

    def lookup_cac_secretary(self, *, company_id: str) -> APIResponse:
        """Perform CAC lookup for company secretary."""
        endpoint = "/verify/identity/cac-secretary-lookup"
        params = {"companyId": company_id}
        return self.http_client.get(endpoint=endpoint, params=params)

    def lookup_cac_shareholders(self, *, company_id: str) -> APIResponse:
        """Perform CAC lookup for company shareholders."""
        endpoint = "/verify/identity/cac-shareholders-lookup"
        params = {"companyId": company_id}
        return self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # BVN Accounts Lookup & Credit History
    # -------------------------------------------------------------------------

    def initiate_bvn_accounts_lookup(self, *, bvn: str) -> APIResponse:
        """Step 1: Initiate BVN linked accounts lookup."""
        endpoint = "/verify/identity/initiate-bvn-accounts-lookup"
        data = {"bvn": bvn}
        return self.http_client.post(endpoint=endpoint, data=data)

    def request_bvn_accounts_otp(
        self, *, session_id: str, method: Literal["email", "sms"], phone_number: str = ""
    ) -> APIResponse:
        """Step 2: Request OTP for BVN linked accounts lookup."""
        endpoint = "/verify/identity/bvn-accounts-lookup-request-otp"
        data = {"session_id": session_id, "method": method, "phone_number": phone_number}
        return self.http_client.post(endpoint=endpoint, data=data)

    def fetch_bvn_accounts_details(self, *, session_id: str, otp: str) -> APIResponse:
        """Step 3: Fetch BVN linked accounts details using OTP."""
        endpoint = "/verify/identity/fetch-bvn-accounts-details"
        data = {"session_id": session_id, "otp": otp}
        return self.http_client.post(endpoint=endpoint, data=data)

    def lookup_credit_history(self, *, bvn: str) -> APIResponse:
        """Check credit history associated with a BVN."""
        endpoint = "/verify/identity/credit-history-lookup"
        data = {"bvn": bvn}
        return self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # BVN iGree
    # -------------------------------------------------------------------------

    def initiate_bvn_igree(self, *, bvn: str) -> APIResponse:
        """Step 1: Initiate BVN iGree consent process."""
        endpoint = "/verify/identity/initiate-bvn-igree"
        data = {"bvn": bvn}
        return self.http_client.post(endpoint=endpoint, data=data)

    def request_bvn_igree_otp(
        self, *, session_id: str, method: str, phone_number: str = ""
    ) -> APIResponse:
        """Step 2: Request OTP for BVN iGree."""
        endpoint = "/verify/identity/bvn-igree-request-otp"
        data = {"session_id": session_id, "method": method, "phone_number": phone_number}
        return self.http_client.post(endpoint=endpoint, data=data)

    def fetch_bvn_igree_details(self, *, session_id: str, otp: str) -> APIResponse:
        """Step 3: Fetch BVN iGree details using OTP."""
        endpoint = "/verify/identity/fetch-bvn-igree-details"
        data = {"session_id": session_id, "otp": otp}
        return self.http_client.post(endpoint=endpoint, data=data)

    # -------------------------------------------------------------------------
    # Value Added Services (VAS) / Bills Payment
    # -------------------------------------------------------------------------

    def get_vas_billers(self) -> APIResponse:
        """Get list of available VAS billers."""
        endpoint = "/vas/billers"
        return self.http_client.get(endpoint=endpoint)

    def get_vas_payment_item(self, *, biller_id: str) -> APIResponse:
        """Get payment items for a specific biller."""
        endpoint = "/vas/billers/payment-item"
        params = {"biller-id": biller_id}
        return self.http_client.get(endpoint=endpoint, params=params)

    def validate_vas_customer(self, *, customer_id: str, payment_code: str) -> APIResponse:
        """Validate a customer against a payment code for VAS."""
        endpoint = "/vas/validate-customer"
        data = [{"customerId": customer_id, "paymentCode": payment_code}]
        return self.http_client.post(endpoint=endpoint, data=data)

    def pay_vas(
        self, *, customer_id: str, amount: float, reference: str, payment_code: str
    ) -> APIResponse:
        """Process a VAS bill payment."""
        endpoint = "/vas/pay"
        data = {
            "customerId": customer_id,
            "amount": amount,
            "reference": reference,
            "paymentCode": payment_code,
        }
        return self.http_client.post(endpoint=endpoint, data=data)

    def get_vas_transactions(self, *, request_reference: str) -> APIResponse:
        """Query the status of a VAS transaction."""
        endpoint = "/vas/transactions"
        params = {"request-reference": request_reference}
        return self.http_client.get(endpoint=endpoint, params=params)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def get_token_info(self) -> dict[str, Any]:
        """
        Get information about the current authentication token.
        """
        return self.token_manager.get_token_info()

    def close(self) -> None:
        """
        Clean up resources
        """
        self.http_client.session.close()
        if hasattr(self.token_manager, "close"):
            self.token_manager.close()  # type: ignore

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"InterswitchClient(base_url={self.config.base_url!r})"

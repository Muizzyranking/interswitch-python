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
        return self.http_client.post(
            endpoint="/verify/identity/nin",
            data={"firstName": first_name, "lastName": last_name, "nin": nin},
            required_actions="VerifyMeNin",
        )

    def verify_nin_full(self, *, nin: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/nin/verify",
            data={"id": nin},
            required_actions="UVNin",
        )

    def verify_bvn_boolean(self, *, bvn: str, first_name: str, last_name: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/bvn",
            data={"bvn": bvn, "firstName": first_name, "lastName": last_name},
            required_actions="VerifyMeBvn",
        )

    def verify_bvn_full(self, *, bvn: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/bvn/verify",
            data={"id": bvn},
            required_actions="UVBvn",
        )

    def verify_bank_account(self, *, account_number: str, bank_code: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/account-number/resolve",
            data={"accountNumber": account_number, "bankCode": bank_code},
            required_actions="UVBankVerification",
        )

    def verify_tin(self, *, tin: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/verify/identity/tin",
            params={"tin": tin},
            required_actions="VerifyMeTin",
        )

    def verify_drivers_license(self, *, license_id: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/driver-license/verify",
            data={"id": license_id},
            required_actions=["UVDriverLicense", "MonoDriverLicense"],
        )

    def get_bank_list(self) -> APIResponse:
        # No scope restriction — public lookup endpoint
        return self.http_client.get(
            endpoint="/verify/identity/account-number/bank-list",
        )

    def verify_intl_passport(
        self, *, passport_number: str, last_name: str, date_of_birth: str
    ) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/intl-passport-lookup",
            data={
                "passport_number": passport_number,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
            },
            required_actions="MonoIntlPassport",
        )

    # -------------------------------------------------------------------------
    # AML, PEP & Biometrics
    # -------------------------------------------------------------------------

    def verify_domestic_pep(self, *, full_name: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/verification/domestic-pep",
            data={"fullName": full_name},
            required_actions="UVAmlDomestic",
        )

    def verify_global_aml(
        self, *, query: str, entity_type: Literal["Business", "Person"] = "Business"
    ) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/verification/name/aml-checks",
            data={"type": entity_type, "query": query},
            required_actions="UVAmlGlobal",
        )

    def compare_faces(self, *, image1_url: str, image2_url: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/face-comparison",
            data={"image1": image1_url, "image2": image2_url},
            required_actions="UVFaceComparison",
        )

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
        return self.http_client.post(
            endpoint="/addresses",
            data={
                "street": street,
                "stateName": state_name,
                "lgaName": lga_name,
                "landmark": landmark,
                "city": city,
                "applicant": applicant,
            },
            required_actions="VerifyMeAddress",
        )

    def get_physical_address(self, *, reference: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/addresses",
            params={"reference": reference},
            required_actions="VerifyMeAddress",
        )

    # -------------------------------------------------------------------------
    # SafeToken OTP
    # -------------------------------------------------------------------------

    def generate_safetoken(self, *, token_id: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/soft-token/generate",
            data={"tokenId": token_id},
            required_actions="VerveSoftTokenGen",
        )

    def send_safetoken(self, *, token_id: str, email: str, mobile_no: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/soft-token/send",
            data={"tokenId": token_id, "email": email, "mobileNo": mobile_no},
            required_actions=["VerveSoftTokenGen", "VerveSoftTokenGenSms"],
        )

    def verify_safetoken(self, *, token_id: str, otp: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/soft-token/verify",
            data={"tokenId": token_id, "otp": otp},
            required_actions="VerveSoftTokenGen",
        )

    # -------------------------------------------------------------------------
    # CAC Lookup
    # -------------------------------------------------------------------------

    def lookup_cac(self, *, company_name: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/verify/identity/cac-lookup",
            params={"companyName": company_name},
            required_actions="MonoCac",
        )

    def lookup_cac_directors(self, *, company_id: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/verify/identity/cac-directors-lookup",
            params={"companyId": company_id},
            required_actions="MonoCac",
        )

    def lookup_cac_secretary(self, *, company_id: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/verify/identity/cac-secretary-lookup",
            params={"companyId": company_id},
            required_actions="MonoCac",
        )

    def lookup_cac_shareholders(self, *, company_id: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/verify/identity/cac-shareholders-lookup",
            params={"companyId": company_id},
            required_actions="MonoCac",
        )

    # -------------------------------------------------------------------------
    # BVN Accounts Lookup & Credit History
    # -------------------------------------------------------------------------

    def initiate_bvn_accounts_lookup(self, *, bvn: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/initiate-bvn-accounts-lookup",
            data={"bvn": bvn},
            required_actions="MonoBvnAccounts",
        )

    def request_bvn_accounts_otp(
        self, *, session_id: str, method: Literal["email", "sms"], phone_number: str = ""
    ) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/bvn-accounts-lookup-request-otp",
            data={"session_id": session_id, "method": method, "phone_number": phone_number},
            required_actions="MonoBvnAccounts",
        )

    def fetch_bvn_accounts_details(self, *, session_id: str, otp: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/fetch-bvn-accounts-details",
            data={"session_id": session_id, "otp": otp},
            required_actions="MonoBvnAccounts",
        )

    def lookup_credit_history(self, *, bvn: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/credit-history-lookup",
            data={"bvn": bvn},
            required_actions="MonoCreditHistory",
        )

    # -------------------------------------------------------------------------
    # BVN iGree
    # -------------------------------------------------------------------------

    def initiate_bvn_igree(self, *, bvn: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/initiate-bvn-igree",
            data={"bvn": bvn},
            required_actions="MonoBvnIGree",
        )

    def request_bvn_igree_otp(
        self, *, session_id: str, method: Literal["email", "sms"], phone_number: str = ""
    ) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/bvn-igree-request-otp",
            data={"session_id": session_id, "method": method, "phone_number": phone_number},
            required_actions="MonoBvnIGree",
        )

    def fetch_bvn_igree_details(self, *, session_id: str, otp: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/verify/identity/fetch-bvn-igree-details",
            data={"session_id": session_id, "otp": otp},
            required_actions="MonoBvnIGree",
        )

    # -------------------------------------------------------------------------
    # VAS / Bills Payment
    # -------------------------------------------------------------------------

    def get_vas_billers(self) -> APIResponse:
        return self.http_client.get(
            endpoint="/vas/billers",
            required_actions="VasBills",
        )

    def get_vas_payment_item(self, *, biller_id: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/vas/billers/payment-item",
            params={"biller-id": biller_id},
            required_actions="VasBills",
        )

    def validate_vas_customer(self, *, customer_id: str, payment_code: str) -> APIResponse:
        return self.http_client.post(
            endpoint="/vas/validate-customer",
            data=[{"customerId": customer_id, "paymentCode": payment_code}],
            required_actions="VasBills",
        )

    def pay_vas(
        self, *, customer_id: str, amount: float, reference: str, payment_code: str
    ) -> APIResponse:
        return self.http_client.post(
            endpoint="/vas/pay",
            data={
                "customerId": customer_id,
                "amount": amount,
                "reference": reference,
                "paymentCode": payment_code,
            },
            required_actions="VasBills",
        )

    def get_vas_transactions(self, *, request_reference: str) -> APIResponse:
        return self.http_client.get(
            endpoint="/vas/transactions",
            params={"request-reference": request_reference},
            required_actions="VasBills",
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def get_token_info(self) -> dict[str, Any]:
        return self.token_manager.get_token_info()

    def close(self) -> None:
        self.http_client.session.close()
        if hasattr(self.token_manager, "close"):
            self.token_manager.close()  # type: ignore

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        return f"InterswitchClient(base_url={self.config.base_url!r})"

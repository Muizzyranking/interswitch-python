"""
Type definitions for Interswitch SDK using Pydantic.

These models provide type hints, validation, and attribute access
for better IDE support and developer experience.
"""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """OAuth token response from authentication server."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    marketplace_user: str
    client_name: str
    client_logo: str | None = None
    client_description: str
    jti: str

    model_config = {"extra": "allow"}


class TokenInfo(BaseModel):
    """Token information for status checking."""

    is_valid: bool
    expires_at: str | None
    client_name: str | None
    marketplace_user: str | None
    scope: list[str] | None
    api_actions: list[str]


class APIResponse(BaseModel):
    """Base API response structure."""

    success: bool
    code: str
    message: str

    model_config = {"extra": "allow"}


class NINAddress(BaseModel):
    """Address information from NIN verification."""

    town: str
    lga: str
    state: str
    addressLine: str = Field(..., alias="addressLine")


class NINData(BaseModel):
    """NIN verification data."""

    id: str
    status: str
    firstName: str
    middleName: str | None = None
    lastName: str
    mobile: str
    dateOfBirth: str
    gender: str
    address: NINAddress
    image: str
    signature: str

    model_config = {"populate_by_name": True}


class NINResponse(APIResponse):
    """Complete NIN verification response."""

    data: NINData


class BVNData(BaseModel):
    """BVN verification data."""

    id: str
    status: str
    firstName: str
    lastName: str
    middleName: str | None = None
    mobile: str
    dateOfBirth: str
    gender: str
    image: str
    nin: str | None = None

    model_config = {"populate_by_name": True}


class BVNResponse(APIResponse):
    """Complete BVN verification response."""

    data: BVNData


class BVNBooleanData(BaseModel):
    """BVN boolean match data."""

    id: str
    status: str
    match: bool


class BVNBooleanResponse(APIResponse):
    """BVN boolean match response."""

    data: BVNBooleanData


class TINData(BaseModel):
    """TIN verification data."""

    id: str
    status: str
    tin: str
    taxpayerName: str
    cac: str | None = None
    email: str | None = None
    phone: str | None = None

    model_config = {"populate_by_name": True}


class TINResponse(APIResponse):
    """Complete TIN verification response."""

    data: TINData


class DriversLicenseData(BaseModel):
    """Driver's license verification data."""

    id: str
    status: str
    firstName: str
    lastName: str
    middleName: str | None = None
    dateOfBirth: str
    gender: str
    issuedDate: str
    expiryDate: str
    stateOfIssue: str
    photo: str

    model_config = {"populate_by_name": True}


class DriversLicenseResponse(APIResponse):
    """Complete driver's license verification response."""

    data: DriversLicenseData


class DriversLicenseBooleanData(BaseModel):
    """Driver's license boolean verification data."""

    id: str
    status: str
    match: bool


class DriversLicenseBooleanResponse(APIResponse):
    """Driver's license boolean verification response."""

    data: DriversLicenseBooleanData


class BankAccountData(BaseModel):
    """Bank account verification data."""

    accountNumber: str
    accountName: str
    bankCode: str
    bankName: str
    bvn: str | None = None

    model_config = {"populate_by_name": True}


class BankAccountResponse(APIResponse):
    """Bank account verification response."""

    data: BankAccountData


class BankAccount(BaseModel):
    """Individual bank account information."""

    accountNumber: str
    accountName: str
    bankCode: str
    bankName: str

    model_config = {"populate_by_name": True}


class BankAccountsLookupData(BaseModel):
    """Bank accounts lookup data."""

    bvn: str
    accounts: list[BankAccount]


class BankAccountsLookupResponse(APIResponse):
    """Bank accounts lookup response."""

    data: BankAccountsLookupData


class AMLMatch(BaseModel):
    """Single AML match result."""

    name: str
    matchScore: float
    category: str
    listName: str
    details: dict[str, str] | None = None

    model_config = {"populate_by_name": True}


class AMLData(BaseModel):
    """AML screening data."""

    searchName: str
    matches: list[AMLMatch]
    screeningDate: str
    status: str  # "clear" or "matches_found"

    model_config = {"populate_by_name": True}


class AMLResponse(APIResponse):
    """AML screening response."""

    data: AMLData


class CreditHistoryLoan(BaseModel):
    """Individual loan record."""

    loanAmount: float
    loanStatus: str
    monthlyPayment: float
    outstandingBalance: float
    dateOpened: str
    lender: str

    model_config = {"populate_by_name": True}


class CreditHistoryData(BaseModel):
    """Credit history data."""

    bvn: str
    creditScore: int
    totalLoans: int
    activeLoans: int
    totalDebt: float
    loans: list[CreditHistoryLoan]

    model_config = {"populate_by_name": True}


class CreditHistoryResponse(APIResponse):
    """Credit history response."""

    data: CreditHistoryData


class CACDirector(BaseModel):
    """Company director information."""

    name: str
    gender: str | None = None
    nationality: str | None = None
    dateOfBirth: str | None = None

    model_config = {"populate_by_name": True}


class CACShareholder(BaseModel):
    """Company shareholder information."""

    name: str
    shares: int
    sharePercentage: float

    model_config = {"populate_by_name": True}


class CACData(BaseModel):
    """CAC lookup data."""

    rcNumber: str
    companyName: str
    registrationDate: str
    companyType: str
    status: str
    address: str
    email: str | None = None
    phone: str | None = None
    directors: list[CACDirector]
    shareholders: list[CACShareholder]

    model_config = {"populate_by_name": True}


class CACResponse(APIResponse):
    """CAC lookup response."""

    data: CACData


class AddressData(BaseModel):
    """Physical address verification data."""

    addressLine: str
    city: str
    state: str
    lga: str
    postalCode: str | None = None
    verified: bool
    verificationSource: str

    model_config = {"populate_by_name": True}


class AddressResponse(APIResponse):
    """Physical address verification response."""

    data: AddressData


class PassportData(BaseModel):
    """International passport verification data."""

    passportNumber: str
    surname: str
    givenNames: str
    dateOfBirth: str
    gender: str
    nationality: str
    issuedDate: str
    expiryDate: str
    photo: str

    model_config = {"populate_by_name": True}


class PassportResponse(APIResponse):
    """International passport verification response."""

    data: PassportData


class SafetokenData(BaseModel):
    """Safetoken OTP data."""

    transactionId: str
    otp: str | None = None  # Only present in generate (not send)
    expiresIn: int
    status: str

    model_config = {"populate_by_name": True}


class SafetokenResponse(APIResponse):
    """Safetoken response."""

    data: SafetokenData


class SafetokenVerifyData(BaseModel):
    """Safetoken verification result."""

    transactionId: str
    valid: bool
    message: str

    model_config = {"populate_by_name": True}


class SafetokenVerifyResponse(APIResponse):
    """Safetoken verification response."""

    data: SafetokenVerifyData


class FacialComparisonData(BaseModel):
    """Facial comparison result data."""

    matchScore: float
    isMatch: bool
    confidence: float

    model_config = {"populate_by_name": True}


class FacialComparisonResponse(APIResponse):
    """Facial comparison response."""

    data: FacialComparisonData


class TransactionData(BaseModel):
    """Transaction search data."""

    transactionReference: str
    amount: float
    currency: str
    status: str
    paymentMethod: str
    customerEmail: str | None = None
    customerPhone: str | None = None
    transactionDate: str

    model_config = {"populate_by_name": True}


class TransactionResponse(APIResponse):
    """Transaction search response."""

    data: TransactionData

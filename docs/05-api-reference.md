# API Reference

All methods are available on both `InterswitchClient` (sync) and `AsyncInterswitchClient` (async — prefix calls with `await`).

Every method returns `APIResponse` on success or raises an exception. See [Error Handling](02-error-handling.md).

`required_actions` is what the SDK checks against your token's `api_actions` before making the request. If the action is missing, `InsufficientActionsError` is raised immediately.

---

## Identity Verification

### verify_nin

Verify an NIN with a boolean name match.

```python
response = client.verify_nin(
    nin="12345678901",
    first_name="Muiz",
    last_name="Yusuf",
)
```

| Parameter | Type | Required |
|---|---|---|
| `nin` | `str` | Yes |
| `first_name` | `str` | Yes |
| `last_name` | `str` | Yes |

Required API action(s): `VerifyMeNin`

---

### verify_nin_full

Verify a 16-digit virtual NIN and retrieve the full record.

```python
response = client.verify_nin_full(nin="1234567890123456")
```

| Parameter | Type | Required |
|---|---|---|
| `nin` | `str` | Yes — 16-digit virtual NIN |

Required API action(s): `UVNin`

---

### verify_bvn_boolean

Verify a BVN with a boolean name match.

```python
response = client.verify_bvn_boolean(
    bvn="12345678901",
    first_name="Muiz",
    last_name="Yusuf",
)
```

| Parameter | Type | Required |
|---|---|---|
| `bvn` | `str` | Yes |
| `first_name` | `str` | Yes |
| `last_name` | `str` | Yes |

Required API action(s): `VerifyMeBvn`

---

### verify_bvn_full

Verify a BVN and retrieve the full record.

```python
response = client.verify_bvn_full(bvn="12345678901")
```

| Parameter | Type | Required |
|---|---|---|
| `bvn` | `str` | Yes |

Required API action(s): `UVBvn`

---

### verify_bank_account

Resolve and verify a bank account number.

```python
response = client.verify_bank_account(
    account_number="1000000000",
    bank_code="058",
)
```

| Parameter | Type | Required |
|---|---|---|
| `account_number` | `str` | Yes |
| `bank_code` | `str` | Yes |

Required API action(s): `UVBankVerification`

---

### verify_tin

Verify a Tax Identification Number.

```python
response = client.verify_tin(tin="08120451-1001")
```

| Parameter | Type | Required |
|---|---|---|
| `tin` | `str` | Yes |

Required API action(s): `VerifyMeTin`

---

### verify_drivers_license

Verify a driver's license.

```python
response = client.verify_drivers_license(license_id="AAA00000AA00")
```

| Parameter | Type | Required |
|---|---|---|
| `license_id` | `str` | Yes |

Required API action(s): `UVDriverLicense` **or** `MonoDriverLicense` — either is sufficient.

---

### verify_intl_passport

Verify an international passport.

```python
response = client.verify_intl_passport(
    passport_number="B00000000",
    last_name="Yusuf",
    date_of_birth="01/01/1990",
)
```

| Parameter | Type | Required |
|---|---|---|
| `passport_number` | `str` | Yes |
| `last_name` | `str` | Yes |
| `date_of_birth` | `str` | Yes — format: `DD/MM/YYYY` |

Required API action(s): `MonoIntlPassport`

---

### get_bank_list

Retrieve the list of supported banks.

```python
response = client.get_bank_list()
```

No action restriction.

---

## AML, PEP & Biometrics

### verify_domestic_pep

Domestic AML / PEP check against the Nigerian sanctions list.

```python
response = client.verify_domestic_pep(full_name="John Michael Doe")
```

| Parameter | Type | Required |
|---|---|---|
| `full_name` | `str` | Yes |

Required API action(s): `UVAmlDomestic`

---

### verify_global_aml

Global AML check.

```python
response = client.verify_global_aml(query="Acme Nigeria Ltd")
response = client.verify_global_aml(query="John Doe", entity_type="Person")
```

| Parameter | Type | Required | Default |
|---|---|---|---|
| `query` | `str` | Yes | — |
| `entity_type` | `"Business"` \| `"Person"` | No | `"Business"` |

Required API action(s): `UVAmlGlobal`

---

### compare_faces

Compare two face images.

```python
response = client.compare_faces(
    image1_url="https://example.com/photo1.jpg",
    image2_url="https://example.com/photo2.jpg",
)
```

| Parameter | Type | Required |
|---|---|---|
| `image1_url` | `str` | Yes |
| `image2_url` | `str` | Yes |

Required API action(s): `UVFaceComparison`

---

## Address Verification

### submit_physical_address

Submit a physical address for verification.

```python
response = client.submit_physical_address(
    street="13 Test Street",
    state_name="Lagos",
    lga_name="Mushin",
    landmark="Near Mushin Market",
    city="Lagos",
    applicant={
        "firstname": "Muiz",
        "lastname": "Yusuf",
        "phone": "+2349012345678",
        "dob": "1990-01-01",
        "gender": "male",
    },
)
```

| Parameter | Type | Required |
|---|---|---|
| `street` | `str` | Yes |
| `state_name` | `str` | Yes |
| `lga_name` | `str` | Yes |
| `landmark` | `str` | Yes |
| `city` | `str` | Yes |
| `applicant` | `dict` | Yes — `firstname`, `lastname`, `phone`, `dob`, `gender` |

Required API action(s): `VerifyMeAddress`

---

### get_physical_address

Retrieve the status of a submitted address verification.

```python
response = client.get_physical_address(reference="ref-001")
```

| Parameter | Type | Required |
|---|---|---|
| `reference` | `str` | Yes — the `customerReference` from `submit_physical_address` |

Required API action(s): `VerifyMeAddress`

---

## SafeToken OTP

### generate_safetoken

Generate a SafeToken OTP.

```python
response = client.generate_safetoken(token_id="user-identifier")
# response.data["otp"] — the generated OTP
# response.data["expiry"] — expiry string
```

| Parameter | Type | Required |
|---|---|---|
| `token_id` | `str` | Yes — your internal user identifier |

Required API action(s): `VerveSoftTokenGen`

---

### send_safetoken

Generate and send a SafeToken OTP to a user's email or phone.

```python
response = client.send_safetoken(
    token_id="user-identifier",
    email="user@example.com",
    mobile_no="08012345678",
)
```

| Parameter | Type | Required |
|---|---|---|
| `token_id` | `str` | Yes |
| `email` | `str` | Yes |
| `mobile_no` | `str` | Yes |

Required API action(s): `VerveSoftTokenGen` **or** `VerveSoftTokenGenSms`

---

### verify_safetoken

Verify a SafeToken OTP entered by the user.

```python
response = client.verify_safetoken(token_id="user-identifier", otp="123456")
# response.data["transactionStatus"] — "Y" if valid
```

| Parameter | Type | Required |
|---|---|---|
| `token_id` | `str` | Yes |
| `otp` | `str` | Yes |

Required API action(s): `VerveSoftTokenGen`

---

## CAC Lookup

### lookup_cac

Search for a company by name.

```python
response = client.lookup_cac(company_name="Acme")
# response.data — list of matching companies with id, approved_name, rc_number
```

| Parameter | Type | Required |
|---|---|---|
| `company_name` | `str` | Yes |

Required API action(s): `MonoCac`

---

### lookup_cac_directors

Retrieve directors for a company.

```python
response = client.lookup_cac_directors(company_id="3369190")
```

| Parameter | Type | Required |
|---|---|---|
| `company_id` | `str` | Yes — `id` from `lookup_cac` |

Required API action(s): `MonoCac`

---

### lookup_cac_secretary

Retrieve company secretary details.

```python
response = client.lookup_cac_secretary(company_id="3369190")
```

| Parameter | Type | Required |
|---|---|---|
| `company_id` | `str` | Yes |

Required API action(s): `MonoCac`

---

### lookup_cac_shareholders

Retrieve company shareholders.

```python
response = client.lookup_cac_shareholders(company_id="3369190")
```

| Parameter | Type | Required |
|---|---|---|
| `company_id` | `str` | Yes |

Required API action(s): `MonoCac`

---

## BVN Linked Accounts Lookup

Three-step flow: initiate → request OTP → fetch details.

### initiate_bvn_accounts_lookup

```python
response = client.initiate_bvn_accounts_lookup(bvn="12345678901")
# response.data["session_id"] — use in subsequent steps
# response.data["methods"] — available OTP delivery methods
```

Required API action(s): `MonoBvnAccounts`

---

### request_bvn_accounts_otp

```python
response = client.request_bvn_accounts_otp(
    session_id="session-id-from-initiate",
    method="email",          # or "sms"
    phone_number="",         # required when method="sms"
)
```

| Parameter | Type | Required | Default |
|---|---|---|---|
| `session_id` | `str` | Yes | — |
| `method` | `"email"` \| `"sms"` | Yes | — |
| `phone_number` | `str` | No | `""` |

Required API action(s): `MonoBvnAccounts`

---

### fetch_bvn_accounts_details

```python
response = client.fetch_bvn_accounts_details(
    session_id="session-id-from-initiate",
    otp="123456",
)
# response.data — list of linked bank accounts
```

Required API action(s): `MonoBvnAccounts`

---

### lookup_credit_history

Check credit history linked to a BVN.

```python
response = client.lookup_credit_history(bvn="12345678901")
```

Required API action(s): `MonoCreditHistory`

---

## BVN iGree

Three-step consent flow: initiate → request OTP → fetch details.

### initiate_bvn_igree

```python
response = client.initiate_bvn_igree(bvn="12345678901")
# response.data["session_id"]
```

Required API action(s): `MonoBvnIGree`

---

### request_bvn_igree_otp

```python
response = client.request_bvn_igree_otp(
    session_id="session-id",
    method="sms",
    phone_number="08012345678",
)
```

Required API action(s): `MonoBvnIGree`

---

### fetch_bvn_igree_details

```python
response = client.fetch_bvn_igree_details(
    session_id="session-id",
    otp="654321",
)
```

Required API action(s): `MonoBvnIGree`

---

## VAS / Bills Payment

### get_vas_billers

```python
response = client.get_vas_billers()
# response.data — list of biller categories
```

Required API action(s): `VasBills`

---

### get_vas_payment_item

```python
response = client.get_vas_payment_item(biller_id="520")
# response.data — list of payment items for the biller
```

Required API action(s): `VasBills`

---

### validate_vas_customer

```python
response = client.validate_vas_customer(
    customer_id="07065544567",
    payment_code="10902",
)
```

Required API action(s): `VasBills`

---

### pay_vas

```python
response = client.pay_vas(
    customer_id="07065544567",
    amount=20000,
    reference="your-unique-reference",
    payment_code="10902",
)
```

| Parameter | Type | Required |
|---|---|---|
| `customer_id` | `str` | Yes |
| `amount` | `float` | Yes — in kobo |
| `reference` | `str` | Yes — must be unique per transaction |
| `payment_code` | `str` | Yes |

Required API action(s): `VasBills`

---

### get_vas_transactions

```python
response = client.get_vas_transactions(request_reference="your-unique-reference")
```

Required API action(s): `VasBills`

---

## APIResponse

All methods return `APIResponse` on success:

```python
response.success      # bool — always True
response.code         # str — e.g. "200"
response.status_code  # str — e.g. "200"
response.message      # str — e.g. "request processed successfully"
response.data         # dict | list | None — the actual result
```

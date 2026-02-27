import os

from interswitch import InterswitchClient
from interswitch.exceptions import InterswitchError


def main():
    """Run demo examples."""

    # client_id = os.getenv("INTERSWITCH_CLIENT_ID")
    client_id = "IKIAFBF542E9A917B5C6EA8A8C36E209F3C76D5A2213"
    # client_secret = os.getenv("INTERSWITCH_CLIENT_SECRET")
    client_secret = "E02887530483717F017BBA4B3AE5E37CDDC6C475"

    if not client_id or not client_secret:
        print("❌ Error: Please set INTERSWITCH_CLIENT_ID and INTERSWITCH_CLIENT_SECRET")
        print("   export INTERSWITCH_CLIENT_ID='your_id'")
        print("   export INTERSWITCH_CLIENT_SECRET='your_secret'")
        return

    print("🔧 Initializing Interswitch client...")
    client = InterswitchClient(
        client_id=client_id,
        client_secret=client_secret,
    )

    # Check token info
    print("\n📋 Token Information:")
    token_info = client.get_token_info()
    print(f"   Token valid: {token_info['is_valid']}")
    # print(f"   Expires at: {token_info['expires_at']}")
    # print(f"   Marketplace user: {token_info['marketplace_user']}")

    # Demo 1: NIN Verification

    print("\n" + "=" * 60)
    print("Demo 1: NIN Verification")
    print("=" * 60)

    nin = input("Enter NIN to verify (or press Enter to skip): ").strip()
    first_name = input("Enter First name to verify (or press Enter to skip): ").strip()
    last_name = input("Enter Last name to verify (or press Enter to skip): ").strip()
    if nin:
        try:
            print(f"🔍 Verifying NIN: {nin}")
            response = client.verify_nin(nin=nin, first_name=first_name, last_name=last_name)

            print("✅ NIN Verification Successful!")
            print(response)
            # print(f"   Name: {response.data.firstName} {response.data.lastName}")
            # print(f"   Date of Birth: {response.data.dateOfBirth}")
            # print(f"   Gender: {response.data.gender}")
            # print(f"   State: {response.data.address.state}")
            # print(f"   LGA: {response.data.address.lga}")
        except InterswitchError as e:
            print(f"❌ Error: {e}")

    print("\n📋 Token Information:")
    token_info = client.get_token_info()
    print(token_info)
    print(f"   Token valid: {token_info['is_valid']}")

    #
    # Demo 2: BVN Verification (Full)
    print("\n" + "=" * 60)
    print("Demo 2: BVN Full Details Verification")
    print("=" * 60)

    bvn = input("Enter BVN to verify (or press Enter to skip): ").strip()
    if bvn:
        try:
            print(f"🔍 Verifying BVN: {bvn}")
            response = client.verify_bvn_full(bvn=bvn)

            print("✅ BVN Verification Successful!")
            print(response.data)
            print(f"   Name: {response.data['firstName']} {response.data['lastName']}")
        except InterswitchError as e:
            print(f"❌ Error: {e}")

    # Demo 3: BVN Boolean Match
    print("\n" + "=" * 60)
    print("Demo 3: BVN Boolean Match")
    print("=" * 60)

    bvn = input("Enter BVN (or press Enter to skip): ").strip()
    if bvn:
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        try:
            print("🔍 Checking BVN match...")
            response = client.verify_bvn_boolean(
                bvn=bvn,
                first_name=first_name,
                last_name=last_name,
            )
            print(response)
        except InterswitchError as e:
            print(f"❌ Error: {e}")

    # Demo 4: Bank Account Verification
    print("\n" + "=" * 60)
    print("Demo 4: Bank Account Verification")
    print("=" * 60)

    account = input("Enter account number (or press Enter to skip): ").strip()
    if account:
        bank_code = input("Enter bank code (e.g., 058 for GTBank): ").strip()

        try:
            print("🔍 Verifying account...")
            response = client.verify_bank_account(
                account_number=account,
                bank_code=bank_code,
            )

            print("✅ Account Verification Successful!")
            print(response)
            # print(f"   Account Name: {response.data.accountName}")
            # print(f"   Account Number: {response.data.accountNumber}")
            # print(f"   Bank: {response.data.bankName}")
        except InterswitchError as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


#
if __name__ == "__main__":
    main()

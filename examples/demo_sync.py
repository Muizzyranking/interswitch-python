import json
import logging
import os

from interswitch import InterswitchClient
from interswitch.exceptions import AuthenticationError, InterswitchError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def print_response(data: dict | None) -> None:
    """Helper to pretty-print dictionary responses."""
    if data:
        print(json.dumps(data, indent=2))
    else:
        print("No data returned.")


def main() -> None:
    """Run synchronous demo examples."""

    client_id = os.getenv("INTERSWITCH_CLIENT_ID", "IKIA5C033FB09089D41239DFB784E163208462359948")
    client_secret = os.getenv(
        "INTERSWITCH_CLIENT_SECRET", "CFE5A78D3E5C125AEB9D93A1B91C305276F0DF4D"
    )

    print("🔧 Initializing Interswitch client...")
    try:
        client = InterswitchClient(client_id=client_id, client_secret=client_secret)
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    print("\n📋 Token Information:")
    try:
        token_info = client.get_token_info()
        print(f"   Token valid: {token_info.get('is_valid')}")
        if token_info.get("expires_at"):
            print(f"   Expires at: {token_info['expires_at']}")
    except AuthenticationError as e:
        print(f"❌ Authentication Failed: {e.message}")
        return

    print("\n" + "=" * 60)
    print("Demo 1: NIN Verification")
    print("=" * 60)

    nin = input("Enter NIN to verify (or press Enter to skip): ").strip()
    if nin:
        first_name = input("Enter First name: ").strip()
        last_name = input("Enter Last name: ").strip()
        try:
            print(f"🔍 Verifying NIN: {nin}...")
            # Note: Using strict keyword arguments here
            response = client.verify_nin(nin=nin, first_name=first_name, last_name=last_name)

            print("✅ NIN Verification Successful!")
            print_response(response.data)
        except InterswitchError as e:
            print(f"❌ Error [{e.status_code}]: {e.message}")

    # Demo 2: BVN Verification (Full)
    print("\n" + "=" * 60)
    print("Demo 2: BVN Full Details Verification")
    print("=" * 60)

    bvn = input("Enter BVN for full details (or press Enter to skip): ").strip()
    if bvn:
        try:
            print(f"🔍 Fetching full BVN details for: {bvn}...")
            response = client.verify_bvn_full(bvn=bvn)

            print("✅ BVN Verification Successful!")
            print_response(response.data)
        except InterswitchError as e:
            print(f"❌ Error [{e.status_code}]: {e.message}")

    # Demo 3: BVN Boolean Match
    print("\n" + "=" * 60)
    print("Demo 3: BVN Boolean Match")
    print("=" * 60)

    bvn_bool = input("Enter BVN for boolean match (or press Enter to skip): ").strip()
    if bvn_bool:
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        try:
            print("🔍 Checking BVN match...")
            response = client.verify_bvn_boolean(
                bvn=bvn_bool,
                first_name=first_name,
                last_name=last_name,
            )
            print("✅ Match check completed!")
            print_response(response.data)
        except InterswitchError as e:
            print(f"❌ Error [{e.status_code}]: {e.message}")

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
            print_response(response.data)
        except InterswitchError as e:
            print(f"❌ Error [{e.status_code}]: {e.message}")

    print("\n" + "=" * 60)
    print("🎉 Sync Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

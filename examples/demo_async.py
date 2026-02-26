import asyncio
import json
import os

from interswitch import AsyncInterswitchClient
from interswitch.exceptions import InterswitchError


def print_response(data: dict | list | None) -> None:
    """Helper to pretty-print dictionary responses."""
    if isinstance(data, dict):
        print(json.dumps(data, indent=2))
    elif isinstance(data, list):
        print(json.dumps(data, indent=2))
    else:
        print("No data returned.")


async def main() -> None:
    """Run asynchronous demo examples."""

    client_id = os.getenv("INTERSWITCH_CLIENT_ID", "IKIA5C033FB09089D41239DFB784E163208462359948")
    client_secret = os.getenv(
        "INTERSWITCH_CLIENT_SECRET", "CFE5A78D3E5C125AEB9D93A1B91C305276F0DF4D"
    )

    print("⚡ Initializing Async Interswitch client...")

    async with AsyncInterswitchClient(client_id=client_id, client_secret=client_secret) as client:
        print("\n📋 Fetching Async Token Information...")
        token_info = client.get_token_info()
        print(f"   Token valid: {token_info.get('is_valid')}")

        print("\n" + "=" * 60)
        print("Async Demo: Fetching Supported Banks List")
        print("=" * 60)

        try:
            print("🔍 Requesting bank list...")
            response = await client.get_bank_list()

            print("✅ Bank list retrieved successfully!")
            banks = (
                response.data if isinstance(response.data, list) else response.data.get("banks", [])
            )
            print_response(banks[:3] if banks else None)
            print("   ... (truncated for brevity)")

        except InterswitchError as e:
            print(f"❌ Error [{e.status_code}]: {e.message}")

    print("\n" + "=" * 60)
    print("🎉 Async Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

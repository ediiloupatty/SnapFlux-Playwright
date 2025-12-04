"""
Script untuk memperbaiki company_id user admin_lorito
Mengganti company_id dari 1 (PT. Moyveronika) ke 2 (PT. LORITO BERKARYA ABADI)
"""

from modules.data.supabase_client import SupabaseManager


def main():
    print("=" * 80)
    print("FIX USER COMPANY_ID - SnapFlux")
    print("=" * 80)
    print()

    manager = SupabaseManager()

    if not manager.is_connected:
        print("❌ FAILED: Cannot connect to Supabase!")
        return

    print("✅ Connected to Supabase")
    print()

    # Check current state
    print("Checking current user data...")
    try:
        user_res = (
            manager.client.table("users")
            .select("*")
            .eq("username", "admin_lorito")
            .execute()
        )

        if not user_res.data:
            print("❌ User 'admin_lorito' not found!")
            return

        user = user_res.data[0]
        print(f"Current User Data:")
        print(f"  Username: {user['username']}")
        print(f"  Full Name: {user.get('full_name')}")
        print(f"  Current Company ID: {user.get('company_id')}")
        print()

        # Get company names
        if user.get("company_id"):
            comp_res = (
                manager.client.table("companies")
                .select("name")
                .eq("id", user["company_id"])
                .execute()
            )
            if comp_res.data:
                print(f"  Current Company: {comp_res.data[0]['name']}")

        # Get target company
        target_comp_res = (
            manager.client.table("companies").select("*").eq("id", 2).execute()
        )
        if not target_comp_res.data:
            print("❌ Target company (ID: 2) not found!")
            return

        target_company = target_comp_res.data[0]
        print()
        print(f"Target Company:")
        print(f"  ID: {target_company['id']}")
        print(f"  Name: {target_company['name']}")
        print()

        # Confirm
        print("-" * 80)
        confirm = input(
            f"Update admin_lorito company_id to {target_company['id']} ({target_company['name']})? (yes/no): "
        ).strip()

        if confirm.lower() != "yes":
            print("❌ Cancelled by user")
            return

        # Update user
        print()
        print("Updating user company_id...")
        update_res = (
            manager.client.table("users")
            .update({"company_id": target_company["id"]})
            .eq("username", "admin_lorito")
            .execute()
        )

        if update_res.data:
            print("✅ Successfully updated!")
            print()
            print("New User Data:")
            updated_user = update_res.data[0]
            print(f"  Username: {updated_user['username']}")
            print(f"  Full Name: {updated_user.get('full_name')}")
            print(f"  Company ID: {updated_user.get('company_id')}")
            print()

            # Verify
            print("Verifying update...")
            verify_res = (
                manager.client.table("users")
                .select("*, companies(name)")
                .eq("username", "admin_lorito")
                .execute()
            )

            if verify_res.data:
                verified = verify_res.data[0]
                print(f"  ✅ Verified Company ID: {verified.get('company_id')}")

                # Check accounts for this company
                print()
                print("Checking accounts for this company...")
                acc_res = (
                    manager.client.table("accounts")
                    .select("id")
                    .eq("company_id", target_company["id"])
                    .execute()
                )
                print(
                    f"  ✅ Found {len(acc_res.data)} accounts for {target_company['name']}"
                )

            print()
            print("=" * 80)
            print("✅ FIX COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print()
            print("📝 Next Steps:")
            print("1. Restart aplikasi SnapFlux")
            print("2. Login sebagai admin_lorito")
            print("3. Pastikan hanya muncul 24 akun (PT. LORITO)")
            print()
        else:
            print("❌ Update failed - no data returned")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Script untuk debugging dan checking database company_id issues
Jalankan script ini untuk memeriksa data users, accounts, dan company_id mapping
"""

import logging

from modules.data.supabase_client import SupabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    print("=" * 80)
    print("DATABASE CHECKER - SnapFlux Multi-Company System")
    print("=" * 80)
    print()

    manager = SupabaseManager()

    if not manager.is_connected:
        print("❌ FAILED: Cannot connect to Supabase!")
        return

    print("✅ Connected to Supabase")
    print()

    # 1. Check Companies
    print("-" * 80)
    print("1️⃣  CHECKING COMPANIES TABLE")
    print("-" * 80)
    try:
        companies_res = manager.client.table("companies").select("*").execute()
        companies = companies_res.data

        if companies:
            print(f"Total Companies: {len(companies)}")
            for comp in companies:
                print(f"  • ID: {comp['id']}, Name: {comp['name']}")
        else:
            print("⚠️  No companies found!")
    except Exception as e:
        print(f"❌ Error fetching companies: {e}")

    print()

    # 2. Check Users
    print("-" * 80)
    print("2️⃣  CHECKING USERS TABLE")
    print("-" * 80)
    try:
        users_res = manager.client.table("users").select("*").execute()
        users = users_res.data

        if users:
            print(f"Total Users: {len(users)}")
            for user in users:
                print(f"  • Username: {user['username']}")
                print(f"    Full Name: {user.get('full_name', 'N/A')}")
                print(
                    f"    Company ID: {user.get('company_id', 'NULL')} (type: {type(user.get('company_id'))})"
                )
                print(f"    Role: {user.get('role', 'N/A')}")
                print(f"    Active: {user.get('is_active', False)}")

                # Check if company_id exists in companies
                if user.get("company_id"):
                    comp_check = (
                        manager.client.table("companies")
                        .select("name")
                        .eq("id", user["company_id"])
                        .execute()
                    )
                    if comp_check.data:
                        print(f"    ✅ Company: {comp_check.data[0]['name']}")
                    else:
                        print(
                            f"    ❌ WARNING: company_id {user['company_id']} NOT FOUND in companies table!"
                        )
                else:
                    print(f"    ⚠️  WARNING: company_id is NULL/empty!")
                print()
        else:
            print("⚠️  No users found!")
    except Exception as e:
        print(f"❌ Error fetching users: {e}")

    print()

    # 3. Check Accounts by Company
    print("-" * 80)
    print("3️⃣  CHECKING ACCOUNTS TABLE (by company)")
    print("-" * 80)
    try:
        # Get all accounts
        all_accounts_res = manager.client.table("accounts").select("*").execute()
        all_accounts = all_accounts_res.data

        print(f"Total Accounts in Database: {len(all_accounts)}")
        print()

        # Group by company_id
        accounts_by_company = {}
        accounts_null_company = []

        for acc in all_accounts:
            company_id = acc.get("company_id")
            if company_id is None:
                accounts_null_company.append(acc)
            else:
                if company_id not in accounts_by_company:
                    accounts_by_company[company_id] = []
                accounts_by_company[company_id].append(acc)

        # Show breakdown
        for company_id, accounts in accounts_by_company.items():
            # Get company name
            comp_res = (
                manager.client.table("companies")
                .select("name")
                .eq("id", company_id)
                .execute()
            )
            company_name = (
                comp_res.data[0]["name"] if comp_res.data else "Unknown Company"
            )

            print(f"Company ID {company_id} ({company_name}): {len(accounts)} accounts")

            # Show first 3 accounts as sample
            for idx, acc in enumerate(accounts[:3], 1):
                print(
                    f"  {idx}. {acc.get('nama', 'N/A')} - {acc.get('username', 'N/A')} (company_id: {acc.get('company_id')})"
                )

            if len(accounts) > 3:
                print(f"  ... and {len(accounts) - 3} more accounts")
            print()

        if accounts_null_company:
            print(
                f"⚠️  WARNING: {len(accounts_null_company)} accounts with NULL company_id!"
            )
            for idx, acc in enumerate(accounts_null_company[:5], 1):
                print(
                    f"  {idx}. {acc.get('nama', 'N/A')} - {acc.get('username', 'N/A')}"
                )
            if len(accounts_null_company) > 5:
                print(f"  ... and {len(accounts_null_company) - 5} more")
            print()

    except Exception as e:
        print(f"❌ Error fetching accounts: {e}")

    print()

    # 4. Test Fetch Accounts with Company Filter
    print("-" * 80)
    print("4️⃣  TESTING FETCH_ACCOUNTS WITH COMPANY FILTER")
    print("-" * 80)

    # Test for each company
    try:
        for comp_id in accounts_by_company.keys():
            print(f"\nTesting fetch_accounts(company_filter={comp_id})...")
            filtered_accounts = manager.fetch_accounts(company_filter=comp_id)

            # Get company name
            comp_res = (
                manager.client.table("companies")
                .select("name")
                .eq("id", comp_id)
                .execute()
            )
            company_name = comp_res.data[0]["name"] if comp_res.data else "Unknown"

            print(f"  Company: {company_name}")
            print(f"  Expected: {len(accounts_by_company[comp_id])} accounts")
            print(f"  Returned: {len(filtered_accounts)} accounts")

            if len(filtered_accounts) == len(accounts_by_company[comp_id]):
                print("  ✅ PASS: Count matches!")
            else:
                print("  ❌ FAIL: Count mismatch!")

            # Show first 3
            if filtered_accounts:
                print("  Sample accounts:")
                for idx, acc in enumerate(filtered_accounts[:3], 1):
                    print(
                        f"    {idx}. {acc.get('nama')} - company_id should be {comp_id}"
                    )
    except Exception as e:
        print(f"❌ Error testing fetch: {e}")

    print()

    # 5. Check Automation Results
    print("-" * 80)
    print("5️⃣  CHECKING AUTOMATION_RESULTS TABLE")
    print("-" * 80)
    try:
        results_res = (
            manager.client.table("automation_results").select("*").limit(10).execute()
        )
        results = results_res.data

        if results:
            print(f"Sample Results (showing first 10):")
            for idx, res in enumerate(results, 1):
                print(
                    f"  {idx}. {res.get('nama', 'N/A')} - account_id: {res.get('account_id', 'NULL')}"
                )

                # Check if account_id valid
                if res.get("account_id"):
                    acc_check = (
                        manager.client.table("accounts")
                        .select("company_id")
                        .eq("id", res["account_id"])
                        .execute()
                    )
                    if acc_check.data:
                        print(
                            f"     ✅ Linked to company_id: {acc_check.data[0].get('company_id')}"
                        )
                    else:
                        print(f"     ❌ account_id {res['account_id']} NOT FOUND!")
                else:
                    print(f"     ⚠️  account_id is NULL!")
        else:
            print("ℹ️  No automation results yet")
    except Exception as e:
        print(f"❌ Error checking results: {e}")

    print()
    print("=" * 80)
    print("DATABASE CHECK COMPLETE")
    print("=" * 80)
    print()
    print("📝 RECOMMENDATIONS:")
    print("1. Pastikan semua users memiliki company_id yang valid")
    print("2. Pastikan semua accounts memiliki company_id yang sesuai")
    print("3. Pastikan automation_results memiliki account_id yang valid")
    print("4. Periksa logs di atas untuk warning atau error")
    print()

    # 6. Test Login untuk user tertentu
    print("-" * 80)
    print("6️⃣  TEST LOGIN (Optional)")
    print("-" * 80)
    print("Anda bisa test login untuk user tertentu:")
    print()

    username = input("Enter username to test (or press Enter to skip): ").strip()
    if username:
        password = input("Enter password: ").strip()
        if password:
            print(f"\nTesting login for '{username}'...")
            result = manager.login_user(username, password)

            if result["success"]:
                print("✅ Login SUCCESS!")
                user_info = result["user"]
                print(f"  Username: {user_info.get('username')}")
                print(f"  Full Name: {user_info.get('full_name')}")
                print(
                    f"  Company ID: {user_info.get('company_id')} (type: {type(user_info.get('company_id'))})"
                )
                print(f"  Company Name: {user_info.get('company_name')}")
                print(f"  Role: {user_info.get('role')}")

                # Test fetch accounts dengan company_id ini
                company_id = user_info.get("company_id")
                if company_id:
                    print(f"\n  Testing fetch_accounts with company_id={company_id}...")
                    test_accounts = manager.fetch_accounts(company_filter=company_id)
                    print(f"  ✅ Found {len(test_accounts)} accounts for this company")
                else:
                    print("  ⚠️  WARNING: User has NULL company_id!")
            else:
                print(f"❌ Login FAILED: {result.get('message')}")

    print()
    print("=" * 80)
    print("Script selesai. Periksa output di atas untuk masalah!")
    print("=" * 80)


if __name__ == "__main__":
    main()

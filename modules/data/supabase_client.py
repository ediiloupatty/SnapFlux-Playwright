import hashlib
import logging
import os
from datetime import datetime

from supabase import Client, create_client

# Hardcoded credentials as requested by user
SUPABASE_URL = "https://hidbcpniglqrarzwkkrf.supabase.co"
SUPABASE_KEY = "sb_publishable_-0x9OgbEDjiim9TdTZpBHg_TRwk6gXY"


class SupabaseManager:
    def __init__(self):
        self.logger = logging.getLogger("supabase_manager")
        self.client: Client = None
        self.is_connected = False

        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.is_connected = True
            self.logger.info("Supabase client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {str(e)}")
            self.is_connected = False

    def fetch_accounts(self, company_filter=None):
        """
        Fetch all accounts from 'accounts' table.
        Returns formatted list for the application.
        """
        if not self.is_connected:
            self.logger.error("Supabase not connected")
            return []

        try:
            self.logger.info(
                f"[DEBUG] fetch_accounts called with company_filter={company_filter}"
            )

            # Fetch data from 'accounts' table
            query = self.client.table("accounts").select("*")

            # Apply company filter if provided
            if company_filter:
                self.logger.info(
                    f"[DEBUG] Applying company_id filter: {company_filter}"
                )
                query = query.eq("company_id", company_filter)
            else:
                self.logger.warning(
                    "[DEBUG] No company_filter provided - fetching ALL accounts!"
                )

            response = query.execute()
            data = response.data

            self.logger.info(f"[DEBUG] Raw query returned {len(data)} accounts")

            # Debug: Log first few accounts with their company_id
            for idx, item in enumerate(data[:3]):
                self.logger.info(
                    f"[DEBUG] Account {idx + 1}: nama={item.get('nama')}, company_id={item.get('company_id')}"
                )

            formatted_accounts = []
            for idx, item in enumerate(data, 1):
                # Map DB columns to App format
                username = item.get("username", "")
                pin = item.get("pin", "")  # Correctly mapped to PIN column
                nama = item.get("nama", username)
                pangkalan_id = item.get("pangkalan_id", username)

                formatted_accounts.append(
                    {
                        "id": idx,
                        "nama": nama,
                        "username": username,
                        "pin": pin,
                        "pangkalan_id": pangkalan_id,
                        "status": "waiting",
                        "progress": 0,
                        "db_id": item.get("id"),
                    }
                )

            self.logger.info(
                f"[DEBUG] Fetched {len(formatted_accounts)} accounts from Supabase (company_filter={company_filter})"
            )
            return formatted_accounts

        except Exception as e:
            self.logger.error(f"Error fetching accounts from Supabase: {str(e)}")
            return []

    def update_account_result(
        self, username, stok, input_tabung, status, pangkalan_id=None
    ):
        """
        Update the result for a specific account in the database.

        Args:
            username: Username untuk mencari account
            stok: Stok value
            input_tabung: Tabung terjual
            status: Status hasil
            pangkalan_id: Optional pangkalan_id sebagai fallback pencarian
        """
        if not self.is_connected:
            self.logger.error(
                f"[DEBUG] Supabase not connected when updating {username}"
            )
            return False

        try:
            self.logger.info(
                f"[DEBUG] Updating result for username: {username}, pangkalan_id: {pangkalan_id}"
            )

            # Try to find account by username first
            account_res = (
                self.client.table("accounts")
                .select("id, pangkalan_id, nama, username")
                .eq("username", username)
                .execute()
            )

            # If not found by username, try pangkalan_id
            if not account_res.data and pangkalan_id:
                self.logger.warning(
                    f"[DEBUG] Account not found by username {username}, trying pangkalan_id: {pangkalan_id}"
                )
                account_res = (
                    self.client.table("accounts")
                    .select("id, pangkalan_id, nama, username")
                    .eq("pangkalan_id", pangkalan_id)
                    .execute()
                )

            if not account_res.data:
                self.logger.error(
                    f"[DEBUG] Account {username} / {pangkalan_id} not found in database"
                )
                return False

            account_data = account_res.data[0]
            self.logger.info(
                f"[DEBUG] Found account: id={account_data.get('id')}, nama={account_data.get('nama')}, username={account_data.get('username')}"
            )

            insert_data = {
                "account_id": account_data.get("id"),
                "pangkalan_id": account_data.get("pangkalan_id"),
                "nama": account_data.get("nama"),
                "stok": str(stok),
                "tabung_terjual": str(input_tabung),
                "status": status,
                "keterangan": f"Checked at {datetime.now().strftime('%H:%M')}",
            }

            self.logger.info(f"[DEBUG] Inserting data: {insert_data}")

            # Insert into automation_results
            try:
                result = (
                    self.client.table("automation_results")
                    .insert(insert_data)
                    .execute()
                )

                self.logger.info(f"[DEBUG] Insert result: {result}")
                self.logger.info(f"[DEBUG] Insert result.data: {result.data}")

                if result.data and len(result.data) > 0:
                    self.logger.info(
                        f"[DEBUG] ✅ Successfully inserted result to Supabase for {username}, record_id: {result.data[0].get('id')}"
                    )
                    return True
                else:
                    self.logger.error(
                        f"[DEBUG] ❌ Insert returned no data for {username}. Response: {result}"
                    )
                    return False
            except Exception as insert_error:
                self.logger.error(
                    f"[DEBUG] ❌ Insert exception for {username}: {str(insert_error)}",
                    exc_info=True,
                )
                return False

        except Exception as e:
            self.logger.error(
                f"[DEBUG] ❌ Error updating Supabase for {username}: {str(e)}",
                exc_info=True,
            )
            return False

    def get_today_summary(self, company_filter=None):
        """
        Get summary statistics from automation_results for today.
        Returns dict with total, success, failed, total_sales, total_stock.
        """
        if not self.is_connected:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "total_sales": 0,
                "total_stock": 0,
            }

        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # Better approach: Get account_ids for company first, then filter results
            if company_filter:
                # Get account_ids for this company
                acc_res = (
                    self.client.table("accounts")
                    .select("id")
                    .eq("company_id", company_filter)
                    .execute()
                )
                account_ids = [item["id"] for item in acc_res.data]

                if not account_ids:
                    return {
                        "total": 0,
                        "success": 0,
                        "failed": 0,
                        "total_sales": 0,
                        "total_stock": 0,
                    }

                # Fetch results for today with company filter using account_id
                query = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{today}T00:00:00")
                    .in_("account_id", account_ids)
                )
            else:
                # Fetch all results for today without filter
                query = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{today}T00:00:00")
                )

            response = query.execute()
            data = response.data

            total = len(data)
            success = 0
            failed = 0
            total_sales = 0
            total_stock = 0

            for item in data:
                status = item.get("status", "")

                # Count success/failed
                if "Ada Penjualan" in status or "Tidak Ada Penjualan" in status:
                    success += 1
                else:
                    failed += 1

                # Sum sales and stock
                try:
                    stok_str = (
                        str(item.get("stok", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    total_stock += int(stok_str)
                except:
                    pass

                try:
                    sales_str = (
                        str(item.get("tabung_terjual", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    total_sales += int(sales_str)
                except:
                    pass

            return {
                "total": total,
                "success": success,
                "failed": failed,
                "total_sales": total_sales,
                "total_stock": total_stock,
            }

        except Exception as e:
            self.logger.error(f"Error getting today summary: {str(e)}")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "total_sales": 0,
                "total_stock": 0,
            }

    def get_unprocessed_accounts_today(self, company_filter=None):
        """
        Get accounts that haven't been checked today (Smart Resume).
        Returns formatted list for the application.
        """
        if not self.is_connected:
            return []

        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # Get all accounts with company filter
            acc_query = self.client.table("accounts").select("*")
            if company_filter:
                acc_query = acc_query.eq("company_id", company_filter)

            all_accounts_res = acc_query.execute()
            all_accounts = all_accounts_res.data

            if not all_accounts:
                return []

            # Get account_ids for the filtered accounts
            account_ids = [acc.get("id") for acc in all_accounts]

            # Get processed account_ids today
            processed_res = (
                self.client.table("automation_results")
                .select("account_id")
                .gte("created_at", f"{today}T00:00:00")
                .in_("account_id", account_ids)
                .execute()
            )
            processed_account_ids = set(
                item.get("account_id")
                for item in processed_res.data
                if item.get("account_id")
            )

            # Filter unprocessed accounts
            unprocessed = []
            idx = 1
            for account in all_accounts:
                account_db_id = account.get("id")
                if account_db_id not in processed_account_ids:
                    unprocessed.append(
                        {
                            "id": idx,
                            "nama": account.get("nama", account.get("username")),
                            "username": account.get("username", ""),
                            "pin": account.get("pin", ""),
                            "pangkalan_id": account.get(
                                "pangkalan_id", account.get("username")
                            ),
                            "status": "waiting",
                            "progress": 0,
                            "db_id": account_db_id,
                        }
                    )
                    idx += 1

            self.logger.info(
                f"Found {len(unprocessed)} unprocessed accounts for today (company_id: {company_filter})"
            )
            return unprocessed

        except Exception as e:
            self.logger.error(f"Error getting unprocessed accounts: {str(e)}")
            return []

    def get_stock_movement_today(self, company_filter=None):
        """
        Calculate yesterday's actual sales based on stock difference.
        Logic:
        - Get yesterday's last check (last stock + reported sales)
        - Get today's first check (current stock)
        - Calculate: Total Sales Yesterday = Reported Sales Yesterday + (Yesterday Stock - Today Stock)
        """
        if not self.is_connected:
            return {
                "total_sales_yesterday": 0,
                "reported_sales_yesterday": 0,
                "unreported_sales": 0,
            }

        try:
            from datetime import timedelta

            today = datetime.now().date()
            yesterday = today - timedelta(days=1)

            today_str = today.strftime("%Y-%m-%d")
            yesterday_str = yesterday.strftime("%Y-%m-%d")

            if company_filter:
                # Get account_ids for this company
                acc_res = (
                    self.client.table("accounts")
                    .select("id")
                    .eq("company_id", company_filter)
                    .execute()
                )
                account_ids = [item["id"] for item in acc_res.data]

                if not account_ids:
                    return {
                        "total_sales_yesterday": 0,
                        "reported_sales_yesterday": 0,
                        "unreported_sales": 0,
                    }

                # Get yesterday's data with company filter
                query_yesterday = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{yesterday_str}T00:00:00")
                    .lt("created_at", f"{today_str}T00:00:00")
                    .in_("account_id", account_ids)
                    .order("created_at")
                )

                # Get today's data with company filter
                query_today = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{today_str}T00:00:00")
                    .in_("account_id", account_ids)
                    .order("created_at")
                )
            else:
                # Get all data without filter
                query_yesterday = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{yesterday_str}T00:00:00")
                    .lt("created_at", f"{today_str}T00:00:00")
                    .order("created_at")
                )
                query_today = (
                    self.client.table("automation_results")
                    .select("*")
                    .gte("created_at", f"{today_str}T00:00:00")
                    .order("created_at")
                )

            yesterday_response = query_yesterday.execute()
            yesterday_data = yesterday_response.data

            today_response = query_today.execute()
            today_data = today_response.data

            if not yesterday_data or not today_data:
                return {
                    "total_sales_yesterday": 0,
                    "reported_sales_yesterday": 0,
                    "unreported_sales": 0,
                }

            # Group by account_id (more reliable than pangkalan_id)
            yesterday_by_account = {}
            for item in yesterday_data:
                account_id = item.get("account_id")
                if not account_id:
                    continue
                if account_id not in yesterday_by_account:
                    yesterday_by_account[account_id] = []
                yesterday_by_account[account_id].append(item)

            today_by_account = {}
            for item in today_data:
                account_id = item.get("account_id")
                if not account_id:
                    continue
                if account_id not in today_by_account:
                    today_by_account[account_id] = []
                today_by_account[account_id].append(item)

            # Calculate for each account
            total_sales_yesterday = 0
            total_reported_yesterday = 0
            total_unreported = 0

            for account_id in yesterday_by_account.keys():
                # Get last check from yesterday
                yesterday_checks = sorted(
                    yesterday_by_account[account_id],
                    key=lambda x: x.get("created_at", ""),
                )
                if not yesterday_checks:
                    continue

                last_check_yesterday = yesterday_checks[-1]  # Last check yesterday

                # Get first check from today for this account
                if account_id not in today_by_account:
                    continue

                today_checks = sorted(
                    today_by_account[account_id], key=lambda x: x.get("created_at", "")
                )
                if not today_checks:
                    continue

                first_check_today = today_checks[0]  # First check today

                try:
                    # Parse stock values
                    yesterday_stock_str = (
                        str(last_check_yesterday.get("stok", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    today_stock_str = (
                        str(first_check_today.get("stok", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )

                    yesterday_stock = int(yesterday_stock_str)
                    today_stock = int(today_stock_str)

                    # Parse reported sales (tabung_terjual) from yesterday
                    reported_str = (
                        str(last_check_yesterday.get("tabung_terjual", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    reported_sales = int(reported_str)

                    # Calculate stock difference (overnight sales not recorded)
                    stock_diff = yesterday_stock - today_stock

                    if stock_diff >= 0:
                        # Stock diff is the unreported sales (sold after last check yesterday)
                        unreported = stock_diff

                        # Total sales yesterday = reported + unreported
                        total_yesterday = reported_sales + unreported

                        total_sales_yesterday += total_yesterday
                        total_reported_yesterday += reported_sales
                        total_unreported += unreported

                except Exception as e:
                    self.logger.error(
                        f"Error parsing data for account_id {account_id}: {str(e)}"
                    )
                    continue

            return {
                "total_sales_yesterday": total_sales_yesterday,
                "reported_sales_yesterday": total_reported_yesterday,
                "unreported_sales": total_unreported,
            }

        except Exception as e:
            self.logger.error(f"Error calculating stock movement: {str(e)}")
            return {
                "total_sales_yesterday": 0,
                "reported_sales_yesterday": 0,
                "unreported_sales": 0,
            }

    def add_account(self, data):
        """
        Add a new account to the database.
        Data dict should contain: nama, username, pin, pangkalan_id, company_id
        Returns: (success, message)
        """
        if not self.is_connected:
            return False, "Tidak ada koneksi ke database"

        username = data.get("username")
        pangkalan_id = data.get("pangkalan_id")
        
        try:
            # Check if username exists
            existing_user = (
                self.client.table("accounts")
                .select("id")
                .eq("username", username)
                .execute()
            )
            if existing_user.data:
                self.logger.warning(f"Account {username} already exists")
                return False, f"Username '{username}' sudah terdaftar"

            # Check if pangkalan_id exists (optional validation if unique is required)
            if pangkalan_id:
                existing_pangkalan = (
                    self.client.table("accounts")
                    .select("id")
                    .eq("pangkalan_id", pangkalan_id)
                    .execute()
                )
                if existing_pangkalan.data:
                    self.logger.warning(f"Pangkalan ID {pangkalan_id} already exists")
                    return False, f"ID Pangkalan '{pangkalan_id}' sudah terdaftar pada akun lain"

            # Insert new account
            insert_data = {
                "nama": data.get("nama"),
                "username": username,
                "pin": data.get("pin"),
                "pangkalan_id": pangkalan_id,
                "status": "active",
                "company_id": data.get("company_id"),
            }

            self.client.table("accounts").insert(insert_data).execute()
            self.logger.info(f"Successfully added account: {username}")
            return True, "Berhasil menambahkan akun"
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error adding account {username}: {error_msg}")
            
            # Try to catch specific Supabase/Postgres errors if message is generic
            if "duplicate key value" in error_msg:
                if "username" in error_msg:
                    return False, "Username sudah digunakan"
                if "pangkalan_id" in error_msg:
                    return False, "ID Pangkalan sudah digunakan"
            
            return False, f"Gagal menyimpan ke database: {error_msg}"

    def get_stock_summary_by_date(self, company_filter=None, date_str=None):
        """
        Get stock summary for a specific date.

        Args:
            company_filter (int): Company ID to filter
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            dict: {total_stock: int, total_sales: int}
        """
        if not self.is_connected:
            return {"total_stock": 0, "total_sales": 0}

        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")

            # Get account_ids for company
            if company_filter:
                acc_res = (
                    self.client.table("accounts")
                    .select("id")
                    .eq("company_id", company_filter)
                    .execute()
                )
                account_ids = [item["id"] for item in acc_res.data]

                if not account_ids:
                    return {"total_stock": 0, "total_sales": 0}

                # Get results for this date with company filter
                query = (
                    self.client.table("automation_results")
                    .select("stok, tabung_terjual")
                    .gte("created_at", f"{date_str}T00:00:00")
                    .lte("created_at", f"{date_str}T23:59:59.999999")
                    .in_("account_id", account_ids)
                )
            else:
                query = (
                    self.client.table("automation_results")
                    .select("stok, tabung_terjual")
                    .gte("created_at", f"{date_str}T00:00:00")
                    .lte("created_at", f"{date_str}T23:59:59.999999")
                )

            response = query.execute()
            data = response.data

            total_stock = 0
            total_sales = 0

            for item in data:
                try:
                    stok_str = (
                        str(item.get("stok", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    total_stock += int(stok_str)
                except:
                    pass

                try:
                    sales_str = (
                        str(item.get("tabung_terjual", "0"))
                        .replace(" Tabung", "")
                        .replace(",", "")
                    )
                    total_sales += int(sales_str)
                except:
                    pass

            return {"total_stock": total_stock, "total_sales": total_sales}

        except Exception as e:
            self.logger.error(f"Error getting stock summary: {str(e)}")
            return {"total_stock": 0, "total_sales": 0}

    def get_automation_results(self, company_filter=None, limit=100, date_filter=None):
        """
        Get automation results (monitoring data) with company filter.

        Args:
            company_filter (int): Company ID to filter results
            limit (int): Maximum number of results to return
            date_filter (str): Date filter in YYYY-MM-DD format (optional)

        Returns:
            list: List of automation results
        """
        if not self.is_connected:
            return []

        try:
            # Base query
            query = (
                self.client.table("automation_results")
                .select("*")
                .order("created_at", desc=True)
            )

            # Apply date filter if provided
            if date_filter:
                self.logger.info(f"[DEBUG] Applying date filter: {date_filter}")
                # Use lte (less than or equal) instead of lt to include 23:59:59
                query = query.gte("created_at", f"{date_filter}T00:00:00").lte(
                    "created_at", f"{date_filter}T23:59:59.999999"
                )

            # Apply company filter via account_id
            if company_filter:
                # Get account_ids for this company
                acc_res = (
                    self.client.table("accounts")
                    .select("id")
                    .eq("company_id", company_filter)
                    .execute()
                )
                account_ids = [item["id"] for item in acc_res.data]

                if not account_ids:
                    return []

                # Filter by account_ids
                query = query.in_("account_id", account_ids)

            # Apply limit
            query = query.limit(limit)

            response = query.execute()
            self.logger.info(
                f"Fetched {len(response.data)} automation results (company_id: {company_filter})"
            )
            return response.data

        except Exception as e:
            self.logger.error(f"Error fetching automation results: {str(e)}")
            return []

    def login_user(self, username, password):
        """
        Login user by checking credentials against 'users' table.
        Password is hashed using SHA256 before comparison.
        """
        if not self.is_connected:
            return {"success": False, "message": "Database not connected"}

        try:
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Fetch user
            response = (
                self.client.table("users")
                .select("*")
                .eq("username", username)
                .execute()
            )

            if not response.data:
                return {"success": False, "message": "Username tidak ditemukan"}

            user = response.data[0]

            # Check password
            if user.get("password_hash") == password_hash:
                # Check if active
                if not user.get("is_active", True):
                    return {"success": False, "message": "Akun dinonaktifkan"}

                # Update last login
                try:
                    self.client.table("users").update(
                        {"last_login": datetime.now().isoformat()}
                    ).eq("id", user["id"]).execute()
                except:
                    pass

                # Get company name
                company_name = "Unknown"
                company_id = user.get("company_id")
                if company_id:
                    try:
                        comp_res = (
                            self.client.table("companies")
                            .select("name")
                            .eq("id", company_id)
                            .execute()
                        )
                        if comp_res.data:
                            company_name = comp_res.data[0]["name"]
                    except:
                        pass

                return {
                    "success": True,
                    "user": {
                        "username": user["username"],
                        "full_name": user.get("full_name"),
                        "company_id": company_id,
                        "company_name": company_name,
                        "role": user.get("role"),
                    },
                }
            else:
                return {"success": False, "message": "Password salah"}

        except Exception as e:
            self.logger.error(f"Login error for {username}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

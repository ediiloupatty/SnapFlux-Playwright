
import os
import logging
import hashlib
from datetime import datetime
from supabase import create_client, Client

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
            return []

        try:
            # Fetch data from 'accounts' table
            query = self.client.table("accounts").select("*")
            
            # Apply company filter if provided
            if company_filter:
                query = query.eq("company_name", company_filter)
                
            response = query.execute()
            data = response.data
            
            formatted_accounts = []
            for idx, item in enumerate(data, 1):
                # Map DB columns to App format
                username = item.get("username", "")
                pin = item.get("pin", "") # Correctly mapped to PIN column
                nama = item.get("nama", username)
                pangkalan_id = item.get("pangkalan_id", username)
                
                formatted_accounts.append({
                    "id": idx,
                    "nama": nama,
                    "username": username,
                    "pin": pin,
                    "pangkalan_id": pangkalan_id,
                    "status": "waiting",
                    "progress": 0,
                    "db_id": item.get("id")
                })
                
            self.logger.info(f"Fetched {len(formatted_accounts)} accounts from Supabase")
            return formatted_accounts

        except Exception as e:
            self.logger.error(f"Error fetching accounts from Supabase: {str(e)}")
            return []

    def update_account_result(self, username, stok, input_tabung, status):
        """
        Update the result for a specific account in the database.
        """
        if not self.is_connected:
            return False

        try:
            account_res = self.client.table("accounts").select("pangkalan_id, nama").eq("username", username).execute()
            if not account_res.data:
                self.logger.warning(f"Account {username} not found for result logging")
                return False
                
            account_data = account_res.data[0]
            
            insert_data = {
                "pangkalan_id": account_data.get("pangkalan_id"),
                "nama": account_data.get("nama"),
                "stok": str(stok),
                "tabung_terjual": str(input_tabung),
                "status": status,
                "keterangan": f"Checked at {datetime.now().strftime('%H:%M')}"
            }
            
            # Insert into automation_results
            self.client.table("automation_results").insert(insert_data).execute()
            self.logger.info(f"Inserted result to Supabase for {username}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating Supabase for {username}: {str(e)}")
            return False

    def get_today_summary(self, company_filter=None):
        """
        Get summary statistics from automation_results for today.
        Returns dict with total, success, failed, total_sales, total_stock.
        """
        if not self.is_connected:
            return {"total": 0, "success": 0, "failed": 0, "total_sales": 0, "total_stock": 0}

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Fetch all results for today
            query = self.client.table("automation_results").select("*").gte("created_at", f"{today}T00:00:00")
            
            # Apply company filter if provided
            # Note: automation_results doesn't have company_name directly, but we can filter by pangkalan_id if needed
            # However, for simplicity and performance, we might need to join or filter in application
            # Ideally automation_results should have company_id or we filter by accounts first
            
            # Better approach: Get accounts for company first, then filter results
            if company_filter:
                # Get pangkalan_ids for this company
                acc_res = self.client.table("accounts").select("pangkalan_id").eq("company_name", company_filter).execute()
                pangkalan_ids = [item["pangkalan_id"] for item in acc_res.data]
                
                if not pangkalan_ids:
                    return {"total": 0, "success": 0, "failed": 0, "total_sales": 0, "total_stock": 0}
                    
                # Filter results by these pangkalan_ids
                # Supabase 'in' filter takes a list
                query = query.in_("pangkalan_id", pangkalan_ids)
            
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
                    stok_str = str(item.get("stok", "0")).replace(" Tabung", "").replace(",", "")
                    total_stock += int(stok_str)
                except:
                    pass
                    
                try:
                    sales_str = str(item.get("tabung_terjual", "0")).replace(" Tabung", "").replace(",", "")
                    total_sales += int(sales_str)
                except:
                    pass
            
            return {
                "total": total,
                "success": success,
                "failed": failed,
                "total_sales": total_sales,
                "total_stock": total_stock
            }

        except Exception as e:
            self.logger.error(f"Error getting today summary: {str(e)}")
            return {"total": 0, "success": 0, "failed": 0, "total_sales": 0, "total_stock": 0}

    def get_unprocessed_accounts_today(self, company_filter=None):
        """
        Get accounts that haven't been checked today (Smart Resume).
        Returns formatted list for the application.
        """
        if not self.is_connected:
            return []

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get all accounts
            acc_query = self.client.table("accounts").select("*")
            if company_filter:
                acc_query = acc_query.eq("company_name", company_filter)
            
            all_accounts_res = acc_query.execute()
            all_accounts = all_accounts_res.data
            
            # Get processed accounts today (based on pangkalan_id)
            processed_res = self.client.table("automation_results").select("pangkalan_id").gte("created_at", f"{today}T00:00:00").execute()
            processed_ids = set(item.get("pangkalan_id") for item in processed_res.data)
            
            # Filter unprocessed accounts
            unprocessed = []
            idx = 1
            for account in all_accounts:
                pangkalan_id = account.get("pangkalan_id", account.get("username"))
                if pangkalan_id not in processed_ids:
                    unprocessed.append({
                        "id": idx,
                        "nama": account.get("nama", account.get("username")),
                        "username": account.get("username", ""),
                        "pin": account.get("pin", ""),
                        "pangkalan_id": pangkalan_id,
                        "status": "waiting",
                        "progress": 0,
                        "db_id": account.get("id")
                    })
                    idx += 1
            
            self.logger.info(f"Found {len(unprocessed)} unprocessed accounts for today")
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
            return {"total_sales_yesterday": 0, "reported_sales_yesterday": 0, "unreported_sales": 0}

        try:
            from datetime import timedelta
            
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            today_str = today.strftime("%Y-%m-%d")
            yesterday_str = yesterday.strftime("%Y-%m-%d")
            
            # Get yesterday's data (all checks from yesterday)
            query_yesterday = self.client.table("automation_results").select("*").gte("created_at", f"{yesterday_str}T00:00:00").lt("created_at", f"{today_str}T00:00:00").order("created_at")
            
            # Get today's data (all checks from today)
            query_today = self.client.table("automation_results").select("*").gte("created_at", f"{today_str}T00:00:00").order("created_at")
            
            if company_filter:
                # Get pangkalan_ids for this company
                acc_res = self.client.table("accounts").select("pangkalan_id").eq("company_name", company_filter).execute()
                pangkalan_ids = [item["pangkalan_id"] for item in acc_res.data]
                
                if not pangkalan_ids:
                    return {"total_sales_yesterday": 0, "reported_sales_yesterday": 0, "unreported_sales": 0}
                
                query_yesterday = query_yesterday.in_("pangkalan_id", pangkalan_ids)
                query_today = query_today.in_("pangkalan_id", pangkalan_ids)

            yesterday_response = query_yesterday.execute()
            yesterday_data = yesterday_response.data
            
            today_response = query_today.execute()
            today_data = today_response.data
            
            if not yesterday_data or not today_data:
                return {"total_sales_yesterday": 0, "reported_sales_yesterday": 0, "unreported_sales": 0}
            
            # Group by pangkalan_id
            yesterday_by_account = {}
            for item in yesterday_data:
                pangkalan_id = item.get("pangkalan_id")
                if not pangkalan_id:
                    continue
                if pangkalan_id not in yesterday_by_account:
                    yesterday_by_account[pangkalan_id] = []
                yesterday_by_account[pangkalan_id].append(item)
            
            today_by_account = {}
            for item in today_data:
                pangkalan_id = item.get("pangkalan_id")
                if not pangkalan_id:
                    continue
                if pangkalan_id not in today_by_account:
                    today_by_account[pangkalan_id] = []
                today_by_account[pangkalan_id].append(item)
            
            # Calculate for each account
            total_sales_yesterday = 0
            total_reported_yesterday = 0
            total_unreported = 0
            
            for pangkalan_id in yesterday_by_account.keys():
                # Get last check from yesterday
                yesterday_checks = sorted(yesterday_by_account[pangkalan_id], key=lambda x: x.get("created_at", ""))
                if not yesterday_checks:
                    continue
                    
                last_check_yesterday = yesterday_checks[-1]  # Last check yesterday
                
                # Get first check from today for this account
                if pangkalan_id not in today_by_account:
                    continue
                    
                today_checks = sorted(today_by_account[pangkalan_id], key=lambda x: x.get("created_at", ""))
                if not today_checks:
                    continue
                    
                first_check_today = today_checks[0]  # First check today
                
                try:
                    # Parse stock values
                    yesterday_stock_str = str(last_check_yesterday.get("stok", "0")).replace(" Tabung", "").replace(",", "")
                    today_stock_str = str(first_check_today.get("stok", "0")).replace(" Tabung", "").replace(",", "")
                    
                    yesterday_stock = int(yesterday_stock_str)
                    today_stock = int(today_stock_str)
                    
                    # Parse reported sales (tabung_terjual) from yesterday
                    reported_str = str(last_check_yesterday.get("tabung_terjual", "0")).replace(" Tabung", "").replace(",", "")
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
                    self.logger.error(f"Error parsing data for {pangkalan_id}: {str(e)}")
                    continue
            
            return {
                "total_sales_yesterday": total_sales_yesterday,
                "reported_sales_yesterday": total_reported_yesterday,
                "unreported_sales": total_unreported
            }

        except Exception as e:
            self.logger.error(f"Error calculating stock movement: {str(e)}")
            return {"total_sales_yesterday": 0, "reported_sales_yesterday": 0, "unreported_sales": 0}

    def add_account(self, nama, username, pin, pangkalan_id):
        '''Add a new account to the database. Returns True if successful, False otherwise.'''
        if not self.is_connected:
            return False
        try:
            insert_data = {'nama': nama, 'username': username, 'pin': pin, 'pangkalan_id': pangkalan_id}
            self.client.table('accounts').insert(insert_data).execute()
            self.logger.info(f'Successfully added account: {username}')
            return True
        except Exception as e:
            self.logger.error(f'Error adding account {username}: {str(e)}')
            return False

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
            response = self.client.table("users").select("*").eq("username", username).execute()
            
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
                    self.client.table("users").update({
                        "last_login": datetime.now().isoformat()
                    }).eq("id", user["id"]).execute()
                except:
                    pass
                
                return {
                    "success": True,
                    "user": {
                        "username": user["username"],
                        "full_name": user.get("full_name"),
                        "company_access": user.get("company_access"),
                        "role": user.get("role")
                    }
                }
            else:
                return {"success": False, "message": "Password salah"}

        except Exception as e:
            self.logger.error(f"Login error for {username}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

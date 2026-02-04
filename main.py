"""
Main CLI entry point for SnapFlux Automation (No GUI)
Fokus pada alur scraping: Login -> Cek Stok -> Cek Penjualan -> Simpan CSV
"""

import sys
import time
import logging
import os
import csv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.browser.setup import PlaywrightBrowserManager
from modules.browser.login import login_direct
from modules.browser.extractor import (
    get_stock_value_direct, 
    get_tabung_terjual_direct, 
    get_customer_list_from_cards,
    click_last_customer_card,
    click_first_customer_card,
    get_transaction_timestamp
)
from modules.browser.navigation import click_laporan_penjualan_direct, click_rekap_penjualan_direct

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cli_automation")

def save_to_csv(result_data, filename="results/model_scraping_results.csv"):
    """Simpan hasil scraping ke file CSV"""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "pangkalan_id", "nama", "username", 
            "stok", "penjualan", "status"
        ])
        
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(result_data)
    
    print(f"\n[INFO] Hasil berhasil disimpan ke: {filename}")
    print("-" * 50)
    print(f"Timestamp    : {result_data['timestamp']}")
    print(f"Nama         : {result_data['nama']}")
    print(f"Stok         : {result_data['stok']}")
    print(f"Penjualan    : {result_data['penjualan']}")
    print(f"Status       : {result_data['status']}")
    print("-" * 50)

def main():
    start_time = time.time()
    print("============================================================")
    print("SNAPFLUX AUTOMATION - CLI VERSION")
    print("============================================================")

    # 1. Setup Account Data
    account = {
        "nama": "Yoltje",
        "username": "yultjekodongan687@gmail.com",
        "pin": "556677",
        "pangkalan_id": "795357834624021"
    }

    print(f"Target Akun: {account['nama']} ({account['username']})")
    
    browser_manager = None
    
    try:
        # 2. Setup Browser
        print("\n[STEP 1] Setup Browser...")
        browser_manager = PlaywrightBrowserManager()
        # Menggunakan headless=False agar terlihat prosesnya (sesuai request 'coba lihat')
        page = browser_manager.setup_browser(headless=False)
        
        if not page:
            print("[ERROR] Gagal setup browser!")
            return
            


        # 3. Login
        print("\n[STEP 2] Login...")
        success, login_info = login_direct(page, account["username"], account["pin"])
        
        if not success:
            print(f"[ERROR] Login gagal! Info: {login_info}")
            return
            
        print("[SUCCESS] Login berhasil!")

        # 4. Get Data Stok
        print("\n[STEP 3] Mengambil Data Stok...")
        stok_value = get_stock_value_direct(page)
        
        if stok_value:
            print(f"[SUCCESS] Stok ditemukan: {stok_value} Tabung")
        else:
            print("[WARNING] Gagal mengambil data stok (atau stok 0?)")
            stok_value = "0" # Default ke 0 jika gagal/tidak ada

        # 5. Get Data Penjualan
        print("\n[STEP 4] Mengambil Data Penjualan...")
        # Klik menu Laporan Penjualan dulu
        nav_success = click_laporan_penjualan_direct(page)
        
        terjual_value = 0
        if nav_success:
            # Ambil data penjualan
            terjual_val = get_tabung_terjual_direct(page)
            if terjual_val is not None:
                terjual_value = terjual_val
                print(f"[SUCCESS] Data terjual ditemukan: {terjual_value} Tabung")
                
                # --- TAMBAHAN AKSI: Jika ada penjualan, klik Rekap Penjualan ---
                if terjual_value > 0:
                    print("\n[INFO] Stok terjual > 0, mengklik menu Rekap Penjualan...")
                    if click_rekap_penjualan_direct(page):
                        print("[SUCCESS] Berhasil klik menu Rekap Penjualan")
                        
                        # --- TAMBAHAN BARU: List Customer & Klik Terakhir ---
                        time.sleep(1.0) # Tunggu loading list
                        customers = get_customer_list_from_cards(page)
                        print(f"[INFO] Total customer terdeteksi: {len(customers)}")
                        
                        if customers:
                           # --- EXTRA ALUR: Klik Last -> Timestamp -> Back -> Klik First ---
                            # Aksi 1: Klik Customer Paling Bawah (Sudah scroll sebelumnya)
                            if click_last_customer_card(page):
                                # Ambil Timestamp Customer Terakhir
                                ts_last = get_transaction_timestamp(page)
                                print(f"[INFO] Waktu Transaksi (Last Customer): {ts_last}")
                                
                                # Kembali ke list
                                print("Navigasi kembali ke daftar customer...")
                                page.go_back()
                                time.sleep(1.5) # Wait reload
                                
                                # Aksi 2: Klik Customer Paling Atas
                                if click_first_customer_card(page):
                                    # Ambil Timestamp Customer Pertama
                                    ts_first = get_transaction_timestamp(page)
                                    print(f"[INFO] Waktu Transaksi (First Customer): {ts_first}")
                                    
                                    print("\n" + "="*50)
                                    print("ANALISIS WAKTU INPUT")
                                    print("="*50)
                                    print(f"Jam Pertama (Bawah) : {ts_last}")
                                    print(f"Jam Kedua (Atas)    : {ts_first}")
                                    print("-> Berarti pangkalan input berada dalam kurun waktu tersebut")
                                    print("="*50 + "\n")
                                    
                                    # Kembali lagi (optional, untuk cleanup)
                                    page.go_back()
                                    time.sleep(0.5)    # ----------------------------------------------------
                                    
                                else:
                                    print("[WARNING] Gagal klik menu Rekap Penjualan")
                            # ----------------------------------------------------------------
                        
                    else:
                        print("[WARNING] Gagal klik menu Rekap Penjualan")
                # ----------------------------------------------------------------
            else:
                print("[WARNING] Gagal mengambil data terjual")
        else:
            print("[ERROR] Gagal navigasi ke Laporan Penjualan")

        # 6. Process & Save Results
        print("\n[STEP 5] Menyimpan Hasil...")
        
        # Format values
        try:
            stok_int = int(str(stok_value).replace(".", "").replace(",", "").strip())
        except:
            stok_int = 0
            
        status = "Ada Penjualan" if terjual_value > 0 else "Tidak Ada Penjualan"
        
        result_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pangkalan_id": account["pangkalan_id"],
            "nama": account["nama"],
            "username": account["username"],
            "stok": f"{stok_int} Tabung",
            "penjualan": f"{terjual_value} Tabung",
            "status": status
        }
        
        save_to_csv(result_data)
        
    except Exception as e:
        print(f"\n[EXCEPTION] Terjadi error: {str(e)}")
        logger.error(f"Main loop error: {str(e)}", exc_info=True)
        
    finally:
        # 7. Cleanup
        print("\n[STEP 6] Cleanup...")
        if browser_manager:
            time.sleep(3) # Beri waktu sejenak untuk melihat hasil akhir
            browser_manager.close()

        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"\n[INFO] Total Waktu Eksekusi: {minutes} menit {seconds} detik")
        print("Selesai.")

if __name__ == "__main__":
    main()

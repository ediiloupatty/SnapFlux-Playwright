"""
Constants dan konfigurasi untuk PlayWRight automation (Standalone)
File ini berisi semua konstanta yang diperlukan tanpa bergantung pada folder src
"""

import os
from datetime import datetime

# ============================================
# PATH CONFIGURATION
# ============================================

# Base directory untuk PlayWRight
PLAYWRIGHT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PLAYWRIGHT_DIR)

# Direktori penting
AKUN_DIR = os.path.join(BASE_DIR, "akun")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "playwright_automation.log")

# ============================================
# URL CONFIGURATION
# ============================================

LOGIN_URL = "https://subsiditepatlpg.mypertamina.id/merchant-login"

# ============================================
# BULAN INDONESIA
# ============================================

BULAN_ID = [
    "",
    "JANUARI",
    "FEBRUARI",
    "MARET",
    "APRIL",
    "MEI",
    "JUNI",
    "JULI",
    "AGUSTUS",
    "SEPTEMBER",
    "OKTOBER",
    "NOVEMBER",
    "DESEMBER",
]

BULAN_SINGKAT = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agt",
    "Sep",
    "Okt",
    "Nov",
    "Des",
]

# ============================================
# TIMING CONFIGURATION
# ============================================

DEFAULT_DELAY = 2.0  # Delay default antar operasi
RETRY_DELAY = 2.0  # Delay saat retry
ERROR_DELAY = 1.0  # Delay saat error
INTER_ACCOUNT_DELAY = 2.0  # Delay antar akun
MAX_RETRIES = 3  # Maksimal retry

# ============================================
# BROWSER CONFIGURATION
# ============================================

HEADLESS_MODE = True  # Default headless mode
PAGE_LOAD_TIMEOUT = 20000  # 20 detik (dalam milliseconds)
NAVIGATION_TIMEOUT = 20000  # 20 detik (dalam milliseconds)
DEFAULT_TIMEOUT = 20000  # 20 detik (dalam milliseconds)

# ============================================
# CHROME BINARY PATHS
# ============================================

CHROME_BINARY = r"D:\edi\Programing\Snapflux v2\chrome\Chromium\bin\chrome.exe"

# ============================================
# EXCEL CONFIGURATION
# ============================================


def get_master_filename(selected_date=None):
    """
    Generate nama file Excel master dengan format: DATA_SNAPFLUX_MASTER_YYYY_BULAN.xlsx

    Args:
        selected_date (datetime): Tanggal yang dipilih

    Returns:
        str: Nama file Excel
    """
    if selected_date:
        year = selected_date.year
        month = selected_date.month
        month_name = BULAN_ID[month].upper()
    else:
        now = datetime.now()
        year = now.year
        month = now.month
        month_name = BULAN_ID[month].upper()

    return f"DATA_SNAPFLUX_MASTER_{year}_{month_name}.xlsx"


def get_sheet_name_dynamic(selected_date=None):
    """
    Generate nama sheet berdasarkan bulan

    Args:
        selected_date (datetime): Tanggal yang dipilih

    Returns:
        str: Nama sheet
    """
    if selected_date:
        month = selected_date.month
        year = selected_date.year
    else:
        month = datetime.now().month
        year = datetime.now().year

    return f"{BULAN_ID[month].upper()}_{year}"


# ============================================
# VALIDATION PATTERNS
# ============================================

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_PATTERN = r"^(08|628)\d{8,13}$"
PIN_MIN_LENGTH = 4
PIN_MAX_LENGTH = 8

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOG_LEVEL = "INFO"
LOG_MAX_BYTES = 2 * 1024 * 1024  # 2MB
LOG_BACKUP_COUNT = 3
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================
# DATA EXTRACTION PATTERNS
# ============================================

# Pattern untuk mengambil stok dari dashboard
STOK_PATTERNS = [
    r"Stok\s*\n?\s*(\d+)\s*Tabung",
    r"Stok[:\s]*(\d+)\s*Tabung",
]

# Pattern untuk mengambil tabung terjual dari Laporan Penjualan
TABUNG_TERJUAL_PATTERNS = [
    r"Total Tabung LPG 3 Kg Terjual\s*\n?\s*(\d+)\s*Tabung",
    r"Total Tabung LPG 3 Kg Terjual[^\d]*(\d+)\s*Tabung",
]

# ============================================
# ERROR MESSAGES
# ============================================

ERROR_LOGIN_FAILED = "Login gagal"
ERROR_NAVIGATION_FAILED = "Navigasi gagal"
ERROR_DATA_EXTRACTION_FAILED = "Gagal mengambil data"
ERROR_EXCEL_SAVE_FAILED = "Gagal menyimpan ke Excel"

# ============================================
# SUCCESS MESSAGES
# ============================================

SUCCESS_LOGIN = "Login berhasil"
SUCCESS_DATA_EXTRACTED = "Data berhasil diambil"
SUCCESS_EXCEL_SAVED = "Data berhasil disimpan ke Excel"

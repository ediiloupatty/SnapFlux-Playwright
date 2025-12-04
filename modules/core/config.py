"""
Configuration file untuk PlayWRight
File ini berisi konfigurasi default untuk Playwright automation
"""

import os

# ============================================
# BROWSER SETTINGS
# ============================================

# Headless Mode
# True = Browser tidak terlihat (lebih cepat, cocok untuk production)
# False = Browser terlihat (cocok untuk debugging)
HEADLESS_MODE = True

# Browser Timeout Settings (dalam milliseconds)
DEFAULT_TIMEOUT = 20000  # 20 deti
NAVIGATION_TIMEOUT = 20000  # 20 detik
ACTION_TIMEOUT = 10000  # 10 detik

# ============================================
# PERFORMANCE SETTINGS
# ============================================

# Delay antar akun (dalam detik)
INTER_ACCOUNT_DELAY = 2.0

# Delay setelah login (dalam detik)
POST_LOGIN_DELAY = 1.5

# Delay setelah navigasi (dalam detik)
POST_NAVIGATION_DELAY = 1.0

# ============================================
# RETRY SETTINGS
# ============================================

# Maksimal retry untuk operasi yang gagal
MAX_RETRIES = 3

# Delay antar retry (dalam detik)
RETRY_DELAY = 2.0

# Timeout untuk "Gagal Masuk Akun" (dalam detik)
GAGAL_MASUK_AKUN_TIMEOUT = 120

# ============================================
# LOGGING SETTINGS
# ============================================

# Level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Log file path (relative to project root)
LOG_FILE = "logs/playwright_automation.log"

# Log rotation settings
LOG_MAX_BYTES = 2 * 1024 * 1024  # 2MB
LOG_BACKUP_COUNT = 3

# ============================================
# BROWSER BINARY PATHS
# ============================================

# Custom Chrome binary path (None untuk menggunakan default Chromium)
CHROME_BINARY_PATH = None

# Contoh custom path (uncomment untuk menggunakan):
# CHROME_BINARY_PATH = r"D:\edi\Programing\Snapflux v2\chrome\Chromium\bin\chrome.exe"

# ============================================
# ENVIRONMENT DETECTION
# ============================================

# Auto-detect Docker environment
AUTO_DETECT_DOCKER = True

# Force Docker mode (jika True, akan selalu menggunakan setting Docker)
FORCE_DOCKER_MODE = False

# ============================================
# SCREENSHOT SETTINGS
# ============================================

# Ambil screenshot saat error
SCREENSHOT_ON_ERROR = True

# Path untuk menyimpan screenshot
SCREENSHOT_PATH = "logs/screenshots"

# Format screenshot (png, jpeg)
SCREENSHOT_FORMAT = "png"

# ============================================
# DATA EXTRACTION SETTINGS
# ============================================

# Minimum jumlah tabung untuk filter customer list
MIN_TABUNG_FILTER = 2

# Timeout untuk wait data load (dalam milliseconds)
DATA_LOAD_TIMEOUT = 10000

# ============================================
# EXCEL SETTINGS
# ============================================

# Path untuk menyimpan hasil Excel (relative to project root)
EXCEL_OUTPUT_PATH = "results"

# Format nama file Excel
EXCEL_FILENAME_FORMAT = "DATA_SNAPFLUX_MASTER_{year}_{month}.xlsx"

# ============================================
# HELPER FUNCTIONS
# ============================================


def get_config(key, default=None):
    """
    Get configuration value by key

    Args:
        key (str): Configuration key name
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    return globals().get(key, default)


def set_config(key, value):
    """
    Set configuration value

    Args:
        key (str): Configuration key name
        value: Value to set
    """
    globals()[key] = value


def is_headless_mode():
    """
    Check if headless mode is enabled

    Returns:
        bool: True if headless, False otherwise
    """
    # Check environment variable first
    env_headless = os.environ.get("PLAYWRIGHT_HEADLESS", "").lower()
    if env_headless in ["true", "1", "yes"]:
        return True
    elif env_headless in ["false", "0", "no"]:
        return False

    # Return config value
    return HEADLESS_MODE


def get_chrome_binary():
    """
    Get Chrome binary path

    Returns:
        str or None: Chrome binary path
    """
    # Check environment variable first
    env_chrome = os.environ.get("CHROME_BINARY_PATH", "")
    if env_chrome and os.path.exists(env_chrome):
        return env_chrome

    # Return config value
    return CHROME_BINARY_PATH


# ============================================
# CONFIGURATION PRESETS
# ============================================

# Fast Mode (untuk production, prioritas kecepatan)
FAST_MODE_CONFIG = {
    "HEADLESS_MODE": True,
    "DEFAULT_TIMEOUT": 15000,
    "NAVIGATION_TIMEOUT": 15000,
    "INTER_ACCOUNT_DELAY": 1.0,
    "POST_LOGIN_DELAY": 1.0,
    "POST_NAVIGATION_DELAY": 0.5,
}

# Debug Mode (untuk debugging, prioritas visibility)
DEBUG_MODE_CONFIG = {
    "HEADLESS_MODE": False,
    "DEFAULT_TIMEOUT": 30000,
    "NAVIGATION_TIMEOUT": 30000,
    "INTER_ACCOUNT_DELAY": 3.0,
    "POST_LOGIN_DELAY": 2.0,
    "POST_NAVIGATION_DELAY": 1.5,
    "SCREENSHOT_ON_ERROR": True,
}

# Production Mode (untuk production, balanced)
PRODUCTION_MODE_CONFIG = {
    "HEADLESS_MODE": True,
    "DEFAULT_TIMEOUT": 20000,
    "NAVIGATION_TIMEOUT": 20000,
    "INTER_ACCOUNT_DELAY": 2.0,
    "POST_LOGIN_DELAY": 1.5,
    "POST_NAVIGATION_DELAY": 1.0,
    "SCREENSHOT_ON_ERROR": True,
}


def apply_preset(preset_name):
    """
    Apply configuration preset

    Args:
        preset_name (str): Name of preset ('fast', 'debug', 'production')
    """
    presets = {
        "fast": FAST_MODE_CONFIG,
        "debug": DEBUG_MODE_CONFIG,
        "production": PRODUCTION_MODE_CONFIG,
    }

    preset = presets.get(preset_name.lower())
    if preset:
        for key, value in preset.items():
            set_config(key, value)
        print(f"✓ Applied {preset_name.upper()} preset")
    else:
        print(f"✗ Unknown preset: {preset_name}")


# ============================================
# USAGE EXAMPLES
# ============================================

"""
# Cara menggunakan config:

# 1. Import config
from PlayWRight.config import HEADLESS_MODE, get_config, set_config, is_headless_mode

# 2. Get config value
headless = is_headless_mode()
timeout = get_config('DEFAULT_TIMEOUT', 20000)

# 3. Set config value
set_config('HEADLESS_MODE', False)

# 4. Apply preset
from PlayWRight.config import apply_preset
apply_preset('debug')  # Untuk debugging
apply_preset('fast')   # Untuk kecepatan maksimal
apply_preset('production')  # Untuk production

# 5. Override via environment variable
# set PLAYWRIGHT_HEADLESS=false
# python main_playwright.py

# 6. Override via code
import PlayWRight.config as pw_config
pw_config.HEADLESS_MODE = False
"""

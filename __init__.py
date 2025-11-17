"""
PlayWRight Package - Playwright Implementation untuk SnapFlux
=============================================================

Package ini berisi implementasi lengkap automation SnapFlux menggunakan Playwright
sebagai alternatif dari Selenium dengan performa yang lebih baik.

Modules:
    - browser_setup: Setup dan konfigurasi Playwright browser
    - login_handler: Fungsi login dan authentication
    - data_extractor: Fungsi ekstraksi data (stok, penjualan, dll)
    - navigation_handler: Fungsi navigasi antar halaman
    - main_playwright: Main script untuk menjalankan automation

Usage:
    from PlayWRight.main_playwright import run_cek_stok_playwright
    from PlayWRight.browser_setup import PlaywrightBrowserManager

    # Setup browser
    manager = PlaywrightBrowserManager()
    page = manager.setup_browser(headless=True)

    # Atau jalankan full automation
    run_cek_stok_playwright(accounts, selected_date)

Features:
    - Auto-waiting untuk elements
    - Built-in retry mechanism
    - Better error handling
    - Faster execution (~25-33% faster than Selenium)
    - Modern API yang lebih mudah digunakan

Author: SnapFlux Development Team
Version: 2.0
License: Sesuai dengan license utama SnapFlux v2.0
"""

__version__ = "2.0.0"
__author__ = "SnapFlux Development Team"
__all__ = [
    "PlaywrightBrowserManager",
    "login_direct",
    "get_stock_value_direct",
    "get_tabung_terjual_direct",
    "click_laporan_penjualan_direct",
    "navigate_to_atur_produk",
    "run_cek_stok_playwright",
]

# Import main classes dan functions untuk kemudahan akses
try:
    from .browser_setup import PlaywrightBrowserManager
    from .data_extractor import (
        extract_transaction_data,
        get_customer_list_direct,
        get_stock_value_direct,
        get_tabung_terjual_direct,
    )
    from .login_handler import is_logged_in, login_direct, logout
    from .main_playwright import run_cek_stok_playwright
    from .navigation_handler import (
        click_catat_penjualan_direct,
        click_date_elements_direct,
        click_laporan_penjualan_direct,
        click_rekap_penjualan_direct,
        navigate_to_atur_produk,
    )
except ImportError as e:
    # Fallback jika ada dependency yang belum terinstall
    import warnings

    warnings.warn(
        f"Some PlayWRight modules could not be imported: {str(e)}. "
        "Make sure Playwright is installed: pip install playwright && python -m playwright install"
    )

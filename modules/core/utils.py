"""
Utility functions untuk PlayWRight (Standalone)
File ini berisi fungsi-fungsi bantuan yang diperlukan untuk automation Playwright
Tidak bergantung pada folder src
"""

import logging
import os
import queue
import re
import sys
import threading
import time
from collections import Counter
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pandas as pd

# Updated import for modular structure
from .validators import is_valid_email, is_valid_phone, is_valid_pin

# Setup logger
logger = logging.getLogger("playwright_automation")

# ============================================
# PATH CONFIGURATION
# ============================================

# Base directory untuk PlayWRight
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Direktori penting
AKUN_DIR = os.path.join(BASE_DIR, "akun")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "playwright_automation.log")

# Pastikan direktori ada
os.makedirs(AKUN_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ============================================
# LOGGING FUNCTIONS
# ============================================


def setup_logging():
    """
    Setup logging system untuk Playwright automation
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    logger.setLevel(logging.DEBUG)

    # Rotating file handler
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Hapus handler lama jika ada
    logger.handlers.clear()
    logger.addHandler(handler)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)


# ============================================
# ACCOUNT MANAGEMENT
# ============================================


def load_accounts_from_excel(filename):
    """
    Load data akun dari file Excel dengan validasi

    Args:
        filename (str): Path ke file Excel

    Returns:
        list: List tuple (nama, username, pin, pangkalan_id)
    """
    try:
        df = pd.read_excel(
            filename, dtype={"Nama": str, "Username": str, "Password": str, "Pangkalan_id": str}
        )

        valid_accounts = []

        for _, row in df.iterrows():
            nama = str(row["Nama"]).strip()
            username = str(row["Username"]).strip()
            pin = str(row["Password"]).strip()
            
            # Baca Pangkalan_id (bisa kosong untuk backward compatibility)
            pangkalan_id = str(row.get("Pangkalan_id", "")).strip()
            
            # Jika Pangkalan_id kosong, gunakan username sebagai fallback
            if not pangkalan_id or pangkalan_id == "nan":
                pangkalan_id = username
                logger.warning(f"Pangkalan_id tidak ditemukan untuk {nama}, menggunakan username sebagai ID")

            # Validasi username
            if not (is_valid_email(username) or is_valid_phone(username)):
                logger.warning(f"Invalid username: {username}")
                continue

            # Validasi PIN
            if not is_valid_pin(pin):
                logger.warning(f"Invalid PIN for {username}")
                continue

            valid_accounts.append((nama, username, pin, pangkalan_id))

        if not valid_accounts:
            raise ValueError("No valid accounts found in Excel file!")

        return valid_accounts

    except Exception as e:
        logger.error(f"Error loading accounts: {str(e)}")
        raise


def print_account_stats(accounts):
    """
    Print statistik akun

    Args:
        accounts (list): List akun
    """
    usernames = [acc[1] for acc in accounts]
    total = len(usernames)
    unique = len(set(usernames))

    print(f"\nTotal akun: {total}")
    print(f"Akun unik: {unique}")

    if total != unique:
        dupe = [u for u, c in Counter(usernames).items() if c > 1]
        print(f"Username duplikat: {dupe}")
    else:
        print("Tidak ada username yang duplikat.")


# ============================================
# INPUT FUNCTIONS
# ============================================


def input_with_timeout(prompt, timeout):
    """
    Input dengan timeout

    Args:
        prompt (str): Prompt untuk input
        timeout (int): Timeout dalam detik

    Returns:
        str: Input dari user atau empty string jika timeout
    """
    q = queue.Queue()

    def inner():
        try:
            q.put(input(prompt))
        except Exception:
            q.put("")

    thread = threading.Thread(target=inner)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return ""
    else:
        try:
            return q.get_nowait()
        except queue.Empty:
            return ""


def get_date_input():
    """
    Minta input tanggal dari user dengan validasi

    Returns:
        datetime: Tanggal yang dipilih atau None jika skip
    """
    while True:
        try:
            print("\n📅 === FILTER TANGGAL LAPORAN PENJUALAN ===")
            print("Masukkan tanggal yang ingin diambil datanya (format: DD/MM/YYYY)")
            print("Contoh: 19/07/2025")
            print("Atau tekan Enter tanpa input untuk LEWATI filter tanggal")
            print(
                "(Otomatis lewati filter tanggal jika tidak ada input dalam 15 detik)"
            )

            date_input = input_with_timeout("Tanggal: ", 15).strip()

            if not date_input:
                print("User tidak input tanggal - akan lewati fungsi klik tanggal")
                print("Data akan diambil tanpa filter tanggal spesifik")
                return None

            if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_input):
                print("✗ Format tanggal salah! Gunakan format DD/MM/YYYY")
                continue

            day, month, year = map(int, date_input.split("/"))

            if year < 2020 or year > 2030:
                print("✗ Tahun tidak valid! Gunakan tahun antara 2020-2030")
                continue
            if month < 1 or month > 12:
                print("✗ Bulan tidak valid!")
                continue
            if day < 1 or day > 31:
                print("✗ Hari tidak valid!")
                continue

            try:
                selected_date = datetime(year, month, day)
                print(
                    f"✓ Tanggal berhasil di-parse: {selected_date.strftime('%d %B %Y')}"
                )
                return selected_date
            except ValueError as ve:
                print(f"✗ Tanggal tidak valid! {str(ve)}")
                continue

        except Exception as e:
            print(f"✗ Error input tanggal: {str(e)}")
            return None


# ============================================
# SUMMARY FUNCTIONS
# ============================================


def print_final_summary(rekap, total_accounts, total_duration):
    """
    Print ringkasan akhir proses automation

    Args:
        rekap (dict): Dictionary rekap hasil
        total_accounts (int): Total akun yang diproses
        total_duration (float): Total durasi proses
    """
    print(f"\n{'=' * 60}")
    print("RINGKASAN AKHIR")
    print(f"{'=' * 60}")
    print(f"Total Akun: {total_accounts}")
    print(f"✓ Sukses: {len(rekap.get('sukses', []))} akun")
    print(f"✗ Gagal Login: {len(rekap.get('gagal_login', []))} akun")
    print(f"✗ Gagal Navigasi: {len(rekap.get('gagal_navigasi', []))} akun")
    print(f"Total Waktu: {total_duration:.2f} detik")

    if total_accounts > 0:
        avg_time = total_duration / total_accounts
        print(f"Rata-rata per Akun: {avg_time:.2f} detik")

    print(f"{'=' * 60}")


# ============================================
# HELPER FUNCTIONS
# ============================================


def get_main_menu_input():
    """
    Get input untuk main menu

    Returns:
        str: Pilihan menu
    """
    return input("Pilih menu: ").strip()


def format_duration(seconds):
    """
    Format durasi ke format yang mudah dibaca

    Args:
        seconds (float): Durasi dalam detik

    Returns:
        str: Durasi dalam format yang mudah dibaca
    """
    if seconds < 60:
        return f"{seconds:.2f} detik"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} menit"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} jam"

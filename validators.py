"""
Validators module untuk PlayWRight (Standalone)
File ini berisi fungsi-fungsi validasi yang diperlukan untuk automation Playwright
Tidak bergantung pada folder src
"""

import re


def is_valid_email(email):
    """
    Validasi format email

    Args:
        email (str): Email yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, str(email)) is not None


def is_valid_phone(phone):
    """
    Validasi format nomor HP Indonesia

    Args:
        phone (str): Nomor HP yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not phone:
        return False
    # Nomor HP Indonesia: 08xx atau 628xx, panjang 10-15 digit
    pattern = r"^(08|628)\d{8,13}$"
    return re.match(pattern, str(phone)) is not None


def is_valid_pin(pin):
    """
    Validasi format PIN

    Args:
        pin (str): PIN yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not pin:
        return False
    # PIN harus angka, panjang 4-8 digit
    pin_str = str(pin)
    return pin_str.isdigit() and 4 <= len(pin_str) <= 8


def parse_stok_to_int(stok_str):
    """
    Parse string stok ke integer
    Contoh: "89 Tabung" -> 89

    Args:
        stok_str (str): String stok yang akan di-parse

    Returns:
        int: Nilai stok dalam integer
    """
    if not stok_str:
        return 0

    try:
        # Jika sudah integer, return langsung
        if isinstance(stok_str, int):
            return stok_str

        # Extract angka dari string
        match = re.search(r"(\d+)", str(stok_str))
        if match:
            return int(match.group(1))

        return 0
    except Exception:
        return 0


def parse_inputan_to_int(inputan_str):
    """
    Parse string inputan ke integer
    Contoh: "12 Tabung" -> 12

    Args:
        inputan_str (str): String inputan yang akan di-parse

    Returns:
        int: Nilai inputan dalam integer
    """
    if not inputan_str:
        return 0

    try:
        # Jika sudah integer, return langsung
        if isinstance(inputan_str, int):
            return inputan_str

        # Extract angka dari string
        match = re.search(r"(\d+)", str(inputan_str))
        if match:
            return int(match.group(1))

        return 0
    except Exception:
        return 0


def validate_date_format(date_str):
    """
    Validasi format tanggal DD/MM/YYYY

    Args:
        date_str (str): String tanggal yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not date_str:
        return False

    pattern = r"^\d{2}/\d{2}/\d{4}$"
    return re.match(pattern, str(date_str)) is not None


def validate_date_range(day, month, year):
    """
    Validasi range tanggal

    Args:
        day (int): Hari (1-31)
        month (int): Bulan (1-12)
        year (int): Tahun (2020-2030)

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not all(isinstance(x, int) for x in [day, month, year]):
        return False

    if year < 2020 or year > 2030:
        return False
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False

    return True


def sanitize_string(text):
    """
    Sanitize string untuk keamanan dan konsistensi

    Args:
        text (str): Text yang akan di-sanitize

    Returns:
        str: Text yang sudah di-sanitize
    """
    if not text:
        return ""

    # Strip whitespace
    text = str(text).strip()

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


def validate_username(username):
    """
    Validasi username (harus email atau nomor HP)

    Args:
        username (str): Username yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not username:
        return False

    return is_valid_email(username) or is_valid_phone(username)


def validate_account_data(nama, username, pin):
    """
    Validasi data akun lengkap

    Args:
        nama (str): Nama pangkalan
        username (str): Username (email atau HP)
        pin (str): PIN

    Returns:
        tuple: (is_valid, error_message)
    """
    if not nama or not str(nama).strip():
        return False, "Nama tidak boleh kosong"

    if not validate_username(username):
        return False, "Username harus berupa email atau nomor HP yang valid"

    if not is_valid_pin(pin):
        return False, "PIN harus berupa angka 4-8 digit"

    return True, None


def clean_number_string(number_str):
    """
    Bersihkan string angka dari karakter non-digit

    Args:
        number_str (str): String angka

    Returns:
        str: String angka yang sudah dibersihkan
    """
    if not number_str:
        return "0"

    # Extract only digits
    digits = re.sub(r"\D", "", str(number_str))
    return digits if digits else "0"


def format_tabung(value):
    """
    Format nilai ke format "X Tabung"

    Args:
        value (int/str): Nilai yang akan di-format

    Returns:
        str: Format "X Tabung"
    """
    if isinstance(value, str):
        # Jika sudah format "X Tabung", return langsung
        if "tabung" in value.lower():
            return value
        # Parse ke int dulu
        value = parse_inputan_to_int(value)

    return f"{value} Tabung"


def format_currency(value):
    """
    Format nilai ke format currency Indonesia

    Args:
        value (int/float): Nilai yang akan di-format

    Returns:
        str: Format "Rp X.XXX"
    """
    try:
        value = float(value)
        return f"Rp{value:,.0f}".replace(",", ".")
    except Exception:
        return "Rp0"


def extract_number_from_text(text):
    """
    Extract semua angka dari text

    Args:
        text (str): Text yang akan di-extract

    Returns:
        list: List of integers
    """
    if not text:
        return []

    matches = re.findall(r"\d+", str(text))
    return [int(m) for m in matches]


def is_valid_nik(nik):
    """
    Validasi format NIK Indonesia (16 digit)

    Args:
        nik (str): NIK yang akan divalidasi

    Returns:
        bool: True jika valid, False jika tidak
    """
    if not nik:
        return False

    nik_str = str(nik)
    return nik_str.isdigit() and len(nik_str) == 16


def validate_excel_columns(df, required_columns):
    """
    Validasi kolom Excel yang diperlukan

    Args:
        df (DataFrame): DataFrame yang akan divalidasi
        required_columns (list): List kolom yang diperlukan

    Returns:
        tuple: (is_valid, missing_columns)
    """
    if df is None or df.empty:
        return False, required_columns

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return False, missing

    return True, []

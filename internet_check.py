"""
Simple Internet Connection Checker
Helper functions untuk check koneksi internet tanpa kompleksitas
"""

import logging
import socket
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Global state
_is_checking = False
_last_check_result = True
_last_check_time = 0
_check_cache_seconds = 5  # Cache hasil check selama 5 detik


def check_internet_simple(timeout: int = 3) -> bool:
    """
    Check koneksi internet dengan cara sederhana

    Args:
        timeout: Timeout untuk check (seconds)

    Returns:
        True jika ada koneksi, False jika tidak
    """
    global _last_check_result, _last_check_time

    # Return cached result jika baru di-check
    current_time = time.time()
    if current_time - _last_check_time < _check_cache_seconds:
        return _last_check_result

    # Test dengan socket ke Google DNS
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        _last_check_result = True
        _last_check_time = current_time
        return True
    except (socket.timeout, socket.error, OSError):
        pass

    # Fallback ke Cloudflare DNS
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("1.1.1.1", 53))
        _last_check_result = True
        _last_check_time = current_time
        return True
    except (socket.timeout, socket.error, OSError):
        _last_check_result = False
        _last_check_time = current_time
        return False


def check_internet_http(timeout: int = 5) -> bool:
    """
    Check koneksi internet dengan HTTP request
    Lebih reliable tapi lebih lambat

    Args:
        timeout: Timeout untuk request (seconds)

    Returns:
        True jika ada koneksi, False jika tidak
    """
    try:
        response = requests.get("https://www.google.com", timeout=timeout)
        return response.status_code in [200, 301, 302]
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        return False


def wait_for_internet(
    timeout: int = 300, check_interval: int = 5, log_callback: Optional[callable] = None
) -> bool:
    """
    Wait sampai koneksi internet tersedia atau timeout

    Args:
        timeout: Maximum waktu tunggu (seconds)
        check_interval: Interval check (seconds)
        log_callback: Callback function untuk log (msg, level)

    Returns:
        True jika koneksi tersedia, False jika timeout
    """
    start_time = time.time()
    attempts = 0

    if log_callback:
        log_callback("⏳ Menunggu koneksi internet...", "warning")
    else:
        logger.warning("Waiting for internet connection...")

    while (time.time() - start_time) < timeout:
        attempts += 1

        if check_internet_simple(timeout=3):
            elapsed = time.time() - start_time
            if log_callback:
                log_callback(
                    f"✅ Koneksi internet kembali setelah {elapsed:.1f} detik ({attempts} percobaan)",
                    "success",
                )
            else:
                logger.info(f"Internet connection restored after {elapsed:.1f} seconds")
            return True

        # Log progress setiap 30 detik
        elapsed = time.time() - start_time
        if attempts % 6 == 0:  # 6 x 5 seconds = 30 seconds
            if log_callback:
                log_callback(
                    f"⏳ Masih menunggu koneksi... ({elapsed:.0f}/{timeout}s)",
                    "warning",
                )

        time.sleep(check_interval)

    # Timeout
    if log_callback:
        log_callback(f"❌ Timeout menunggu koneksi internet ({timeout}s)", "error")
    else:
        logger.error(f"Timeout waiting for internet connection ({timeout}s)")

    return False


def check_before_step(
    step_name: str,
    username: str = "",
    max_wait: int = 300,
    log_callback: Optional[callable] = None,
) -> bool:
    """
    Check internet sebelum melakukan step tertentu
    Jika tidak ada koneksi, tunggu sampai ada atau timeout

    Args:
        step_name: Nama step (e.g., "login", "get_stock")
        username: Username yang sedang diproses (untuk log)
        max_wait: Maximum waktu tunggu (seconds)
        log_callback: Callback function untuk log (msg, level)

    Returns:
        True jika koneksi OK, False jika timeout
    """
    if not check_internet_simple():
        user_info = f"untuk {username} " if username else ""

        if log_callback:
            log_callback(
                f"⚠️ Koneksi terputus sebelum {step_name} {user_info}", "warning"
            )
        else:
            logger.warning(f"Connection lost before {step_name} for {username}")

        # Wait for connection
        return wait_for_internet(timeout=max_wait, log_callback=log_callback)

    return True


def wrap_with_internet_check(func):
    """
    Decorator untuk wrap function dengan internet check

    Usage:
        @wrap_with_internet_check
        def my_function():
            # your code
            pass
    """

    def wrapper(*args, **kwargs):
        if not check_internet_simple():
            logger.warning(f"No internet connection before executing {func.__name__}")
            if not wait_for_internet(timeout=60):
                logger.error(f"Timeout waiting for internet before {func.__name__}")
                return None

        return func(*args, **kwargs)

    return wrapper


# Convenience functions
def is_online() -> bool:
    """Quick check jika online"""
    return check_internet_simple(timeout=2)


def ensure_online(timeout: int = 60, log_callback: Optional[callable] = None) -> bool:
    """Pastikan online atau tunggu sampai online"""
    if is_online():
        return True
    return wait_for_internet(timeout=timeout, log_callback=log_callback)


# Testing
if __name__ == "__main__":
    print("Testing Internet Check Module...")

    print("\n1. Simple check:")
    result = check_internet_simple()
    print(f"   Connected: {result}")

    print("\n2. HTTP check:")
    result = check_internet_http()
    print(f"   Connected: {result}")

    print("\n3. Quick online check:")
    result = is_online()
    print(f"   Online: {result}")

    print("\n4. Testing wait (will timeout quickly for demo):")

    def dummy_log(msg, level):
        print(f"   [{level.upper()}] {msg}")

    result = wait_for_internet(timeout=10, check_interval=2, log_callback=dummy_log)
    print(f"   Result: {result}")

    print("\n5. Check before step:")
    result = check_before_step(
        "test_operation", "test_user", max_wait=5, log_callback=dummy_log
    )
    print(f"   Result: {result}")

    print("\nTest completed!")

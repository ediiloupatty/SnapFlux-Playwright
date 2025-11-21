"""
Script untuk install dan setup Playwright untuk SnapFlux v2.0
Otomatis menginstall Playwright dan browser Chromium yang diperlukan
"""

import os
import subprocess
import sys


def print_header():
    """Cetak header yang menarik"""
    print("=" * 60)
    print("  PLAYWRIGHT INSTALLATION SCRIPT")
    print("  SnapFlux v2.0 - Automation Tool")
    print("=" * 60)
    print()


def check_python_version():
    """Cek versi Python"""
    print("Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Error: Python 3.8 atau lebih baru diperlukan!")
        print("   Silakan upgrade Python Anda.")
        return False

    print("✓ Python version OK")
    print()
    return True


def check_pip():
    """Cek apakah pip tersedia"""
    print("Checking pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"   {result.stdout.strip()}")
        print("✓ pip is available")
        print()
        return True
    except subprocess.CalledProcessError:
        print("✗ Error: pip tidak ditemukan!")
        return False


def install_playwright():
    """Install Playwright package"""
    print("Installing Playwright package...")
    print("   This may take a few minutes...")
    print()

    try:
        # Install playwright
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright>=1.40.0"], check=True
        )

        print()
        print("✓ Playwright package installed successfully!")
        print()
        return True

    except subprocess.CalledProcessError as e:
        print()
        print(f"✗ Error installing Playwright: {e}")
        return False


def install_browsers():
    """Install browser Chromium untuk Playwright"""
    print("Installing Chromium browser...")
    print("   This will download Chromium (~170MB)...")
    print()

    try:
        # Install chromium browser
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=True
        )

        print()
        print("✓ Chromium browser installed successfully!")
        print()
        return True

    except subprocess.CalledProcessError as e:
        print()
        print(f"✗ Error installing Chromium: {e}")
        return False


def verify_installation():
    """Verifikasi instalasi Playwright"""
    print("Verifying Playwright installation...")

    try:
        # Coba import playwright
        import playwright

        print(f"✓ Playwright module can be imported")
        print(
            f"   Version: {playwright.__version__ if hasattr(playwright, '__version__') else 'Unknown'}"
        )

        # Coba import sync_api
        from playwright.sync_api import sync_playwright

        print("✓ Playwright sync_api available")

        print()
        print("Installation verified successfully!")
        print()
        return True

    except ImportError as e:
        print(f"✗ Error verifying installation: {e}")
        print()
        return False


def print_next_steps():
    """Cetak langkah selanjutnya"""
    print("=" * 60)
    print("  INSTALLATION COMPLETE!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print()
    print("1. Run the Playwright version using:")
    print("   python PlayWRight\\main_playwright.py")
    print()
    print("   Or double-click:")
    print("   SnapFlux_Playwright.bat")
    print()
    print("2. The script will use Playwright instead of Selenium")
    print("   for better performance and stability")
    print()
    print("3. Check logs/automation.log for any issues")
    print()
    print("=" * 60)
    print()


def print_failure():
    """Cetak pesan kegagalan"""
    print()
    print("=" * 60)
    print("  INSTALLATION FAILED!")
    print("=" * 60)
    print()
    print("Playwright installation incomplete.")
    print()
    print("Manual Installation:")
    print()
    print("1. Install Playwright package:")
    print("   pip install playwright")
    print()
    print("2. Install browser:")
    print("   python -m playwright install chromium")
    print()
    print("3. Verify installation:")
    print("   python -c \"import playwright; print('OK')\"")
    print()
    print("=" * 60)
    print()


def main():
    """Main function"""
    print_header()

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    if not check_pip():
        print("Please install pip first:")
        print("python -m ensurepip --default-pip")
        sys.exit(1)

    # Ask for confirmation
    print("This script will install:")
    print("  • Playwright package (~5MB)")
    print("  • Chromium browser (~170MB)")
    print()

    try:
        response = input("Continue? (Y/n): ").strip().lower()
        if response and response not in ["y", "yes"]:
            print()
            print("Installation cancelled by user.")
            sys.exit(0)
    except KeyboardInterrupt:
        print()
        print("\nInstallation cancelled by user.")
        sys.exit(0)

    print()
    print("=" * 60)
    print("  STARTING INSTALLATION")
    print("=" * 60)
    print()

    # Install Playwright package
    if not install_playwright():
        print_failure()
        sys.exit(1)

    # Install Chromium browser
    if not install_browsers():
        print_failure()
        sys.exit(1)

    # Verify installation
    if not verify_installation():
        print_failure()
        sys.exit(1)

    # Success!
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("\n⚠ Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

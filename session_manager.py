"""
Session Manager untuk SnapFlux Automation
Handle save/load browser session state untuk reuse login dan efficiency
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.sync_api import BrowserContext, Page

# Setup logger
logger = logging.getLogger("session_manager")


class SessionManager:
    """
    Manage browser session state untuk multiple accounts
    - Save session state per account
    - Load session state untuk skip login
    - Validate session masih valid
    - Clear expired sessions
    """

    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize SessionManager

        Args:
            sessions_dir (str): Directory untuk menyimpan session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)

        # Session validity duration (default: 7 hari)
        self.session_validity_days = 7

        logger.info(f"SessionManager initialized with dir: {self.sessions_dir}")

    def _get_session_path(self, username: str) -> Path:
        """
        Get path untuk session file berdasarkan username

        Args:
            username (str): Username akun

        Returns:
            Path: Path ke session file
        """
        # Sanitize username untuk filename
        safe_username = "".join(c for c in username if c.isalnum() or c in "._-@")
        return self.sessions_dir / f"session_{safe_username}.json"

    def _get_metadata_path(self, username: str) -> Path:
        """
        Get path untuk metadata file

        Args:
            username (str): Username akun

        Returns:
            Path: Path ke metadata file
        """
        safe_username = "".join(c for c in username if c.isalnum() or c in "._-@")
        return self.sessions_dir / f"meta_{safe_username}.json"

    def save_session(self, context: BrowserContext, username: str) -> bool:
        """
        Save browser session state untuk akun

        Args:
            context (BrowserContext): Browser context yang akan disimpan
            username (str): Username akun

        Returns:
            bool: True jika berhasil save
        """
        try:
            session_path = self._get_session_path(username)
            meta_path = self._get_metadata_path(username)

            # Save storage state (cookies, localStorage, sessionStorage)
            context.storage_state(path=str(session_path))

            # Save metadata (timestamp, validity, etc)
            metadata = {
                "username": username,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (
                    datetime.now() + timedelta(days=self.session_validity_days)
                ).isoformat(),
                "version": "1.0",
            }

            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✓ Session saved for {username}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to save session for {username}: {str(e)}")
            return False

    def load_session(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Load session state untuk akun jika masih valid

        Args:
            username (str): Username akun

        Returns:
            Optional[Dict]: Session state dict atau None jika tidak valid
        """
        try:
            session_path = self._get_session_path(username)
            meta_path = self._get_metadata_path(username)

            # Check if session files exist
            if not session_path.exists() or not meta_path.exists():
                logger.info(f"No session found for {username}")
                return None

            # Load metadata
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Check if session expired
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"Session expired for {username}")
                self.clear_session(username)
                return None

            # Load session state
            with open(session_path, "r", encoding="utf-8") as f:
                session_state = json.load(f)

            logger.info(f"✓ Session loaded for {username}")
            return session_state

        except Exception as e:
            logger.error(f"✗ Failed to load session for {username}: {str(e)}")
            return None

    def has_valid_session(self, username: str) -> bool:
        """
        Check apakah ada valid session untuk akun

        Args:
            username (str): Username akun

        Returns:
            bool: True jika ada valid session
        """
        return self.load_session(username) is not None

    def clear_session(self, username: str) -> bool:
        """
        Clear/hapus session untuk akun

        Args:
            username (str): Username akun

        Returns:
            bool: True jika berhasil clear
        """
        try:
            session_path = self._get_session_path(username)
            meta_path = self._get_metadata_path(username)

            # Remove files if exist
            if session_path.exists():
                session_path.unlink()
            if meta_path.exists():
                meta_path.unlink()

            logger.info(f"✓ Session cleared for {username}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to clear session for {username}: {str(e)}")
            return False

    def clear_all_sessions(self) -> int:
        """
        Clear semua sessions

        Returns:
            int: Jumlah session yang dihapus
        """
        count = 0
        try:
            for file in self.sessions_dir.glob("session_*.json"):
                file.unlink()
                count += 1
            for file in self.sessions_dir.glob("meta_*.json"):
                file.unlink()

            logger.info(f"✓ Cleared {count} sessions")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to clear all sessions: {str(e)}")
            return count

    def clear_expired_sessions(self) -> int:
        """
        Clear hanya session yang sudah expired

        Returns:
            int: Jumlah session yang dihapus
        """
        count = 0
        try:
            for meta_file in self.sessions_dir.glob("meta_*.json"):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    expires_at = datetime.fromisoformat(metadata["expires_at"])
                    if datetime.now() > expires_at:
                        username = metadata["username"]
                        if self.clear_session(username):
                            count += 1

                except Exception as e:
                    logger.warning(f"Error checking {meta_file}: {str(e)}")
                    continue

            logger.info(f"✓ Cleared {count} expired sessions")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to clear expired sessions: {str(e)}")
            return count

    def get_session_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get informasi tentang session

        Args:
            username (str): Username akun

        Returns:
            Optional[Dict]: Info session atau None
        """
        try:
            meta_path = self._get_metadata_path(username)

            if not meta_path.exists():
                return None

            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Calculate remaining time
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            saved_at = datetime.fromisoformat(metadata["saved_at"])
            remaining = expires_at - datetime.now()

            return {
                "username": username,
                "saved_at": saved_at,
                "expires_at": expires_at,
                "is_valid": datetime.now() < expires_at,
                "remaining_days": remaining.days,
                "remaining_hours": remaining.seconds // 3600,
            }

        except Exception as e:
            logger.error(f"✗ Failed to get session info for {username}: {str(e)}")
            return None

    def list_all_sessions(self) -> list:
        """
        List semua sessions yang tersimpan

        Returns:
            list: List of session info dicts
        """
        sessions = []
        try:
            for meta_file in self.sessions_dir.glob("meta_*.json"):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    username = metadata["username"]
                    info = self.get_session_info(username)
                    if info:
                        sessions.append(info)

                except Exception as e:
                    logger.warning(f"Error reading {meta_file}: {str(e)}")
                    continue

            return sessions

        except Exception as e:
            logger.error(f"✗ Failed to list sessions: {str(e)}")
            return []

    def validate_session(self, page: Page, username: str) -> bool:
        """
        Validate apakah session masih bekerja dengan check login status

        Args:
            page (Page): Browser page
            username (str): Username akun

        Returns:
            bool: True jika session valid dan masih logged in
        """
        try:
            # Try to check if user is logged in
            # This is application-specific, adjust based on your app

            # Example: Check for logout button or user info
            page.wait_for_timeout(1000)

            # Check if we're on login page (means session invalid)
            if "login" in page.url.lower():
                logger.warning(f"Session invalid for {username} - on login page")
                return False

            # Additional checks dapat ditambahkan sesuai aplikasi
            logger.info(f"✓ Session validated for {username}")
            return True

        except Exception as e:
            logger.error(f"✗ Session validation failed for {username}: {str(e)}")
            return False

    def set_validity_days(self, days: int):
        """
        Set durasi validity untuk session baru

        Args:
            days (int): Jumlah hari session valid
        """
        self.session_validity_days = days
        logger.info(f"Session validity set to {days} days")

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics tentang sessions

        Returns:
            Dict: Statistics dict
        """
        try:
            all_sessions = self.list_all_sessions()
            valid_sessions = [s for s in all_sessions if s["is_valid"]]
            expired_sessions = [s for s in all_sessions if not s["is_valid"]]

            return {
                "total": len(all_sessions),
                "valid": len(valid_sessions),
                "expired": len(expired_sessions),
            }

        except Exception as e:
            logger.error(f"✗ Failed to get stats: {str(e)}")
            return {"total": 0, "valid": 0, "expired": 0}


# Singleton instance
_session_manager = None


def get_session_manager(sessions_dir: str = "sessions") -> SessionManager:
    """
    Get singleton instance of SessionManager

    Args:
        sessions_dir (str): Directory untuk sessions

    Returns:
        SessionManager: Singleton instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(sessions_dir)
    return _session_manager

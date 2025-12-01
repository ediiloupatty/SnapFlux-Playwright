"""
Telemetry Manager untuk SnapFlux Automation
Monitoring metrics, performance tracking, dan analytics minimal tapi standar industri
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logger
logger = logging.getLogger("telemetry")


class TelemetryManager:
    """
    Lightweight telemetry system untuk monitoring automation
    - Track success/failure rates
    - Performance metrics
    - Error tracking
    - Real-time statistics
    """

    def __init__(self, metrics_dir: str = "metrics"):
        """
        Initialize TelemetryManager

        Args:
            metrics_dir (str): Directory untuk menyimpan metrics
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)

        # Current session metrics
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")

        # Counters
        self.total_accounts = 0
        self.successful_accounts = 0
        self.failed_accounts = 0
        self.skipped_accounts = 0

        # Detailed tracking
        self.account_timings = []  # List of processing times
        self.errors = defaultdict(int)  # Error type counts
        self.accounts_processed = []  # Detailed account info

        # Business Metrics
        self.total_stok_terpantau = 0
        self.total_penjualan_unit = 0

        # Performance metrics
        self.start_times = {}  # Track operation start times
        self.operation_durations = defaultdict(list)  # Operation timings

        logger.info(f"TelemetryManager initialized - Session: {self.session_id}")

    def start_operation(self, operation_name: str, identifier: str = None):
        """
        Mark start of an operation untuk timing

        Args:
            operation_name (str): Name of operation (e.g., 'login', 'data_extraction')
            identifier (str): Unique identifier (e.g., username)
        """
        key = f"{operation_name}:{identifier}" if identifier else operation_name
        self.start_times[key] = time.time()

    def end_operation(self, operation_name: str, identifier: str = None) -> float:
        """
        Mark end of operation dan calculate duration

        Args:
            operation_name (str): Name of operation
            identifier (str): Unique identifier

        Returns:
            float: Duration in seconds
        """
        key = f"{operation_name}:{identifier}" if identifier else operation_name
        if key in self.start_times:
            duration = time.time() - self.start_times[key]
            self.operation_durations[operation_name].append(duration)
            del self.start_times[key]
            return duration
        return 0.0

    def record_account_start(self, username: str):
        """
        Record start of account processing

        Args:
            username (str): Account username
        """
        self.total_accounts += 1
        self.start_operation("account_processing", username)

    def record_account_success(self, username: str, data: Dict[str, Any] = None):
        """
        Record successful account processing

        Args:
            username (str): Account username
            data (Dict): Additional data about the account
        """
        self.successful_accounts += 1
        duration = self.end_operation("account_processing", username)
        self.account_timings.append(duration)

        self.accounts_processed.append(
            {
                "username": username,
                "status": "success",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "data": data or {},
            }
        )

        logger.info(f"✓ Account success: {username} ({duration:.2f}s)")

    def record_account_failure(
        self, username: str, error_type: str, error_message: str = None, nama: str = None
    ):
        """
        Record failed account processing

        Args:
            username (str): Account username
            error_type (str): Type of error (e.g., 'login_failed', 'timeout')
            error_message (str): Detailed error message
            nama (str): Account name/display name
        """
        self.failed_accounts += 1
        duration = self.end_operation("account_processing", username)
        self.errors[error_type] += 1

        self.accounts_processed.append(
            {
                "username": username,
                "nama": nama or username,
                "status": "failed",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "error_type": error_type,
                "error_message": error_message,
            }
        )

        logger.warning(f"✗ Account failed: {nama or username} - {error_type}")

    def record_account_skip(self, username: str, reason: str = None):
        """
        Record skipped account

        Args:
            username (str): Account username
            reason (str): Reason for skip
        """
        self.skipped_accounts += 1

        self.accounts_processed.append(
            {
                "username": username,
                "status": "skipped",
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
            }
        )

        logger.info(f"Account skipped: {username}")

    def record_business_metrics(self, stok: int, penjualan: int):
        """
        Record business metrics (stok dan penjualan)
        
        Args:
            stok (int): Jumlah stok awal
            penjualan (int): Jumlah tabung terjual
        """
        if stok > 0:
            self.total_stok_terpantau += stok
        if penjualan > 0:
            self.total_penjualan_unit += penjualan

    def get_success_rate(self) -> float:
        """
        Calculate success rate

        Returns:
            float: Success rate percentage (0-100)
        """
        total = self.total_accounts
        if total == 0:
            return 0.0
        return (self.successful_accounts / total) * 100

    def get_failure_rate(self) -> float:
        """
        Calculate failure rate

        Returns:
            float: Failure rate percentage (0-100)
        """
        total = self.total_accounts
        if total == 0:
            return 0.0
        return (self.failed_accounts / total) * 100

    def get_average_processing_time(self) -> float:
        """
        Get average processing time per account

        Returns:
            float: Average time in seconds
        """
        if not self.account_timings:
            return 0.0
        return sum(self.account_timings) / len(self.account_timings)

    def get_total_duration(self) -> float:
        """
        Get total session duration

        Returns:
            float: Duration in seconds
        """
        return (datetime.now() - self.session_start).total_seconds()

    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """
        Get statistics for specific operation

        Args:
            operation_name (str): Name of operation

        Returns:
            Dict: Stats including avg, min, max, total
        """
        durations = self.operation_durations.get(operation_name, [])
        if not durations:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "total": 0.0}

        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations),
        }

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics untuk dashboard

        Returns:
            Dict: Current metrics
        """
        # Get failed accounts with details
        failed_accounts_detail = [
            {
                "nama": acc.get("nama", acc.get("username", "Unknown")),
                "username": acc.get("username", ""),
                "error_type": acc.get("error_type", "unknown"),
                "error_message": acc.get("error_message", "")
            }
            for acc in self.accounts_processed
            if acc.get("status") == "failed"
        ]
        
        return {
            "session_id": self.session_id,
            "session_duration": self.get_total_duration(),
            "total_accounts": self.total_accounts,
            "successful": self.successful_accounts,
            "failed": self.failed_accounts,
            "skipped": self.skipped_accounts,
            "success_rate": round(self.get_success_rate(), 2),
            "failure_rate": round(self.get_failure_rate(), 2),
            "avg_processing_time": round(self.get_average_processing_time(), 2),
            "errors": dict(self.errors),
            "failed_accounts_detail": failed_accounts_detail,  # NEW
            "business_metrics": {
                "total_stok": self.total_stok_terpantau,
                "total_penjualan": self.total_penjualan_unit
            },
            "timestamp": datetime.now().isoformat(),
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive data untuk dashboard display

        Returns:
            Dict: Dashboard data
        """
        total_duration = self.get_total_duration()
        avg_time = self.get_average_processing_time()

        # Calculate throughput (accounts per minute)
        throughput = 0.0
        if total_duration > 0:
            throughput = (self.total_accounts / total_duration) * 60

        # Top errors
        top_errors = sorted(self.errors.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "overview": {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "session_duration_seconds": round(total_duration, 2),
                "session_duration_formatted": self._format_duration(total_duration),
            },
            "counters": {
                "total": self.total_accounts,
                "successful": self.successful_accounts,
                "failed": self.failed_accounts,
                "skipped": self.skipped_accounts,
            },
            "business": {
                "total_stok": self.total_stok_terpantau,
                "total_penjualan": self.total_penjualan_unit
            },
            "rates": {
                "success_rate": round(self.get_success_rate(), 2),
                "failure_rate": round(self.get_failure_rate(), 2),
            },
            "performance": {
                "avg_processing_time": round(avg_time, 2),
                "min_processing_time": round(min(self.account_timings), 2)
                if self.account_timings
                else 0,
                "max_processing_time": round(max(self.account_timings), 2)
                if self.account_timings
                else 0,
                "throughput_per_minute": round(throughput, 2),
            },
            "errors": {
                "total_errors": sum(self.errors.values()),
                "unique_error_types": len(self.errors),
                "top_errors": [
                    {"type": error_type, "count": count}
                    for error_type, count in top_errors
                ],
            },
        }

    def save_session_report(self, filename: str = None) -> str:
        """
        Save detailed session report to JSON file

        Args:
            filename (str): Custom filename (optional)

        Returns:
            str: Path to saved report
        """
        if filename is None:
            filename = f"report_{self.session_id}.json"

        report_path = self.metrics_dir / filename

        report = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_duration": self.get_total_duration(),
            },
            "summary": self.get_real_time_metrics(),
            "dashboard": self.get_dashboard_data(),
            "detailed_accounts": self.accounts_processed,
            "operation_stats": {
                op: self.get_operation_stats(op)
                for op in self.operation_durations.keys()
            },
        }

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Session report saved: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"✗ Failed to save report: {str(e)}")
            return ""

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration ke human-readable format

        Args:
            seconds (float): Duration in seconds

        Returns:
            str: Formatted duration
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def reset(self):
        """
        Reset semua metrics untuk session baru
        """
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")

        self.total_accounts = 0
        self.successful_accounts = 0
        self.failed_accounts = 0
        self.skipped_accounts = 0

        self.account_timings = []
        self.errors = defaultdict(int)
        self.accounts_processed = []
        self.start_times = {}
        self.accounts_processed = []
        self.start_times = {}
        self.operation_durations = defaultdict(list)
        
        self.total_stok_terpantau = 0
        self.total_penjualan_unit = 0

        logger.info(f"TelemetryManager reset - New session: {self.session_id}")


# Singleton instance
_telemetry_manager = None


def get_telemetry_manager(metrics_dir: str = "metrics") -> TelemetryManager:
    """
    Get singleton instance of TelemetryManager

    Args:
        metrics_dir (str): Directory untuk metrics

    Returns:
        TelemetryManager: Singleton instance
    """
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager(metrics_dir)
    return _telemetry_manager

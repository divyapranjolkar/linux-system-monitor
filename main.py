
import argparse
import json
import platform
import time

from pathlib import Path
from datetime import datetime

from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.disk import get_disk_info
from modules.processes import get_process_info
from modules.network import get_network_info

from utils.logger import setup_logger
from utils.reports import save_report


# Absolute path to the project directory.
BASE_DIR = Path(__file__).resolve().parent


def load_config():
    """Load application configuration from JSON."""

    config_file = BASE_DIR / "config" / "settings.json"

    with config_file.open("r", encoding="utf-8") as file:
        config = json.load(file)

    # Make the log file path independent of the terminal's
    # current working directory.
    log_path = Path(config["logging"]["file"])

    if not log_path.is_absolute():
        config["logging"]["file"] = str(BASE_DIR / log_path)

    return config


def collect_system_data(config):
    """Collect information from all monitoring modules."""

    return {
        "timestamp": datetime.now().astimezone().isoformat(),

        "system": {
            "hostname": platform.node(),
            "operating_system": platform.system(),
            "kernel": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        },

        "cpu": get_cpu_info(),

        "memory": get_memory_info(),

        "disk": get_disk_info(
            config["monitoring"]["disk_path"]
        ),

        "processes": get_process_info(),

        "network": get_network_info()
    }


def check_thresholds(data, config, logger):
    """Log warnings when resource usage reaches configured limits."""

    thresholds = config["thresholds"]

    checks = [
        (
            "CPU",
            data["cpu"]["usage_percent"],
            thresholds["cpu_percent"]
        ),
        (
            "Memory",
            data["memory"]["usage_percent"],
            thresholds["memory_percent"]
        ),
        (
            "Disk",
            data["disk"]["usage_percent"],
            thresholds["disk_percent"]
        )
    ]

    for name, usage, limit in checks:

        if usage >= limit:
            logger.warning(
                "%s usage is high: %.2f%% (threshold: %.2f%%)",
                name,
                usage,
                limit
            )

            print(
                f"WARNING: {name} usage is high: "
                f"{usage:.2f}%"
            )


def display_report(data):
    """Display collected information in the terminal."""

    print("\n" + "=" * 65)
    print("                 LINUX SYSTEM MONITOR")
    print("=" * 65)

    # SYSTEM INFORMATION
    print("\n[1] SYSTEM INFORMATION")

    print("Hostname:", data["system"]["hostname"])
    print("Operating System:", data["system"]["operating_system"])
    print("Kernel:", data["system"]["kernel"])
    print("Architecture:", data["system"]["architecture"])
    print("Python Version:", data["system"]["python_version"])

    # CPU INFORMATION
    print("\n[2] CPU INFORMATION")

    cpu = data["cpu"]

    print("Logical Cores:", cpu["logical_cores"])
    print("Physical Cores:", cpu["physical_cores"])
    print(f"CPU Usage: {cpu['usage_percent']:.2f}%")

    if cpu["frequency_mhz"] is not None:
        print(f"CPU Frequency: {cpu['frequency_mhz']:.2f} MHz")

    # MEMORY INFORMATION
    print("\n[3] MEMORY INFORMATION")

    memory = data["memory"]

    print("Total RAM:", memory["total_gb"], "GB")
    print("Used RAM:", memory["used_gb"], "GB")
    print("Available RAM:", memory["available_gb"], "GB")
    print(f"RAM Usage: {memory['usage_percent']:.2f}%")

    print("Total Swap:", memory["swap_total_gb"], "GB")
    print("Used Swap:", memory["swap_used_gb"], "GB")
    print(f"Swap Usage: {memory['swap_percent']:.2f}%")

    # DISK INFORMATION
    print("\n[4] DISK INFORMATION")

    disk = data["disk"]

    print("Filesystem Path:", disk["path"])
    print("Total Disk:", disk["total_gb"], "GB")
    print("Used Disk:", disk["used_gb"], "GB")
    print("Free Disk:", disk["free_gb"], "GB")
    print(f"Disk Usage: {disk['usage_percent']:.2f}%")

    # PROCESS INFORMATION
    print("\n[5] PROCESS INFORMATION")

    process_data = data["processes"]

    print("Total Processes:", process_data["total_processes"])
    print("\nTop Processes by Memory Usage:")

    print(
        f"{'PID':<10}"
        f"{'PROCESS NAME':<25}"
        f"{'MEMORY %':>12}"
    )

    print("-" * 47)

    for process in process_data["top_processes"]:

        print(
            f"{process['pid']:<10}"
            f"{process['name'][:24]:<25}"
            f"{process['memory_percent']:>11.2f}%"
        )

    # NETWORK INFORMATION
    print("\n[6] NETWORK INFORMATION")

    network = data["network"]

    print("Data Sent:", network["bytes_sent_mb"], "MB")
    print("Data Received:", network["bytes_received_mb"], "MB")
    print("Packets Sent:", network["packets_sent"])
    print("Packets Received:", network["packets_received"])
    print("Incoming Errors:", network["errors_in"])
    print("Outgoing Errors:", network["errors_out"])
    print("Incoming Dropped Packets:", network["dropped_in"])
    print("Outgoing Dropped Packets:", network["dropped_out"])

    print("\nGenerated:", data["timestamp"])

    print("\n" + "=" * 65)
    print("                 MONITORING COMPLETED")
    print("=" * 65)


def run_monitor(config, logger, save=True):
    """Execute one complete monitoring cycle."""

    logger.info("Starting monitoring cycle")

    data = collect_system_data(config)

    display_report(data)

    check_thresholds(data, config, logger)

    logger.info("Monitoring cycle completed")

    if save:
        report_directory = (
            BASE_DIR / config["reports"]["directory"]
        )

        report_file = save_report(
            data,
            report_directory
        )

        logger.info("Report saved: %s", report_file)

        print("\nReport saved:", report_file)

    return data


def main():

    parser = argparse.ArgumentParser(
        description="Linux System Monitor"
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run continuous monitoring"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Monitoring interval in seconds"
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Do not save a JSON report"
    )

    args = parser.parse_args()

    if args.interval is not None and args.interval < 1:
        parser.error("Interval must be at least 1 second")

    config = load_config()

    logger = setup_logger(config)

    interval = (
        args.interval
        if args.interval is not None
        else config["monitoring"]["interval_seconds"]
    )

    if not isinstance(interval, int) or isinstance(interval, bool) or interval < 1:
        parser.error("Configured monitoring interval must be a positive integer")

    logger.info("Linux System Monitor started")

    try:

        if args.watch:

            print("\nContinuous monitoring started.")
            print("Press Ctrl+C to stop.\n")

            while True:

                run_monitor(
                    config,
                    logger,
                    save=not args.no_report
                )

                print(f"\nNext monitoring cycle in {interval} seconds.")

                time.sleep(interval)

        else:

            run_monitor(
                config,
                logger,
                save=not args.no_report
            )

    except KeyboardInterrupt:

        print("\nMonitoring stopped by user.")

        logger.info("Monitoring stopped by user")

    except Exception:

        logger.exception("Monitoring application failed")

        raise


if __name__ == "__main__":
    main()


import psutil

from pathlib import Path


def get_process_info(limit=10):
    """Return process count and top processes by memory usage."""

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "username", "memory_percent", "cmdline"]
    ):

        try:
            info = process.info

            process_name = info["name"] or "Unknown"
            command = info.get("cmdline") or []

            # Some processes expose a generic name such as MainThread.
            # Use the executable name when available.
            if command:
                executable_name = Path(command[0]).name

                if process_name == "MainThread":
                    process_name = executable_name

            processes.append({
                "pid": info["pid"],
                "name": process_name,
                "username": info["username"] or "Unknown",
                "memory_percent": float(
                    info["memory_percent"] or 0
                )
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    processes.sort(
        key=lambda process: process["memory_percent"],
        reverse=True
    )

    return {
        "total_processes": len(psutil.pids()),
        "top_processes": processes[:limit]
    }

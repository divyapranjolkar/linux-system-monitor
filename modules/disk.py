import psutil


def get_disk_info(path="/"):
    """Collect disk capacity and usage information."""

    disk = psutil.disk_usage(path)

    return {
        "path": path,
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "usage_percent": disk.percent
    }

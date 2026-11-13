import psutil


def get_cpu_info():
    """Collect CPU usage, core count and frequency."""

    cpu_percent = psutil.cpu_percent(interval=1)

    frequency = psutil.cpu_freq()

    return {
        "logical_cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "usage_percent": cpu_percent,
        "frequency_mhz": (
            round(frequency.current, 2)
            if frequency
            else None
        )
    }

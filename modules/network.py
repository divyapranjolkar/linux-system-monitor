import psutil


def get_network_info():
    """Collect cumulative network traffic counters."""

    counters = psutil.net_io_counters()

    return {
        "bytes_sent_mb": round(
            counters.bytes_sent / (1024 ** 2), 2
        ),
        "bytes_received_mb": round(
            counters.bytes_recv / (1024 ** 2), 2
        ),
        "packets_sent": counters.packets_sent,
        "packets_received": counters.packets_recv,
        "errors_in": counters.errin,
        "errors_out": counters.errout,
        "dropped_in": counters.dropin,
        "dropped_out": counters.dropout
    }

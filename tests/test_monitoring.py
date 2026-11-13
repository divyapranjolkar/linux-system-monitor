
import json
import tempfile
import unittest

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.disk import get_disk_info
from modules.processes import get_process_info
from modules.network import get_network_info

from utils.reports import save_report


class TestCPUMonitor(unittest.TestCase):

    @patch("modules.cpu.psutil.cpu_freq")
    @patch("modules.cpu.psutil.cpu_percent")
    @patch("modules.cpu.psutil.cpu_count")
    def test_cpu_information(
        self,
        mock_count,
        mock_percent,
        mock_frequency
    ):

        mock_count.side_effect = [8, 4]
        mock_percent.return_value = 25.0
        mock_frequency.return_value = SimpleNamespace(
            current=3200.0
        )

        result = get_cpu_info()

        self.assertEqual(result["logical_cores"], 8)
        self.assertEqual(result["physical_cores"], 4)
        self.assertEqual(result["usage_percent"], 25.0)
        self.assertEqual(result["frequency_mhz"], 3200.0)


class TestMemoryMonitor(unittest.TestCase):

    @patch("modules.memory.psutil.swap_memory")
    @patch("modules.memory.psutil.virtual_memory")
    def test_memory_information(
        self,
        mock_memory,
        mock_swap
    ):

        mock_memory.return_value = SimpleNamespace(
            total=8 * 1024**3,
            used=4 * 1024**3,
            available=4 * 1024**3,
            percent=50.0
        )

        mock_swap.return_value = SimpleNamespace(
            total=2 * 1024**3,
            used=1 * 1024**3,
            percent=50.0
        )

        result = get_memory_info()

        self.assertEqual(result["total_gb"], 8.0)
        self.assertEqual(result["used_gb"], 4.0)
        self.assertEqual(result["available_gb"], 4.0)
        self.assertEqual(result["usage_percent"], 50.0)
        self.assertEqual(result["swap_total_gb"], 2.0)


class TestDiskMonitor(unittest.TestCase):

    @patch("modules.disk.psutil.disk_usage")
    def test_disk_information(self, mock_disk):

        mock_disk.return_value = SimpleNamespace(
            total=100 * 1024**3,
            used=40 * 1024**3,
            free=60 * 1024**3,
            percent=40.0
        )

        result = get_disk_info("/")

        self.assertEqual(result["path"], "/")
        self.assertEqual(result["total_gb"], 100.0)
        self.assertEqual(result["used_gb"], 40.0)
        self.assertEqual(result["free_gb"], 60.0)
        self.assertEqual(result["usage_percent"], 40.0)


class TestProcessMonitor(unittest.TestCase):

    @patch("modules.processes.psutil.pids")
    @patch("modules.processes.psutil.process_iter")
    def test_process_information(
        self,
        mock_process_iter,
        mock_pids
    ):

        fake_processes = [
            SimpleNamespace(info={
                "pid": 100,
                "name": "MainThread",
                "username": "tester",
                "memory_percent": 5.0,
                "cmdline": ["/usr/bin/python3"]
            }),
            SimpleNamespace(info={
                "pid": 200,
                "name": "bash",
                "username": "tester",
                "memory_percent": 2.0,
                "cmdline": ["/usr/bin/bash"]
            })
        ]

        mock_process_iter.return_value = fake_processes
        mock_pids.return_value = [100, 200]

        result = get_process_info(limit=1)

        self.assertEqual(result["total_processes"], 2)
        self.assertEqual(len(result["top_processes"]), 1)
        self.assertEqual(
            result["top_processes"][0]["name"],
            "python3"
        )
        self.assertEqual(
            result["top_processes"][0]["memory_percent"],
            5.0
        )


class TestNetworkMonitor(unittest.TestCase):

    @patch("modules.network.psutil.net_io_counters")
    def test_network_information(self, mock_network):

        mock_network.return_value = SimpleNamespace(
            bytes_sent=2 * 1024**2,
            bytes_recv=5 * 1024**2,
            packets_sent=100,
            packets_recv=200,
            errin=0,
            errout=0,
            dropin=0,
            dropout=1
        )

        result = get_network_info()

        self.assertEqual(result["bytes_sent_mb"], 2.0)
        self.assertEqual(result["bytes_received_mb"], 5.0)
        self.assertEqual(result["packets_sent"], 100)
        self.assertEqual(result["packets_received"], 200)
        self.assertEqual(result["dropped_out"], 1)


class TestReportUtility(unittest.TestCase):

    def test_report_creation(self):

        sample_data = {
            "system": {
                "hostname": "test-machine"
            },
            "cpu": {
                "usage_percent": 20.0
            }
        }

        with tempfile.TemporaryDirectory() as temporary_dir:

            report_path = save_report(
                sample_data,
                temporary_dir
            )

            self.assertTrue(report_path.exists())

            with report_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                loaded_data = json.load(file)

            self.assertEqual(
                loaded_data["system"]["hostname"],
                "test-machine"
            )

            self.assertEqual(
                loaded_data["cpu"]["usage_percent"],
                20.0
            )


if __name__ == "__main__":
    unittest.main()

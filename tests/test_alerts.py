
import unittest

from unittest.mock import Mock

from main import check_thresholds


class TestThresholdAlerts(unittest.TestCase):

    def setUp(self):

        self.config = {
            "thresholds": {
                "cpu_percent": 80,
                "memory_percent": 80,
                "disk_percent": 85
            }
        }

        self.logger = Mock()

        self.data = {
            "cpu": {
                "usage_percent": 95.0
            },
            "memory": {
                "usage_percent": 90.0
            },
            "disk": {
                "usage_percent": 90.0
            }
        }

    def test_high_usage_generates_warnings(self):

        check_thresholds(
            self.data,
            self.config,
            self.logger
        )

        self.assertEqual(
            self.logger.warning.call_count,
            3
        )

    def test_normal_usage_generates_no_warnings(self):

        self.data["cpu"]["usage_percent"] = 20.0
        self.data["memory"]["usage_percent"] = 30.0
        self.data["disk"]["usage_percent"] = 40.0

        check_thresholds(
            self.data,
            self.config,
            self.logger
        )

        self.logger.warning.assert_not_called()

    def test_usage_equal_to_threshold_generates_warning(self):

        self.data["cpu"]["usage_percent"] = 80.0
        self.data["memory"]["usage_percent"] = 80.0
        self.data["disk"]["usage_percent"] = 85.0

        check_thresholds(
            self.data,
            self.config,
            self.logger
        )

        self.assertEqual(
            self.logger.warning.call_count,
            3
        )


if __name__ == "__main__":
    unittest.main()

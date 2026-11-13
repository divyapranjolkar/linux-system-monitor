import json

from pathlib import Path
from datetime import datetime


def save_report(data, directory):

    report_dir = Path(directory)

    report_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_file = (
        report_dir / f"system_report_{timestamp}.json"
    )

    with report_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    return report_file


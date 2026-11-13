# Linux System Monitor

A Python-based Linux system monitoring application built with Python, psutil, Bash, and systemd.

## Features

- CPU usage and frequency monitoring
- RAM and swap monitoring
- Disk utilization
- Top processes by memory usage
- Network traffic statistics
- Configurable resource thresholds
- Rotating application logs
- JSON monitoring reports
- Continuous monitoring mode
- Automated unit tests
- Backup and restore scripts
- Scheduled execution using systemd

## Technologies

Python 3, Ubuntu Linux, psutil, Bash, systemd, JSON, Git.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run one monitoring cycle:

```bash
python main.py
```

Run continuous monitoring:

```bash
python main.py --watch
```

Set a custom interval:

```bash
python main.py --watch --interval 10
```

## Testing

```bash
python -m unittest discover -s tests -v
```

## Backup

```bash
./backup_project.sh
```

## Limitations

Network measurements are cumulative counters rather than real-time speeds. Under WSL, resource measurements reflect the Linux environment and may not represent the complete Windows host.

This is an educational Linux monitoring project, not production monitoring infrastructure.

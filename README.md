# LabNSN23 Monitor

A real-time data acquisition (DAQ) monitor built with [Streamlit](https://streamlit.io/) for the **Nuclear & Subnuclear Physics (N&SN) Laboratory 2** exam at the University of Bologna.

The monitor reads a live TDC (Time-to-Digital Converter) data file, displays continuously-updated histograms and rate plots in a web dashboard, detects acquisition stalls, and sends Telegram notifications to the lab team.

---

## Features

- **Histogram display** — TDC spectra for three detector channels (P1, P2, P3) shown in both linear and logarithmic scale, refreshed every 30 seconds
- **Rate monitoring** — instantaneous and average event rates are computed and plotted over time 
- **Dead-acquisition detection** — if no new data arrives for more than 2 minutes, an alert is shown in the dashboard, and a Telegram message is sent
- **Telegram notifications** — automatic status messages are dispatched at scheduled times (09:00 and 15:00) with a screenshot of the current run

---

## Repository structure

```
LabNSN23_monitor/
├── LabMonitor.py      # Main Streamlit application
├── writer.py          # Daq simulator for development purposes
├── config.ini         # Telegram bot credentials and workstation name
├── File.txt           # Example / template data file format, output of the writer script
├── data_23Nov_1.txt   # Sample data file from a real run for the writer script to copy
└── README.md
```

---

## Requirements

- Python 3.9+
- [Streamlit](https://streamlit.io/) — dashboard framework
- [python-telegram-bot](https://python-telegram-bot.org/) — Telegram notifications
- NumPy
- Matplotlib

Install all dependencies with:

```bash
pip install streamlit python-telegram-bot numpy matplotlib
```

> The project was developed in an Anaconda environment on Windows. The GUI file picker (`tkinter`) is used as a fallback when no filename is passed on the command line.

---

## Configuration

Before running, fill in your credentials in `config.ini`:

```ini
[CONFIG]
bot_token = "your-telegram-bot-token"
chat_id   = "your-telegram-chat-id"
postazione = "Workstation A"   ; label shown in notifications
```

- **bot_token** — obtain from [@BotFather](https://t.me/BotFather) on Telegram
- **chat_id** — the group or user ID that should receive alerts
- **postazione** — a human-readable name for the workstation (used in notification messages)

---

## Usage

Navigate to the folder containing the data file, then launch:

```bash
streamlit run LabMonitor.py Filename.txt
```

If no filename argument is provided, a file-picker dialog will open automatically.

The dashboard will open in your default browser. It refreshes every 30 seconds as long as new data is being written to the file.

---

## Data file format

Each line in the data file represents a single event and is expected to follow this whitespace-separated layout:

```
_  <event_number>  <time_from_start>  <ch0_hex>  <ch1_hex>  <ch2_hex>  ...
```

- Lines not starting with `_` are treated as headers and skipped
- TDC counts are in hexadecimal; a value of `0xFFF` (4095) indicates no hit and is excluded from histograms
- The full TDC range is 0–4095, binned in groups of 32

---

## Telegram alerts

Two types of messages are sent automatically:

| Trigger | Message |
|---------|---------|
| No new data for > 2 minutes | `"Data taking stopped in <postazione>!"` |
| Scheduled check at 09:00 and 15:00 | Status photo with caption `"<postazione> data taking is ongoing"` |

The scheduled photo path is currently hardcoded in `LabMonitor.py` — update the `send_photo` call to point to your own screenshot path if needed.

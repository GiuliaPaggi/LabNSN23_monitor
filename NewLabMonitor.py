import time
import os
import sys
from datetime import datetime
import asyncio

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import telegram


# ---------------- TELEGRAM ----------------
BOT_TOKEN = "xxxx"
CHAT_ID = "xxxx"
POSTAZIONE = "Ranzani"

bot = telegram.Bot(token=BOT_TOKEN)

async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def send_photo(photo_path, text):
    await bot.send_message(chat_id=CHAT_ID, text=text)
    with open(photo_path, "rb") as f:
        await bot.send_photo(chat_id=CHAT_ID, photo=f)


# ---------------- UTILS ----------------
def checktime():
    now = datetime.now()
    return (now.hour == 9 and now.minute < 5) or \
           (now.hour == 15 and now.minute < 25)


def read_new_lines(f):
    """Read only new lines without loading entire file"""
    lines = []
    while True:
        line = f.readline()
        if not line:
            break
        lines.append(line)
    return lines


async def main():

    st.set_page_config(page_title="Monitor", layout="wide")
    st.title("DAQ Monitor")

    refresh_time = 30

    # -------- FILE --------
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        st.error("Provide file as argument")
        return

    if not os.path.exists(file_name):
        st.error("File does not exist")
        return

    f = open(file_name, "r")

    # -------- DATA --------
    bins = 256
    hist_p0 = np.zeros(bins, dtype=np.int32)
    hist_p1 = np.zeros(bins, dtype=np.int32)
    hist_p2 = np.zeros(bins, dtype=np.int32)

    x_axis = np.arange(bins)

    rate_info = []
    rate_over_time = []

    MAX_RATE_INFO = 10
    MAX_RATE_HISTORY = 40

    # rate sampling control (10 min)
    loop_counter = 0
    POINT_EVERY_N_LOOPS = int(600 / refresh_time)  # 600s = 10 min

    message_sent = False

    # -------- FIGURE --------
    fig, axes = plt.subplots(3, 3, figsize=(12, 8))
    plot_placeholder = st.empty()

    # -------- LOOP --------
    while True:

        time.sleep(refresh_time)

        # -------- READ INCREMENTALLY --------
        lines = []
        while True:
            l = f.readline()
            if not l:
                break
            lines.append(l)

        # -------- STOP CHECK --------
        if not lines:
            if time.time() - os.path.getmtime(file_name) > 120:
                await send_message(f"Data taking stopped in {POSTAZIONE}!")
                st.error("Data taking stopped")
                return
            continue

        # -------- CLEAN LINES --------
        if not lines[0].startswith("_"):
            lines.pop(0)
        if lines and not lines[-1].endswith("\n"):
            lines.pop(-1)

        if not lines:
            continue

        # -------- PROCESS --------
        for line in lines:
            try:
                parts = line.split()

                p0 = int(parts[3], 16)
                p1 = int(parts[4], 16)
                p2 = int(parts[5], 16)

                if p0 != 4095:
                    hist_p0[p0 // 16] += 1
                if p1 != 4095:
                    hist_p1[p1 // 16] += 1
                if p2 != 4095:
                    hist_p2[p2 // 16] += 1

            except Exception:
                continue

        # -------- RATE --------
        last = lines[-1].split()
        event_n = int(last[1])
        time_from_start = float(last[2])

        if rate_info:
            elapsed = time_from_start - rate_info[0][1]
            inst_rate = (event_n - rate_info[0][0]) / elapsed if elapsed > 0 else 0
        else:
            inst_rate = 0

        avg_rate = event_n / time_from_start if time_from_start > 0 else 0

        rate_info.append((event_n, time_from_start))
        if len(rate_info) > MAX_RATE_INFO:
            rate_info.pop(0)

        # --- sample every 10 minutes ---
        loop_counter += 1
        if loop_counter % POINT_EVERY_N_LOOPS == 0:
            rate_over_time.append(inst_rate)
            if len(rate_over_time) > MAX_RATE_HISTORY:
                rate_over_time.pop(0)

        # -------- PLOTTING --------
        for ax in axes.flatten():
            ax.cla()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # common x ticks
        xticks = np.arange(0, bins + 1, 32)
        xticklabels = [str(i * 16) for i in range(0, bins + 1, 32)]

        # --- LINEAR (row 0) ---
        for i, hist in enumerate([hist_p0, hist_p1, hist_p2]):
            ax = axes[0, i]
            ax.bar(x_axis, hist)
            ax.set_title(f"P{i+1} (Linear)\n{timestamp}")
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            ax.set_xlabel("TDC count")
            ax.set_ylabel("Entries")

        # --- LOG (row 1) ---
        for i, hist in enumerate([hist_p0, hist_p1, hist_p2]):
            ax = axes[1, i]

            mask = hist > 0
            if np.any(mask):
                ax.bar(x_axis[mask], hist[mask])

            ax.set_yscale("log")
            ax.set_title(f"P{i+1} (Log)\n{timestamp}")
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            ax.set_xlabel("TDC count")
            ax.set_ylabel("Entries")

        # --- RATE (row 2) ---
        axes[2, 0].plot(rate_over_time, marker='o')
        axes[2, 0].set_title(f"Rate (1 point / 10 min)\n{timestamp}")
        axes[2, 0].set_xlabel("Time [10 min steps]")
        axes[2, 0].set_ylabel("Hz")

        if rate_over_time:
            ymin = min(rate_over_time) * 0.9
            ymax = max(rate_over_time) * 1.1
            if ymin != ymax:
                axes[2, 0].set_ylim(ymin, ymax)

        axes[2, 1].axis("off")
        axes[2, 2].axis("off")

        # --- GLOBAL TITLE ---
        fig.suptitle(
            f"Events: {event_n} | Avg: {avg_rate:.2f} Hz | Inst: {inst_rate:.2f} Hz",
            fontsize=16
        )
        fig.subplots_adjust(
            left=0.06,
            right=0.98,
            top=0.90,
            bottom=0.08,
            hspace=0.6,   
            wspace=0.3
        )
        plot_placeholder.pyplot(fig)

        # -------- TELEGRAM --------
        if checktime() and not message_sent:
            await send_photo("screenR.jpg",
                             f"{POSTAZIONE} data taking is ongoing")
            message_sent = True
        elif not checktime():
            message_sent = False

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    asyncio.run(main())

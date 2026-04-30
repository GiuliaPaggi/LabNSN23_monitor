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


# ---------------- MAIN ----------------
async def main():

    st.set_page_config(page_title="Monitor", layout="wide")
    st.title("DAQ Monitor")

    refresh_time = 30

    # ------ find valid file to read ------
    if len(sys.argv) > 1:
        file_name = './'+sys.argv[1]
        if not os.path.exists(file_name):
            print('This file does not exist! Select the data file', flush=True)
            Tk().withdraw()
            file_name = askopenfilename()
    else:
        print('Select the data file', flush=True)
        Tk().withdraw()
        file_name = askopenfilename()    
            
    f = open(file_name, 'r')
    print(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+ ' Reading ' + file_name )

    # -------- time histos --------
    bins = 256
    hist_p0 = np.zeros(bins, dtype=np.int32)
    hist_p1 = np.zeros(bins, dtype=np.int32)
    hist_p2 = np.zeros(bins, dtype=np.int32)

    x_axis = np.arange(bins)

    rate_info = []            # last N points
    rate_over_time = []       # plotted history (bounded)

    MAX_RATE_INFO = 10
    MAX_RATE_HISTORY = 40

    message_sent = False

    # -------- plot --------
    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    plot_placeholder = st.empty()

    while True:

        time.sleep(refresh_time)

        lines = read_new_lines(f)

        # -------- check for new lines --------
        if not lines:
            if time.time() - os.path.getmtime(file_name) > 120:
                await send_message(f"Data taking stopped in {POSTAZIONE}!")
                st.error("Data taking stopped")
                return
            continue

        if not lines[0].startswith("_"):
            lines.pop(0)
        if lines and not lines[-1].endswith("\n"):
            lines.pop(-1)

        if not lines:
            continue


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

            except Exception as e:
                print("Broken line:")
                print(line[i])
                print("Error: ", e)
                continue

        # -------- RATE COMPUTATION --------
        last = lines[-1].split()
        event_n = int(last[1])
        time_from_start = float(last[2])

        if rate_info:
            elapsed = time_from_start - rate_info[0][1]
            if elapsed > 0:
                inst_rate = (event_n - rate_info[0][0]) / elapsed
            else:
                inst_rate = 0
        else:
            inst_rate = 0

        avg_rate = event_n / time_from_start if time_from_start > 0 else 0

        rate_info.append((event_n, time_from_start))

        if len(rate_info) > MAX_RATE_INFO:
            rate_info.pop(0)

        rate_over_time.append(inst_rate)
        if len(rate_over_time) > MAX_RATE_HISTORY:
            rate_over_time.pop(0)

        # -------- UPDATE PLOTS  --------
        for ax in axes.flatten():
            ax.cla()

        # linear
        axes[0, 0].bar(x_axis, hist_p0)
        axes[0, 0].set_title("P1")

        axes[0, 1].bar(x_axis, hist_p1)
        axes[0, 1].set_title("P2")

        axes[0, 2].bar(x_axis, hist_p2)
        axes[0, 2].set_title("P3")

        # rate
        axes[1, 0].plot(rate_over_time)
        axes[1, 0].set_title("Rate over time")

        # log plots
        axes[1, 1].bar(x_axis, hist_p0)
        axes[1, 1].set_yscale("log")

        axes[1, 2].bar(x_axis, hist_p1)
        axes[1, 2].set_yscale("log")

        axes[2, 0].bar(x_axis, hist_p2)
        axes[2, 0].set_yscale("log")

        axes[2, 1].axis("off")
        axes[2, 2].axis("off")

        fig.suptitle(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Events: {event_n} | Avg: {avg_rate:.2f} Hz | Inst: {inst_rate:.2f} Hz"
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
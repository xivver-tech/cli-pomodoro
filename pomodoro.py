#!/usr/bin/env python3
"""
CLI Pomodoro Timer
- Classic 25/5 cycles
- Configurable work / break lengths
- Session history saved to disk
- Daily / total stats
"""

import json
import time
import sys
from datetime import datetime, date
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "pomodoro_history.json"

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def clear_line():
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def countdown(seconds: int, label: str):
    end = time.time() + seconds
    while True:
        remaining = int(end - time.time())
        if remaining <= 0:
            break
        mins, secs = divmod(remaining, 60)
        clear_line()
        sys.stdout.write(f"{label}: {mins:02d}:{secs:02d}")
        sys.stdout.flush()
        time.sleep(0.25)
    clear_line()
    print(f"{label}: Done!")

def run_session(work_min: int, break_min: int, cycles: int):
    history = load_history()
    print(f"\nPomodoro: {work_min} min work / {break_min} min break × {cycles} cycles")
    print("Press Ctrl+C to stop early\n")

    completed = 0
    try:
        for i in range(1, cycles + 1):
            print(f"── Cycle {i}/{cycles} ──")
            countdown(work_min * 60, "WORK")
            completed += 1

            # log work session
            history.append({
                "type": "work",
                "minutes": work_min,
                "timestamp": datetime.now().isoformat()
            })
            save_history(history)

            if i < cycles:
                countdown(break_min * 60, "BREAK")
                history.append({
                    "type": "break",
                    "minutes": break_min,
                    "timestamp": datetime.now().isoformat()
                })
                save_history(history)

        print("\nAll cycles finished. Nice work!")
    except KeyboardInterrupt:
        print(f"\n\nStopped early. Completed {completed} work session(s).")

def show_stats():
    history = load_history()
    if not history:
        print("No sessions recorded yet.")
        return

    today = date.today().isoformat()
    work_today = 0
    work_total = 0
    sessions_today = 0
    sessions_total = 0

    for entry in history:
        if entry["type"] != "work":
            continue
        sessions_total += 1
        work_total += entry["minutes"]
        if entry["timestamp"].startswith(today):
            sessions_today += 1
            work_today += entry["minutes"]

    print("\n=== Pomodoro Stats ===")
    print(f"Today  : {sessions_today} sessions  |  {work_today} minutes")
    print(f"Total  : {sessions_total} sessions  |  {work_total} minutes")
    print()

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("stats", "stat", "s"):
        show_stats()
        return

    # defaults: 25 min work, 5 min break, 4 cycles
    work = 25
    brk = 5
    cycles = 4

    if len(sys.argv) >= 2:
        try:
            work = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) >= 3:
        try:
            brk = int(sys.argv[2])
        except ValueError:
            pass
    if len(sys.argv) >= 4:
        try:
            cycles = int(sys.argv[3])
        except ValueError:
            pass

    print("CLI Pomodoro")
    print("Usage: python pomodoro.py [work_min] [break_min] [cycles]")
    print("       python pomodoro.py stats")
    run_session(work, brk, cycles)

if __name__ == "__main__":
    main()

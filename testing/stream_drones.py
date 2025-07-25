#!/usr/bin/env python3
"""
stream_drones.py

Reads all DUSKY*.txt files in cwd (each a JSON array of objects), then every INTERVAL
sends one JSON object from each file to the website

You can filter by timestamp on startup:

    python3 stream_drones.py --start-time 2025-07-25T12:00:00

Controls (any time, press Enter after):
  p → pause streaming
  r → resume streaming
  + → send faster (−0.1 s per step, min 0.01 s)
  - → send slower (+0.1 s per step)
  Ctrl‑C → quit

Usage:
    python3 stream_drones.py [--start-time ISO8601] [--interval 1.0]
"""

import glob
import json
import time
import requests
import os
import sys
import argparse
import threading
from datetime import datetime

# ————— CONFIG —————
BASE_URL         = os.environ.get("DRONE_SERVER_URL", "https://andrewfreeman.pythonanywhere.com")
FILE_GLOB        = "DUSKY*.txt"
DEFAULT_INTERVAL = 1.0

API_KEY    = "cvclUFuGyLdbrrehqA6wfUDoiYtRkS1Yo8g8Jy5A"
SECRET_KEY = "c04cbe664bf2a842ce299ea3f07dd3b21cf06b83a9e1446a22c205e59a0abece"
# —————————————————

def load_iterators(glob_pattern, start_time=None):
    """
    Returns { call_sign: iterator_over_JSON_objects }, optionally filtering
    out any obj whose obj['timestamp'] < start_time.
    """
    iters = {}
    for path in sorted(glob.glob(glob_pattern)):
        cs = os.path.splitext(os.path.basename(path))[0]
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if not isinstance(data, list):
                print(f"⚠️  {path} does not contain a JSON array, skipping.", file=sys.stderr)
                continue
        except (IOError, json.JSONDecodeError) as e:
            print(f"⚠️  Could not load JSON from {path}: {e}", file=sys.stderr)
            continue

        if start_time is not None:
            def filtered(gen):
                for obj in gen:
                    ts = obj.get("timestamp")
                    if not ts:
                        continue
                    try:
                        dt = datetime.fromisoformat(ts)
                    except ValueError:
                        continue
                    if dt >= start_time:
                        yield obj
            iters[cs] = filtered(data)
        else:
            iters[cs] = iter(data)
    return iters

def send_json(call_sign, obj):
    """POST the JSON object to /data, with API headers."""
    url = f"{BASE_URL}/data"
    headers = {
        "X-API-KEY":    API_KEY,
        "X-SECRET-KEY": SECRET_KEY,
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json=obj, headers=headers, timeout=5)
        resp.raise_for_status()
        print(f"[{time.strftime('%H:%M:%S')}] ✓ {call_sign}", file=sys.stdout)
    except requests.RequestException as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ {call_sign}: {e}", file=sys.stderr)

def input_listener(paused_event, interval_container):
    """
    Runs in a daemon thread: waits for 'p', 'r', '+', or '-' + Enter.
    Modifies paused_event or interval_container[0].
    """
    while True:
        cmd = sys.stdin.readline().strip().lower()
        if cmd == 'p' and not paused_event.is_set():
            paused_event.set()
            print("[PAUSED] (type 'r' + Enter to resume)")
        elif cmd == 'r' and paused_event.is_set():
            paused_event.clear()
            print("[RESUMED]")
        elif cmd == '+':
            old = interval_container[0]
            interval_container[0] = max(0.01, old - 0.1)
            print(f"[SPEED ↑] interval now {interval_container[0]:.2f}s")
        elif cmd == '-':
            old = interval_container[0]
            interval_container[0] = old + 0.1
            print(f"[SPEED ↓] interval now {interval_container[0]:.2f}s")

def main():
    p = argparse.ArgumentParser(
        description="Stream JSON drone data with pause/resume, start-time filter, and speed control."
    )
    p.add_argument(
        "--start-time", help="ISO‑8601 timestamp to start streaming from (e.g. 2025-07-25T12:00:00)"
    )
    p.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL,
        help=f"Initial seconds between sends (default: {DEFAULT_INTERVAL})"
    )
    args = p.parse_args()

    # parse start-time if given
    start_time = None
    if args.start_time:
        try:
            start_time = datetime.fromisoformat(args.start_time)
        except ValueError:
            print("❌ Invalid --start-time; use ISO‑8601, e.g. 2025-07-25T12:00:00", file=sys.stderr)
            sys.exit(1)

    # load data iterators
    iterators = load_iterators(FILE_GLOB, start_time=start_time)
    if not iterators:
        print(f"No files matching '{FILE_GLOB}' found or none contained valid data.", file=sys.stderr)
        sys.exit(1)

    # use mutable container so listener can update it
    interval = [args.interval]

    print(f"Loaded {len(iterators)} streams. Starting at " +
          (args.start_time or "the beginning") + f". Interval = {interval[0]:.2f}s")
    print("Controls: p = pause, r = resume, + = faster, - = slower (press Enter after).")

    # start pause/resume & speed listener
    paused = threading.Event()
    threading.Thread(target=input_listener, args=(paused, interval), daemon=True).start()

    alive = set(iterators.keys())
    try:
        while alive:
            if paused.is_set():
                time.sleep(0.1)
                continue

            cycle_start = time.time()
            for cs in list(alive):
                it = iterators[cs]
                try:
                    obj = next(it)
                except StopIteration:
                    alive.remove(cs)
                    continue
                send_json(cs, obj)

            elapsed = time.time() - cycle_start
            to_sleep = interval[0] - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

    except KeyboardInterrupt:
        print("\n✋ Interrupted by user, exiting.", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()


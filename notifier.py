#!/usr/bin/env python3
"""CAT prep math facts notifier — pushes random math questions via ntfy.sh every 30 minutes."""

import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path

import requests

# ── Configuration ──────────────────────────────────────────────────────────────
NTFY_TOPIC = "sai-reminders"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
INTERVAL_SECONDS = 30 * 60  # 30 minutes

STATE_FILE = Path(__file__).parent / "state.json"
LOG_FILE = Path(__file__).parent / "notifier.log"

# ── Topic data ─────────────────────────────────────────────────────────────────
SQUARES = [(n, n * n) for n in range(1, 31)]
CUBES = [(n, n ** 3) for n in range(1, 21)]
TABLES = [(a, b, a * b) for a in range(2, 21) for b in range(1, 21)]
FRACTIONS = [(n, d, round(n / d * 100, 4)) for d in range(2, 21) for n in range(1, d)]
POWERS_OF_2 = [(n, 2 ** n) for n in range(1, 16)]

def _sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

PRIMES = _sieve(100)

TOPICS = {
    "squares":   {"emoji": "🟦", "data": SQUARES},
    "cubes":     {"emoji": "🟧", "data": CUBES},
    "tables":    {"emoji": "✖️",  "data": TABLES},
    "fractions": {"emoji": "💯", "data": FRACTIONS},
    "powers":    {"emoji": "⚡", "data": POWERS_OF_2},
    "primes":    {"emoji": "🔢", "data": PRIMES},
}
TOPIC_ORDER = list(TOPICS.keys())

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ── State ──────────────────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_topic": None, "sent": {t: [] for t in TOPICS}}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ── Question builders ──────────────────────────────────────────────────────────
def pick_item(topic_name, state):
    data = TOPICS[topic_name]["data"]
    sent = state["sent"].get(topic_name, [])
    unsent = [i for i in range(len(data)) if i not in sent]
    if not unsent:
        state["sent"][topic_name] = []
        unsent = list(range(len(data)))
    idx = random.choice(unsent)
    state["sent"][topic_name].append(idx)
    # keep recent list bounded to half the dataset
    max_recent = max(1, len(data) // 2)
    state["sent"][topic_name] = state["sent"][topic_name][-max_recent:]
    return data[idx]

def build_notification(topic_name, state):
    emoji = TOPICS[topic_name]["emoji"]
    item = pick_item(topic_name, state)

    if topic_name == "squares":
        n, ans = item
        title = f"{emoji} {n}² = ?"
        body = f"Answer: {ans}"

    elif topic_name == "cubes":
        n, ans = item
        title = f"{emoji} {n}³ = ?"
        body = f"Answer: {ans}"

    elif topic_name == "tables":
        a, b, ans = item
        title = f"{emoji} {a} × {b} = ?"
        body = f"Answer: {ans}"

    elif topic_name == "fractions":
        n, d, pct = item
        title = f"{emoji} {n}/{d} = ?%"
        body = f"Answer: {pct}%"

    elif topic_name == "powers":
        n, ans = item
        title = f"{emoji} 2^{n} = ?"
        body = f"Answer: {ans}"

    elif topic_name == "primes":
        p = item
        # alternate between two question styles
        if random.random() < 0.5:
            title = f"{emoji} Is {p} prime?"
            body = f"Answer: Yes — {p} is prime"
        else:
            # pick a range around a random prime
            idx = PRIMES.index(p)
            lo = (PRIMES[idx - 1] if idx > 0 else 2) + 1
            hi = PRIMES[min(idx + 3, len(PRIMES) - 1)]
            in_range = [x for x in PRIMES if lo <= x <= hi]
            title = f"{emoji} Primes between {lo} and {hi}?"
            body = f"Answer: {', '.join(map(str, in_range))}"

    return title, body

# ── Send ───────────────────────────────────────────────────────────────────────
def send_notification(title, body):
    resp = requests.post(
        NTFY_URL,
        data=body.encode("utf-8"),
        headers={"Title": title},
        timeout=10,
    )
    resp.raise_for_status()

# ── Topic selection ────────────────────────────────────────────────────────────
def next_topic(last_topic):
    choices = [t for t in TOPIC_ORDER if t != last_topic]
    return random.choice(choices)

# ── Main loop ──────────────────────────────────────────────────────────────────
def main():
    log.info("CAT notifier started")
    state = load_state()

    while True:
        topic = next_topic(state.get("last_topic"))
        try:
            title, body = build_notification(topic, state)
            send_notification(title, body)
            state["last_topic"] = topic
            save_state(state)
            log.info("Sent [%s] %s | %s", topic, title, body)
        except Exception as e:
            log.error("Failed to send notification: %s", e)

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()

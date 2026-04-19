# CAT Prep Math Facts Notifier

Pushes a random CAT prep math question to your phone every 30 minutes via [ntfy.sh](https://ntfy.sh).

## Topics

| Topic | Example question | Answer style |
|-------|-----------------|--------------|
| 🟦 Squares | 17² = ? | 289 |
| 🟧 Cubes | 12³ = ? | 1728 |
| ✖️ Tables | 7 × 8 = ? | 56 |
| 💯 Fractions | 1/7 = ?% | 14.2857% |
| ⚡ Powers of 2 | 2^10 = ? | 1024 |
| 🔢 Primes | Is 67 prime? | Yes |

## Setup

```bash
# Clone and install
git clone <repo-url>
cd notifications
chmod +x install.sh
./install.sh
```

On your phone, install the **ntfy** app and subscribe to topic `sai-reminders`.

## Requirements

- Python 3.x
- `requests` library (installed by `install.sh`)
- systemd (user session)

## Configuration

All config lives at the top of `notifier.py`:

```python
NTFY_TOPIC = "sai-reminders"
INTERVAL_SECONDS = 30 * 60  # 30 minutes
```

## Logs

```bash
tail -f notifier.log
# or
journalctl --user -u cat-notifier -f
```

## Service management

```bash
systemctl --user status cat-notifier
systemctl --user restart cat-notifier
systemctl --user stop cat-notifier
```

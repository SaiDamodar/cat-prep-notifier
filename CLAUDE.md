# CAT Prep Math Facts Notifier

Pushes random CAT math questions to phone via ntfy.sh every 30 minutes.

## What it does
- Picks a random topic (squares, cubes, tables, fractions, powers of 2, primes)
- Never repeats the same topic twice in a row
- Tracks sent items in `state.json` to avoid recent repeats
- Sends title = question, body = answer via ntfy.sh → `sai-reminders` topic

## How to change the interval
Edit `INTERVAL_SECONDS` at the top of `notifier.py`:
```python
INTERVAL_SECONDS = 30 * 60  # change 30 to desired minutes
```
Then restart: `systemctl --user restart cat-notifier`

## How to add new topics
1. Add data list in `notifier.py` (follow pattern of existing topics)
2. Add entry to `TOPICS` dict with `emoji` and `data` keys
3. Add a branch in `build_notification()` to format title/body
4. Add topic name to `TOPIC_ORDER` list

## How to check logs
```bash
# File log (persists across restarts)
tail -f /home/sai/dev/notifications/notifier.log

# systemd journal (live)
journalctl --user -u cat-notifier -f
```

## How to stop/start/restart
```bash
systemctl --user stop cat-notifier
systemctl --user start cat-notifier
systemctl --user restart cat-notifier
systemctl --user status cat-notifier
```

## State file
`state.json` tracks which items were recently sent per topic. Safe to delete if you want a full reset — it regenerates on next run.

## ntfy topic
Topic: `sai-reminders` — subscribe in the ntfy app on your phone.

## Future: self-host ntfy via Tailscale
Replace `NTFY_URL` in `notifier.py` with your Tailscale internal address, e.g.:
```python
NTFY_URL = "http://100.x.x.x:80/sai-reminders"
```
Run ntfy server on a home machine and point Tailscale at it for private, self-hosted notifications without rate limits.

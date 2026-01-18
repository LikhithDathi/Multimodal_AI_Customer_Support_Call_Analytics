from datetime import datetime

def format_timestamp(ts: str):
    dt = datetime.fromisoformat(ts)
    now = datetime.now()

    if dt.date() == now.date():
        return f"Today, {dt.strftime('%I:%M %p')}"
    elif (now.date() - dt.date()).days == 1:
        return f"Yesterday, {dt.strftime('%I:%M %p')}"
    else:
        return dt.strftime("%b %d, %I:%M %p")



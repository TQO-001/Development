import time
from functools import wraps


class RateLimitExceeded(Exception):
    def __init__(self, wait_time):
        self.wait_time = wait_time


def rate_limit(calls: int = 3, period: int = 5):
    def decorator(func):
        timestamps = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timestamps
            current_time = time.perf_counter()

            # Filter out timestamps outside the current window
            timestamps = [t for t in timestamps if current_time - t <= period]

            if len(timestamps) >= calls:
                # Calculate exactly how long we need to wait based on the oldest timestamp in the window
                wait_time = period - (current_time - timestamps[0])
                raise RateLimitExceeded(wait_time)

            timestamps.append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@rate_limit(calls=3, period=5)
def send_request(endpoint: str):
    print(f"[{endpoint}]: Request has been sent")


# --- Modified Execution Loop ---
for i in range(6):
    try:
        send_request("API")
        time.sleep(0.2)  # Just to separate the successful calls slightly
    except RateLimitExceeded as e:
        # Get the remaining time to wait
        remaining = int(e.wait_time) + 1

        # Countdown loop that overwrites the same line
        for seconds_left in range(remaining, 0, -1):
            # \r moves cursor to start, flush=True forces the terminal to display it immediately
            print(f"\r⚠️ Rate limit reached. Waiting... {seconds_left}s", end="", flush=True)
            time.sleep(1)

        # Clear the line entirely when done so the next success print looks clean
        print("\r" + " " * 40 + "\r", end="", flush=True)

        # Retry the request now that the wait is over
        send_request("API")
import time
from threading import Thread

class CountdownBackend:
    def __init__(self):
        self.time_str = "00:00"
        self.countdown_active = False
        self.original_time = "00:00"

    def start_countdown(self, time_str):
        self.original_time = time_str
        self.time_str = time_str
        self.countdown_active = True
        Thread(target=self.update_countdown).start()

    def stop_countdown(self):
        self.countdown_active = False

    def reset_countdown(self):
        self.countdown_active = False
        self.time_str = self.original_time

    def validate_time(self, time_str):
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        if not all(part.isdigit() for part in parts):
            return False
        if int(parts[0]) > 59 or int(parts[1]) > 59:
            return False
        return True

    def update_countdown(self):
        while self.countdown_active:
            time_parts = [int(part) for part in self.time_str.split(":")]
            if time_parts[1] > 0:
                time_parts[1] -= 1
            elif time_parts[0] > 0:
                time_parts[0] -= 1
                time_parts[1] = 59
            else:
                self.countdown_active = False
            self.time_str = f"{time_parts[0]:02d}:{time_parts[1]:02d}"
            time.sleep(1)

import threading
import time
from queue import Queue

class IPCSimulator:
    def __init__(self):
        self.buffer = Queue(maxsize=8)
        self.events = Queue()
        self.speed = 1.0
        self._running = False
        self._threads = []

    def start(self):
        self._running = True
        p = threading.Thread(target=self._producer, daemon=True)
        c = threading.Thread(target=self._consumer, daemon=True)
        p.start(); c.start()
        self._threads.extend([p, c])

    def _sleep(self, secs: float):
        time.sleep(max(0.01, secs / max(0.1, self.speed)))

    def _producer(self):
        i = 0
        while self._running:
            data = {"seq": i, "value": i * 2}
            self.buffer.put(data)
            self.events.put({"type": "produce", "data": data})
            i += 1
            self._sleep(0.4)

    def _consumer(self):
        while self._running:
            data = self.buffer.get()
            self.events.put({"type": "consume", "data": data})
            self._sleep(0.6)

    def pause(self):
        self._running = False

    def resume(self):
        if not self._running:
            self.start()

    def reset(self):
        self.pause()
        while not self.events.empty():
            self.events.get()
        while not self.buffer.empty():
            self.buffer.get()

    def speed_up(self):
        self.speed *= 1.2

    def speed_down(self):
        self.speed /= 1.2


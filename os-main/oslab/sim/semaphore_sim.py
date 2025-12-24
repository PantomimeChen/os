import threading
import time
from queue import Queue

class CountingSemaphore:
    def __init__(self, value: int):
        self._value = value
        self._cond = threading.Condition()

    def acquire(self):
        with self._cond:
            while self._value <= 0:
                self._cond.wait()
            self._value -= 1

    def release(self):
        with self._cond:
            self._value += 1
            self._cond.notify()

    @property
    def value(self):
        return self._value

class SemaphoreSimulator:
    def __init__(self, capacity: int = 3):
        self.sem = CountingSemaphore(capacity)
        self.events = Queue()
        self.speed = 1.0
        self._running = False
        self._threads = []
        self._blocked = []

    def start(self, producers: int = 2, consumers: int = 2):
        self._running = True
        for i in range(producers):
            t = threading.Thread(target=self._producer, args=(i+1,), daemon=True)
            t.start(); self._threads.append(t)
        for i in range(consumers):
            t = threading.Thread(target=self._consumer, args=(i+1,), daemon=True)
            t.start(); self._threads.append(t)

    def _sleep(self, secs: float):
        time.sleep(max(0.01, secs / max(0.1, self.speed)))

    def _producer(self, idx: int):
        i = 0
        while self._running:
            self.events.put({"type": "try", "role": "P", "id": idx})
            acquired = False
            with threading.Lock():
                if self.sem.value <= 0:
                    self._blocked.append(("P", idx))
            self.sem.acquire()
            acquired = True
            self.events.put({"type": "acquire", "role": "P", "id": idx, "sem": self.sem.value})
            self._sleep(0.5)
            self.sem.release()
            self.events.put({"type": "release", "role": "P", "id": idx, "sem": self.sem.value})
            try:
                self._blocked.remove(("P", idx))
            except ValueError:
                pass
            i += 1
            self._sleep(0.4)

    def _consumer(self, idx: int):
        while self._running:
            self.events.put({"type": "try", "role": "C", "id": idx})
            with threading.Lock():
                if self.sem.value <= 0:
                    self._blocked.append(("C", idx))
            self.sem.acquire()
            self.events.put({"type": "acquire", "role": "C", "id": idx, "sem": self.sem.value})
            self._sleep(0.6)
            self.sem.release()
            self.events.put({"type": "release", "role": "C", "id": idx, "sem": self.sem.value})
            try:
                self._blocked.remove(("C", idx))
            except ValueError:
                pass
            self._sleep(0.5)

    def pause(self):
        self._running = False

    def resume(self):
        if not self._running:
            self.start()

    def reset(self):
        self.pause()
        while not self.events.empty():
            self.events.get()
        self._blocked.clear()

    def speed_up(self):
        self.speed *= 1.2

    def speed_down(self):
        self.speed /= 1.2


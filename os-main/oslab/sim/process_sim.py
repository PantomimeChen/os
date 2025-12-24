import threading
import time
from queue import Queue
from typing import Dict, List
from oslab.models.process import ProcessState

class ProcessSimulator:
    def __init__(self):
        self.events = Queue()
        self.speed = 1.0
        self._threads: List[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()

    def start(self, count: int = 5):
        self._running = True
        for i in range(count):
            t = threading.Thread(target=self._run_proc, args=(i + 1,), daemon=True)
            t.start()
            self._threads.append(t)

    def _sleep(self, secs: float):
        time.sleep(max(0.01, secs / max(0.1, self.speed)))

    def _run_proc(self, pid: int):
        self.events.put({"pid": pid, "state": ProcessState.CREATED.value})
        self._sleep(0.5)
        self.events.put({"pid": pid, "state": ProcessState.READY.value})
        self._sleep(0.5)
        if not self._running:
            return
        self.events.put({"pid": pid, "state": ProcessState.RUNNING.value})
        self._sleep(1.0)
        self.events.put({"pid": pid, "state": ProcessState.BLOCKED.value})
        self._sleep(0.5)
        self.events.put({"pid": pid, "state": ProcessState.READY.value})
        self._sleep(0.5)
        self.events.put({"pid": pid, "state": ProcessState.RUNNING.value})
        self._sleep(1.0)
        self.events.put({"pid": pid, "state": ProcessState.TERMINATED.value})

    def pause(self):
        with self._lock:
            self._running = False

    def resume(self):
        with self._lock:
            if not self._running:
                self._running = True

    def reset(self):
        with self._lock:
            self._running = False
            self._threads.clear()
            while not self.events.empty():
                self.events.get()

    def speed_up(self):
        self.speed *= 1.2

    def speed_down(self):
        self.speed /= 1.2


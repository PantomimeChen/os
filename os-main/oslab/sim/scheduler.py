from typing import List, Tuple
from oslab.models.process import ProcSpec, TimelineSlice

def _metrics(specs: List[ProcSpec], slices: List[TimelineSlice]) -> Tuple[float, float]:
    finish = {}
    for s in slices:
        finish[s.pid] = s.end
    waits = []
    turns = []
    for p in specs:
        t = finish[p.pid] - p.arrival
        w = t - p.burst
        waits.append(w)
        turns.append(t)
    return sum(waits) / len(waits) if waits else 0.0, sum(turns) / len(turns) if turns else 0.0

def fcfs(specs: List[ProcSpec], cores: int = 1) -> Tuple[List[TimelineSlice], Tuple[float, float]]:
    time = [0] * cores
    order = sorted(specs, key=lambda p: (p.arrival, p.pid))
    slices = []
    for p in order:
        idx = min(range(cores), key=lambda i: time[i])
        start = max(time[idx], p.arrival)
        end = start + p.burst
        time[idx] = end
        slices.append(TimelineSlice(pid=p.pid, start=start, end=end, core=idx))
    return slices, _metrics(specs, slices)

def sjf(specs: List[ProcSpec], cores: int = 1, preemptive: bool = False) -> Tuple[List[TimelineSlice], Tuple[float, float]]:
    t = 0
    done = set()
    remaining = {p.pid: p.burst for p in specs}
    slices = []
    while len(done) < len(specs):
        ready = [p for p in specs if p.arrival <= t and p.pid not in done and remaining[p.pid] > 0]
        if not ready:
            t = min([p.arrival for p in specs if p.pid not in done])
            continue
        if preemptive:
            p = min(ready, key=lambda x: remaining[x.pid])
            start = t
            t += 1
            remaining[p.pid] -= 1
            slices.append(TimelineSlice(pid=p.pid, start=start, end=t, core=0))
            if remaining[p.pid] == 0:
                done.add(p.pid)
        else:
            p = min(ready, key=lambda x: x.burst)
            start = t
            t += remaining[p.pid]
            slices.append(TimelineSlice(pid=p.pid, start=start, end=t, core=0))
            remaining[p.pid] = 0
            done.add(p.pid)
    return slices, _metrics(specs, slices)

def priority(specs: List[ProcSpec], cores: int = 1, preemptive: bool = False) -> Tuple[List[TimelineSlice], Tuple[float, float]]:
    t = 0
    done = set()
    remaining = {p.pid: p.burst for p in specs}
    slices = []
    while len(done) < len(specs):
        ready = [p for p in specs if p.arrival <= t and p.pid not in done and remaining[p.pid] > 0]
        if not ready:
            t = min([p.arrival for p in specs if p.pid not in done])
            continue
        if preemptive:
            p = min(ready, key=lambda x: x.priority)
            start = t
            t += 1
            remaining[p.pid] -= 1
            slices.append(TimelineSlice(pid=p.pid, start=start, end=t, core=0))
            if remaining[p.pid] == 0:
                done.add(p.pid)
        else:
            p = min(ready, key=lambda x: x.priority)
            start = t
            t += remaining[p.pid]
            slices.append(TimelineSlice(pid=p.pid, start=start, end=t, core=0))
            remaining[p.pid] = 0
            done.add(p.pid)
    return slices, _metrics(specs, slices)

def rr(specs: List[ProcSpec], quantum: int = 1, cores: int = 1) -> Tuple[List[TimelineSlice], Tuple[float, float]]:
    t = 0
    queue: List[ProcSpec] = []
    rem = {p.pid: p.burst for p in specs}
    slices = []
    i = 0
    while True:
        arrivals = [p for p in specs if p.arrival == t]
        queue.extend(arrivals)
        if queue:
            p = queue.pop(0)
            start = t
            run = min(quantum, rem[p.pid])
            t += run
            rem[p.pid] -= run
            slices.append(TimelineSlice(pid=p.pid, start=start, end=t, core=0))
            arrivals2 = [x for x in specs if x.arrival > start and x.arrival <= t]
            queue.extend(arrivals2)
            if rem[p.pid] > 0:
                queue.append(p)
        else:
            pending = [p for p in specs if rem[p.pid] > 0]
            if not pending:
                break
            t = min([p.arrival for p in pending])
        i += 1
        if i > 100000:
            break
    return slices, _metrics(specs, slices)


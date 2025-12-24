from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from oslab.models.process import ProcSpec
from oslab.sim.scheduler import fcfs, rr, sjf, priority
from oslab.sim.process_sim import ProcessSimulator
from oslab.sim.ipc import IPCSimulator
from oslab.sim.semaphore_sim import SemaphoreSimulator

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
psim = ProcessSimulator()
ipc = IPCSimulator()
sem = SemaphoreSimulator()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/schedule")
async def schedule(payload: dict):
    arrivals = payload.get("arrivals", [])
    bursts = payload.get("bursts", [])
    priorities = payload.get("priorities", [])
    cores = int(payload.get("cores", 1))
    quantum = int(payload.get("quantum", 1))
    algo = payload.get("algo", "fcfs")
    n = max(len(arrivals), len(bursts), len(priorities))
    if n == 0:
        specs = [ProcSpec(1,0,5,2), ProcSpec(2,2,3,1), ProcSpec(3,4,2,3)]
    else:
        specs = [
            ProcSpec(i+1,
                     arrivals[i] if i < len(arrivals) else 0,
                     bursts[i] if i < len(bursts) else 1,
                     priorities[i] if i < len(priorities) else 0)
            for i in range(n)
        ]
    if algo == "fcfs":
        slices, metrics = fcfs(specs, cores=cores)
    elif algo == "rr":
        slices, metrics = rr(specs, quantum=quantum)
    elif algo == "sjf":
        slices, metrics = sjf(specs)
    elif algo == "priority":
        slices, metrics = priority(specs)
    else:
        slices, metrics = fcfs(specs, cores=cores)
    return {
        "slices": [{"pid": s.pid, "start": s.start, "end": s.end, "core": s.core} for s in slices],
        "metrics": {"wait": metrics[0], "turn": metrics[1]}
    }

@app.post("/api/proc/start")
async def proc_start():
    psim.reset()
    psim.resume()
    psim.start(6)
    return {"ok": True}

@app.post("/api/proc/resume")
async def proc_resume():
    psim.resume()
    return {"ok": True}

@app.post("/api/proc/pause")
async def proc_pause():
    psim.pause()
    return {"ok": True}

@app.post("/api/proc/reset")
async def proc_reset():
    psim.reset()
    return {"ok": True}

@app.post("/api/proc/speed")
async def proc_speed(payload: dict):
    if "factor" in payload:
        try:
            psim.speed = float(payload["factor"]) or 1.0
        except Exception:
            pass
    else:
        if payload.get("op") == "up":
            psim.speed_up()
        else:
            psim.speed_down()
    return {"ok": True}

@app.get("/api/proc/events")
async def proc_events():
    out = []
    i = 0
    while not psim.events.empty() and i < 128:
        out.append(psim.events.get())
        i += 1
    return {"events": out}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

@app.post("/api/ipc/start")
async def ipc_start():
    ipc.reset()
    ipc.start()
    return {"ok": True}

@app.post("/api/ipc/resume")
async def ipc_resume():
    ipc.resume()
    return {"ok": True}

@app.post("/api/ipc/pause")
async def ipc_pause():
    ipc.pause()
    return {"ok": True}

@app.post("/api/ipc/reset")
async def ipc_reset():
    ipc.reset()
    return {"ok": True}

@app.post("/api/ipc/speed")
async def ipc_speed(payload: dict):
    if "factor" in payload:
        try:
            ipc.speed = float(payload["factor"]) or 1.0
        except Exception:
            pass
    else:
        if payload.get("op") == "up":
            ipc.speed_up()
        else:
            ipc.speed_down()
    return {"ok": True}

@app.get("/api/ipc/state")
async def ipc_state():
    return {"size": ipc.buffer.qsize(), "cap": ipc.buffer.maxsize}

@app.get("/api/ipc/events")
async def ipc_events():
    out = []
    i = 0
    while not ipc.events.empty() and i < 128:
        out.append(ipc.events.get())
        i += 1
    return {"events": out}

@app.post("/api/sem/start")
async def sem_start():
    sem.reset()
    sem.start()
    return {"ok": True}

@app.post("/api/sem/resume")
async def sem_resume():
    sem.resume()
    return {"ok": True}

@app.post("/api/sem/pause")
async def sem_pause():
    sem.pause()
    return {"ok": True}

@app.post("/api/sem/reset")
async def sem_reset():
    sem.reset()
    return {"ok": True}

@app.post("/api/sem/speed")
async def sem_speed(payload: dict):
    if "factor" in payload:
        try:
            sem.speed = float(payload["factor"]) or 1.0
        except Exception:
            pass
    else:
        if payload.get("op") == "up":
            sem.speed_up()
        else:
            sem.speed_down()
    return {"ok": True}

@app.get("/api/sem/state")
async def sem_state():
    return {"value": sem.sem.value, "blocked": list(sem._blocked)}

@app.get("/api/sem/events")
async def sem_events():
    out = []
    i = 0
    while not sem.events.empty() and i < 128:
        out.append(sem.events.get())
        i += 1
    return {"events": out}

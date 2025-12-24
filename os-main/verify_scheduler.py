from oslab.sim.scheduler import fcfs, rr, sjf, priority
from oslab.models.process import ProcSpec

specs = [ProcSpec(1,0,5,2), ProcSpec(2,2,3,1), ProcSpec(3,4,2,3)]
s, m = fcfs(specs)
print("FCFS", len(s), f"{m}")
s, m = rr(specs, quantum=2)
print("RR", len(s), f"{m}")
s, m = sjf(specs)
print("SJF", len(s), f"{m}")
s, m = priority(specs)
print("PRI", len(s), f"{m}")


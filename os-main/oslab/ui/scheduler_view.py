from textual.widgets import TabPane, DataTable, Button, Input, Static
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult
from textual.reactive import reactive
from oslab.sim.scheduler import fcfs, rr, sjf, priority
from oslab.models.process import ProcSpec

class SchedulerView(TabPane):
    speed = reactive(1.0)
    def __init__(self, title: str):
        super().__init__(title=title)
        self._specs = [ProcSpec(1,0,5,2), ProcSpec(2,2,3,1), ProcSpec(3,4,2,3)]
        self._gantt = Static()
        self._metrics = Static()

    def compose(self) -> ComposeResult:
        table = DataTable(id="specs")
        table.add_columns("PID","到达","执行","优先级")
        for p in self._specs:
            table.add_row(str(p.pid), str(p.arrival), str(p.burst), str(p.priority))
        controls = Horizontal(
            Input(placeholder="核数", id="cores"),
            Input(placeholder="到达CSV", id="arrivals"),
            Input(placeholder="执行CSV", id="bursts"),
            Input(placeholder="优先CSV", id="priorities"),
            Button("FCFS", id="run_fcfs"),
            Button("RR", id="run_rr"),
            Input(placeholder="时间片", id="quantum"),
            Button("SJF", id="run_sjf"),
            Button("优先级", id="run_pri")
        )
        yield Vertical(table, controls, self._gantt, self._metrics)

    def _render_gantt(self, slices):
        if not slices:
            self._gantt.update("")
            return
        total = max(s.end for s in slices)
        scale = max(1, int(60 / max(1,total)))
        out = ""
        colors = ["cyan","magenta","green","blue","yellow","red"]
        lanes = {}
        for s in slices:
            lanes.setdefault(s.core, []).append(s)
        for core, items in sorted(lanes.items()):
            out += f"Core {core}:\n"
            for s in items:
                width = max(1, (s.end - s.start) * scale)
                out += f" [white]{s.start}[/]"
                seg = f"[bold white on {colors[s.pid % len(colors)]}]P{s.pid}[/]"
                out += seg * width
                out += f"[white]{s.end}[/]\n"
        self._gantt.update(out)

    def on_button_pressed(self, event: Button.Pressed):
        btn = event.button.id
        if btn == "run_fcfs":
            cores = 1
            inp = self.query_one("#cores", Input)
            try:
                if inp.value:
                    cores = max(1, int(inp.value))
            except Exception:
                cores = 1
            self._apply_inputs()
            s, m = fcfs(self._specs, cores=cores)
            self._render_gantt(s)
            self._metrics.update(f"等待:{m[0]:.2f} 周转:{m[1]:.2f}")
        elif btn == "run_rr":
            q = 1
            inp = self.query_one("#quantum", Input)
            try:
                if inp.value:
                    q = int(inp.value)
            except Exception:
                q = 1
            self._apply_inputs()
            s, m = rr(self._specs, quantum=q)
            self._render_gantt(s)
            self._metrics.update(f"等待:{m[0]:.2f} 周转:{m[1]:.2f}")
        elif btn == "run_sjf":
            self._apply_inputs()
            s, m = sjf(self._specs)
            self._render_gantt(s)
            self._metrics.update(f"等待:{m[0]:.2f} 周转:{m[1]:.2f}")
        elif btn == "run_pri":
            self._apply_inputs()
            s, m = priority(self._specs)
            self._render_gantt(s)
            self._metrics.update(f"等待:{m[0]:.2f} 周转:{m[1]:.2f}")

    def pause(self):
        pass

    def resume(self):
        pass

    def reset(self):
        self._gantt.update("")
        self._metrics.update("")

    def speed_up(self):
        self.speed *= 1.2

    def speed_down(self):
        self.speed /= 1.2

    def _apply_inputs(self):
        arr = self.query_one("#arrivals", Input).value or ""
        bur = self.query_one("#bursts", Input).value or ""
        pri = self.query_one("#priorities", Input).value or ""
        try:
            arrs = [int(x) for x in arr.split(',') if x.strip()]
            burs = [int(x) for x in bur.split(',') if x.strip()]
            pris = [int(x) for x in pri.split(',') if x.strip()]
            n = max(len(arrs), len(burs), len(pris))
            if n:
                specs = []
                for i in range(n):
                    a = arrs[i] if i < len(arrs) else 0
                    b = burs[i] if i < len(burs) else 1
                    p = pris[i] if i < len(pris) else 0
                    specs.append(ProcSpec(i+1, a, b, p))
                self._specs = specs
                table = self.query_one("#specs", DataTable)
                table.clear()
                table.add_columns("PID","到达","执行","优先级")
                for s in self._specs:
                    table.add_row(str(s.pid), str(s.arrival), str(s.burst), str(s.priority))
        except Exception:
            pass

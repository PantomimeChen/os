from textual.widgets import TabPane, DataTable, Button, Static
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from oslab.sim.semaphore_sim import SemaphoreSimulator

class SemaphoreView(TabPane):
    def __init__(self, title: str):
        super().__init__(title=title)
        self.sim = SemaphoreSimulator()
        self.sem_val = Static()
        self.blocked = DataTable()
        self.log_table = DataTable()

    def compose(self) -> ComposeResult:
        self.blocked.add_columns("阻塞角色","ID")
        self.log_table.add_columns("事件","详情")
        controls = Horizontal(Button("开始", id="start"), Button("暂停", id="pause"), Button("重置", id="reset"))
        yield Vertical(self.sem_val, self.blocked, self.log_table, controls)

    def _drain(self):
        while not self.sim.events.empty():
            ev = self.sim.events.get()
            self.sem_val.update(f"信号量值: {ev.get('sem', self.sim.sem.value)}")
            t = ev["type"]
            if t == "try":
                self.log_table.add_row("尝试", f"{ev['role']}{ev['id']}")
            elif t == "acquire":
                self.log_table.add_row("获取", f"{ev['role']}{ev['id']}")
            elif t == "release":
                self.log_table.add_row("释放", f"{ev['role']}{ev['id']}")
        self._render_blocked()

    def _render_blocked(self):
        self.blocked.clear()
        for role, idx in list(self.sim._blocked):
            self.blocked.add_row(role, str(idx))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            self.sim.start()
            self.set_interval(0.1, self._drain)
        elif event.button.id == "pause":
            self.sim.pause()
        elif event.button.id == "reset":
            self.sim.reset()
            self.blocked.clear(); self.log_table.clear(); self.sem_val.update("")

    def pause(self):
        self.sim.pause()

    def resume(self):
        self.sim.resume()

    def reset(self):
        self.sim.reset(); self.blocked.clear(); self.log_table.clear(); self.sem_val.update("")

    def speed_up(self):
        self.sim.speed_up()

    def speed_down(self):
        self.sim.speed_down()

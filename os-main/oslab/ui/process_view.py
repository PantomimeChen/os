from textual.widgets import TabPane, DataTable, Button, Static
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.reactive import reactive
from oslab.sim.process_sim import ProcessSimulator

class ProcessView(TabPane):
    speed = reactive(1.0)
    def __init__(self, title: str):
        super().__init__(title=title)
        self.sim = ProcessSimulator()
        self.table = None
        self.log_view = None

    def compose(self) -> ComposeResult:
        self.table = DataTable(id="ptable")
        self.log_view = Static(id="plog")
        controls = Horizontal(Button("开始", id="start"), Button("暂停", id="pause"), Button("重置", id="reset"))
        yield Vertical(self.table, controls, self.log_view)

    def on_mount(self):
        self.table.add_columns("PID","状态")

    def _update_state(self, pid: int, state: str):
        row = None
        for r in self.table.rows:
            if self.table.get_cell_at(r, 0) == str(pid):
                row = r
                break
        if row is None:
            self.table.add_row(str(pid), state)
        else:
            self.table.update_cell(row, 1, state)
        self.log_view.update(f"PID {pid} -> {state}")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            self.sim.start(6)
            self.set_interval(0.1, self._drain)
        elif event.button.id == "pause":
            self.sim.pause()
        elif event.button.id == "reset":
            self.sim.reset()
            self.table.clear()
            self.log_view.update("")

    def _drain(self):
        while not self.sim.events.empty():
            ev = self.sim.events.get()
            self._update_state(ev["pid"], ev["state"])

    def pause(self):
        self.sim.pause()

    def resume(self):
        self.sim.resume()

    def reset(self):
        self.sim.reset()
        self.table.clear()
        self.log_view.update("")

    def speed_up(self):
        self.sim.speed_up()

    def speed_down(self):
        self.sim.speed_down()

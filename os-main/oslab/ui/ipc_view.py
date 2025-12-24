from textual.widgets import TabPane, DataTable, Button, Static
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from oslab.sim.ipc import IPCSimulator

class IPCView(TabPane):
    def __init__(self, title: str):
        super().__init__(title=title)
        self.sim = IPCSimulator()
        self.buf = DataTable(id="buf")
        self.log_table = DataTable(id="log")
        self.occ = Static()
        self.flow = Static()
        self._flow_lines = []

    def compose(self) -> ComposeResult:
        self.buf.add_columns("序号","值")
        self.log_table.add_columns("方向","数据")
        controls = Horizontal(Button("开始", id="start"), Button("暂停", id="pause"), Button("重置", id="reset"))
        self.occ.update("缓冲区占用: [white]|--------------------| 0%[/]")
        yield Vertical(self.buf, self.log_table, self.occ, self.flow, controls)

    def _drain(self):
        while not self.sim.events.empty():
            ev = self.sim.events.get()
            if ev["type"] == "produce":
                d = ev["data"]
                self.buf.add_row(str(d["seq"]), str(d["value"]))
                self.log_table.add_row("→", f"{d}")
                self._append_flow(f"[green]→ 生产 {d}[/]")
            else:
                d = ev["data"]
                if len(self.buf.rows):
                    self.buf.remove_row(0)
                self.log_table.add_row("←", f"{d}")
                self._append_flow(f"[blue]← 消费 {d}[/]")
        self._update_occ()

    def _update_occ(self):
        size = self.sim.buffer.qsize()
        cap = self.sim.buffer.maxsize
        width = 20
        fill = int(width * size / max(1, cap))
        bar = "|" + "█" * fill + "-" * (width - fill) + "|"
        percent = int(100 * size / max(1, cap))
        self.occ.update(f"缓冲区占用: [yellow]{bar}[/] {percent}%")

    def _append_flow(self, line: str):
        self._flow_lines.append(line)
        if len(self._flow_lines) > 20:
            self._flow_lines.pop(0)
        self.flow.update("\n".join(self._flow_lines))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            self.sim.start()
            self.set_interval(0.1, self._drain)
        elif event.button.id == "pause":
            self.sim.pause()
        elif event.button.id == "reset":
            self.sim.reset()
            self.buf.clear(); self.log_table.clear(); self.flow.update(""); self._flow_lines.clear(); self._update_occ()

    def pause(self):
        self.sim.pause()

    def resume(self):
        self.sim.resume()

    def reset(self):
        self.sim.reset(); self.buf.clear(); self.log_table.clear(); self.flow.update(""); self._flow_lines.clear(); self._update_occ()

    def speed_up(self):
        self.sim.speed_up()

    def speed_down(self):
        self.sim.speed_down()

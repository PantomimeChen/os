from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Button
from textual.containers import Container
from oslab.ui.scheduler_view import SchedulerView
from oslab.ui.process_view import ProcessView
from oslab.ui.ipc_view import IPCView
from oslab.ui.semaphore_view import SemaphoreView

class OSShowcaseApp(App):
    CSS_PATH = None
    BINDINGS = [
        ("s", "export_html", "Export HTML"),
        ("p", "pause_all", "Pause"),
        ("r", "resume_all", "Resume"),
        ("x", "reset_all", "Reset"),
        ("+", "speed_up", "Speed+"),
        ("-", "speed_down", "Speed-")
    ]

    def __init__(self):
        super().__init__()
        self._views = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Button("Pause", id="pause"),
            Button("Resume", id="resume"),
            Button("Reset", id="reset"),
            Button("Speed+", id="speed_plus"),
            Button("Speed-", id="speed_minus"),
        )
        with TabbedContent():
            v1 = SchedulerView(title="CPU 调度")
            v2 = ProcessView(title="进程与线程")
            v3 = IPCView(title="进程间通信")
            v4 = SemaphoreView(title="信号量同步")
            self._views = [v1, v2, v3, v4]
            yield v1
            yield v2
            yield v3
            yield v4
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pause":
            self.action_pause_all()
        elif event.button.id == "resume":
            self.action_resume_all()
        elif event.button.id == "reset":
            self.action_reset_all()
        elif event.button.id == "speed_plus":
            self.action_speed_up()
        elif event.button.id == "speed_minus":
            self.action_speed_down()

    def action_pause_all(self) -> None:
        for v in self._views:
            v.pause()

    def action_resume_all(self) -> None:
        for v in self._views:
            v.resume()

    def action_reset_all(self) -> None:
        for v in self._views:
            v.reset()

    def action_speed_up(self) -> None:
        for v in self._views:
            v.speed_up()

    def action_speed_down(self) -> None:
        for v in self._views:
            v.speed_down()

    def action_export_html(self) -> None:
        from datetime import datetime
        from rich.console import Console
        from rich.tree import Tree
        import os
        console = Console(record=True)
        tree = Tree("OS Showcase")
        for v in self._views:
            tree.add(v.title)
        console.print(tree)
        os.makedirs("exports", exist_ok=True)
        console.save_html(f"exports/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

if __name__ == "__main__":
    OSShowcaseApp().run()

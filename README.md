# 操作系统实验展示（OS Showcase）

本仓库包含一个用于演示操作系统核心概念的教学与展示项目，支持
- Web 交互界面（基于 `FastAPI` + `Jinja2`）

涵盖模块：
- CPU 调度：FCFS、RR、SJF（`oslab/sim/scheduler.py`）
- 进程与线程状态机：创建/就绪/运行/阻塞/终止（`oslab/sim/process_sim.py`）
- 进程间通信：生产者-消费者缓冲区（`oslab/sim/ipc.py`）
- 信号量同步：计数信号量与阻塞队列（`oslab/sim/semaphore_sim.py`）

## 目录结构
- `os-main/app.py`：TUI 入口，提供统一控制与四个页签视图
- `os-main/oslab/ui/*_view.py`：各模块的 UI 视图
- `os-main/oslab/sim/*.py`：各模块的模拟器逻辑
- `os-main/oslab/models/process.py`：进程与调度模型
- `os-main/web/server.py`：Web 服务入口与 API
- `os-main/web/templates/index.html`：Web 前端页面
- `os-main/verify_scheduler.py`：调度算法快速验证脚本
- `os-main/*.spec`：PyInstaller 打包配置
- `os-main/dist/OSShowcase-ProcTable.exe`：已构建示例（Windows）

## 环境依赖
- Python 3.9+
- 依赖包（见 `os-main/requirements.txt`）：
  - `textual`、`rich`（TUI 与渲染）
  - `fastapi`、`uvicorn`、`jinja2`（Web 与模板）
  - `pyinstaller`（可选：打包）

安装依赖：
```
python -m venv .venv
.venv\Scripts\activate
pip install -r os-main/requirements.txt
```

## 运行方式
### 1) 终端界面（TUI）
```
python os-main/app.py
```
- 快捷键：`s` 导出HTML、`p` 暂停、`r` 继续、`x` 重置、`+` 加速、`-` 减速（`os-main/app.py:11`）
- 视图页签：CPU 调度、进程与线程、进程间通信、信号量同步
  - 调度视图交互：见 `os-main/oslab/ui/scheduler_view.py:21`

### 2) Web 界面
开发模式（自动重载）：
```
python -m uvicorn os-main.web.server:app --reload
```
或直接运行：
```
python os-main/web/server.py
```
启动后访问 `http://127.0.0.1:8000/`，页面位于 `os-main/web/templates/index.html`。

## 快速验证
调度算法示例运行：
```
python os-main/verify_scheduler.py
```
相关接口实现：`os-main/oslab/sim/scheduler.py:17`（FCFS）、`83`（RR）、`29`（SJF）、`56`（优先级）

## 打包说明（可选）
使用 PyInstaller（已提供 `.spec` 文件）：
```
pip install pyinstaller
pyinstaller os-main/OSShowcase-ProcTable.spec
pyinstaller os-main/OSShowcase.spec
```
如需修改入口脚本：
- TUI 可使用 `app.py` 作为入口（`OSShowcase-ProcTable.spec`）
- Web 可使用 `web/server.py` 作为入口（`OSShowcase.spec`）
并确保模板资源通过 `datas=[('web\\templates','web\\templates')]` 打包。

## 备注
- Web 端提供统一播放/暂停与速度调节，后台接口见 `os-main/web/server.py:210-222`。
- 所有模拟器的速度控制与事件队列基于 `queue.Queue` 与线程实现，避免复杂依赖，易于扩展。


---
type: Reference
title: systemd.py 源码信源
description: tljh/systemd.py 模块公共 API 信源文档
tags: [reference, source, systemd, service-management, api]
sources:
  - id: tljh-systemd
    title: tljh/systemd.py
---

# systemd.py 源码信源

> Systemd 服务管理模块。封装 systemctl 命令，提供服务安装、启动/停止、启用/禁用和状态检查功能。

## 公共函数

所有函数通过 `subprocess.check_call` 或 `subprocess.run` 执行 systemctl 命令。

### `reload_daemon()`

执行 `systemctl daemon-reload`。在安装或修改 unit 文件后调用。

### `install_unit(name, unit, path="/etc/systemd/system")`

将 unit 内容写入 `{path}/{name}` 文件。不自动 reload 或 restart。

### `uninstall_unit(name, path="/etc/systemd/system")`

删除 `{path}/{name}` 文件。使用 `os.remove` 而非 systemctl。

### `start_service(name)`

执行 `systemctl start {name}`。

### `stop_service(name)`

执行 `systemctl stop {name}`。

### `restart_service(name)`

执行 `systemctl restart {name}`。

### `enable_service(name)`

执行 `systemctl enable {name}`（设置开机自启）。

### `disable_service(name)`

执行 `systemctl disable {name}`（取消开机自启）。

### `check_service_active(name) → bool`

执行 `systemctl is-active {name}`：
- 返回码 0 → 返回 True
- CalledProcessError → 返回 False

### `check_service_enabled(name) → bool`

执行 `systemctl is-enabled {name}`：
- 返回码 0 → 返回 True
- CalledProcessError → 返回 False

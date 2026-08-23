---
type: reference
title: "命令执行工具源码（jupyterlab_latex/util.py）"
description: "跨平台 LaTeX/SyncTeX 子进程执行封装，Windows 同步回退与非 Windows 异步执行的自动切换"
tags: [subprocess, async, sync, windows, tornado, command-execution]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: util-py
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/util.py"
    title: "jupyterlab_latex/util.py"
---

# 命令执行工具源码（jupyterlab_latex/util.py）

本信源登记 `jupyterlab_latex/util.py`（约62行），提供跨平台子进程命令执行功能，自动在 Windows 同步模式和 Unix 异步模式之间切换。

## 导出函数

### run_command_sync(cmd)

`@gen.coroutine` 同步执行命令（Windows 回退方案）：

- 使用 `subprocess.run(cmd, stdout=subprocess.PIPE)` 执行
- `CalledProcessError` 被捕获但 pass（不中断）
- 返回 `(return_code, stdout_decoded_utf8)` 元组

### run_command_async(cmd)

`@gen.coroutine` 异步执行命令（Unix/Linux/macOS 推荐方案）：

- 使用 `tornado.process.Subprocess(cmd, stdout=Subprocess.STREAM, stderr=Subprocess.STREAM)`
- `yield process.wait_for_exit()` 等待完成
- `CalledProcessError` 被捕获但 pass
- `yield process.stdout.read_until_close()` 读取所有输出
- 返回 `(return_code, stdout_decoded_utf8)` 元组

### 平台自动选择

```python
if sys.platform == 'win32':
    run_command = run_command_sync
else:
    run_command = run_command_async
```

Windows 不支持 `tornado.process.Subprocess` 的异步子进程，因此使用同步 `subprocess.run` 作为回退。

## 注意事项

- stderr 被重定向到 stdout（`stderr=Subprocess.STREAM`），所有输出统一从 stdout 读取
- 两个函数都用 `@gen.coroutine` 装饰，返回 Future，调用方需用 `yield`
- `CalledProcessError` 被静默捕获，错误信息通过返回码和 stdout 传递给上层处理

---
okf_version: "0.2"
type: reference
title: "Echo内核源码（echo_kernel.py）"
description: "pytest_jupyter/echo_kernel.py 的完整API：EchoKernel回显内核类、EchoKernelApp启动类、do_execute方法实现"
tags: [echo-kernel, testing-kernel, ipykernel, kernel-base, do-execute, kernel-app]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: echo-kernel-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/echo_kernel.py"
    title: "pytest_jupyter/echo_kernel.py"
---

# Echo内核源码（echo_kernel.py）

本信源登记 `pytest_jupyter/echo_kernel.py`（约70行）的核心类和方法。echo_kernel.py 提供一个极简的回显（echo）测试内核，将收到的代码原样输出到stdout，用于快速测试而无需启动完整的IPython内核。

## 核心类

### class EchoKernel(Kernel)

继承自`ipykernel.kernelbase.Kernel`的简单回显内核。

**类属性：**

| 属性 | 值 | 说明 |
|------|-----|------|
| `implementation` | `"Echo"` | 内核实现名称 |
| `implementation_version` | `"1.0"` | 实现版本 |
| `language` | `"echo"` | 语言标识 |
| `language_version` | `"0.1"` | 语言版本 |
| `language_info` | `{"name": "echo", "mimetype": "text/plain", "file_extension": ".txt"}` | 语言信息字典 |
| `banner` | `"Echo kernel - as useful as a parrot"` | 内核启动横幅 |

[F-040]

#### do_execute(code, silent, store_history=True, user_expressions=None, allow_stdin=False, *, cell_id=None) -> dict

执行代码的核心方法（覆盖Kernel基类）。

**参数：**
- `code` (str): 要执行的代码字符串
- `silent` (bool): 是否静默执行（不输出结果）
- `store_history` (bool): 是否存储历史（未使用，标记noqa）
- `user_expressions`: 用户表达式（未使用）
- `allow_stdin` (bool): 是否允许stdin输入
- `cell_id` (str|None): 单元格ID（未使用）

**行为：**
1. 若非silent模式：
   a. 构造stream_content：`{"name": "stdout", "text": code}`
   b. 调用`self.send_response(self.iopub_socket, "stream", stream_content)`将code原样发送到stdout流
   c. 若`allow_stdin`为True且code不为空且包含`"input("`字符串：
      - 调用`self._input_request("Echo Prompt", self._parent_ident["shell"], self.get_parent(channel="shell"), password=False)`发送输入请求
2. 返回执行结果字典：
   ```python
   {
       "status": "ok",
       "execution_count": self.execution_count,
       "payload": [],
       "user_expressions": {},
   }
   ```

[F-041]

### class EchoKernelApp(IPKernelApp)

继承自`ipykernel.kernelapp.IPKernelApp`的内核应用类。

**类属性：**
- `kernel_class = EchoKernel`：指定使用EchoKernel作为内核类

[F-042]

### 模块入口（__main__）

```python
if __name__ == "__main__":
    logging.disable(logging.ERROR)
    EchoKernelApp.launch_instance()
```

- 禁用ERROR级别以下的日志输出
- 调用`EchoKernelApp.launch_instance()`启动内核应用

[F-043]

## 设计要点

1. **极简实现**：整个内核只有一个核心方法`do_execute`，类属性定义元信息
2. **原样回显**：收到的code直接作为stdout输出，不做任何解析或执行
3. **stdin支持**：检测code中是否包含`input(`调用来触发输入请求，支持需要用户输入的测试场景
4. **继承IPKernelApp**：通过设置`kernel_class = EchoKernel`复用IPKernelApp的完整启动逻辑（连接文件解析、ZMQ通道建立等）
5. **日志静音**：`__main__`入口中禁用非ERROR日志，避免测试输出被内核日志污染
6. **测试加速**：相比启动完整IPython内核，echo内核启动极快，适合需要大量内核生命周期测试的场景

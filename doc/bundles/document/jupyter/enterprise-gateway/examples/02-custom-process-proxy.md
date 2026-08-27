---
okf_version: "0.2"
type: "example"
title: "编写自定义ProcessProxy"
description: "通过继承RemoteProcessProxy实现自定义进程代理，对接新的计算平台，完整实现launch_process和confirm_remote_startup方法"
tags: [example, process-proxy, custom, extension, plugin, remote]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
  - id: process-proxy-concept
    resource: "/concepts/04-process-proxy.md"
    title: "ProcessProxy进程代理体系"
  - id: response-manager
    resource: "/references/response-manager-source.md"
    title: "ResponseManager源码"
---

# 编写自定义ProcessProxy

本示例演示如何编写自定义ProcessProxy，将内核调度到自定义的远程计算平台。我们将创建一个 `MyCustomProcessProxy`，通过自定义API启动远程内核。

## ProcessProxy接口回顾

编写自定义ProcessProxy需要理解以下核心接口（参见 [ProcessProxy进程代理体系](../concepts/04-process-proxy.md)）：

| 方法 | 必须实现 | 说明 |
|------|---------|------|
| `__init__(kernel_manager, proxy_config)` | 是 | 初始化，接收kernel_manager和config字典 |
| `launch_process(kernel_cmd, **kwargs)` | 是 | 启动远程进程，返回self |
| `confirm_remote_startup()` | 是（远程场景） | 等待启动完成，获取连接信息 |
| `poll()` | 通常需要覆写 | 检查进程存活状态 |
| `kill()` | 可能需要覆写 | 强制终止进程 |
| `terminate()` | 可能需要覆写 | 优雅终止 |
| `get_process_info()` | 推荐实现 | HA持久化支持 |
| `load_process_info(info)` | 推荐实现 | HA恢复支持 |
| `cleanup()` | 按需 | 清理资源 |
| `send_signal(signum)` | 通常需要覆写 | 向远程进程发送信号 |

## 实现CustomProcessProxy

以下是一个完整的自定义ProcessProxy示例，假设我们通过一个HTTP API来启动和管理远程内核：

```python
# my_custom_process_proxy.py
import asyncio
import json
import time
import requests
from tornado import web
from enterprise_gateway.services.processproxies.processproxy import RemoteProcessProxy


class MyCustomProcessProxy(RemoteProcessProxy):
    """
    自定义ProcessProxy：通过HTTP API在远程计算平台上启动内核。
    
    proxy_config配置示例（在kernelspec的kernel.json中）：
    {
      "class_name": "my_package.my_custom_process_proxy.MyCustomProcessProxy",
      "config": {
        "api_endpoint": "https://my-compute-platform.example.com/api/kernels",
        "api_token": "my-platform-token",
        "launch_timeout": 60
      }
    }
    """

    def __init__(self, kernel_manager, proxy_config):
        super().__init__(kernel_manager, proxy_config)
        
        # 从proxy_config中读取自定义配置
        self.api_endpoint = proxy_config.get('api_endpoint', 'http://localhost:9000/api/kernels')
        self.api_token = proxy_config.get('api_token', '')
        self.launch_timeout = proxy_config.get('launch_timeout', 60)
        
        # 远程进程标识
        self.remote_job_id = None
        self.remote_host = None

    async def launch_process(self, kernel_cmd, **kwargs):
        """
        通过自定义API在远程平台启动内核。
        """
        # 1. 执行用户授权检查（基类方法）
        self._enforce_authorization()

        # 2. 准备启动命令参数
        # RemoteProcessProxy构造函数已设置response_address和public_key
        env = kwargs.get('env', {})
        
        launch_payload = {
            "kernel_id": self.kernel_manager.kernel_id,
            "command": kernel_cmd,
            "response_address": self.kernel_manager.response_address,
            "public_key": self.kernel_manager.public_key,
            "port_range": self.kernel_manager.port_range,
            "env": env,
            "username": env.get("KERNEL_USERNAME", "default")
        }

        # 3. 调用远程API启动内核
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=launch_payload,
                headers=headers,
                timeout=self.launch_timeout
            )
            response.raise_for_status()
            result = response.json()
            
            self.remote_job_id = result["job_id"]
            self.remote_host = result.get("host", "unknown")
            self.log.info(f"Started remote kernel job {self.remote_job_id} on {self.remote_host}")
        except requests.RequestException as e:
            self.log.error(f"Failed to start remote kernel: {e}")
            raise web.HTTPError(500, f"Failed to start kernel on remote platform: {e}")

        # 4. 等待远程启动完成（接收连接信息）
        await self.confirm_remote_startup()
        return self

    async def confirm_remote_startup(self):
        """
        等待ResponseManager收到launcher回传的连接信息。
        对于自定义平台，如果launcher自动回传（使用EG标准的RSA+AES协议），
        可以直接使用基类的等待逻辑。
        """
        # 方式1：如果远程launcher使用EG标准加密回传协议，
        # 只需轮询ResponseManager等待连接信息
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > self.kernel_manager.kernel_launch_timeout:
                error_message = f"Kernel startup timeout after {elapsed:.1f} seconds"
                self.log.error(error_message)
                # 清理失败的远程任务
                await self._kill_remote_job()
                raise TimeoutError(error_message)

            # 检查本地启动进程是否异常退出
            self.detect_launch_failure()

            # 从ResponseManager获取连接信息（非阻塞轮询）
            connection_info = await self.response_manager.get_connection_info(
                self.kernel_manager.kernel_id
            )
            if connection_info:
                self.log.info(f"Received connection info from remote launcher for {self.kernel_manager.kernel_id}")
                # 记录远程进程信息
                self.ip = connection_info.get("ip", self.remote_host)
                self.pid = connection_info.get("pid", 0)
                self.pgid = connection_info.get("pgid", 0)
                
                # 更新kernel_manager的连接信息
                self._update_connection(connection_info)
                return

            await asyncio.sleep(0.5)  # 500ms轮询间隔

    def _update_connection(self, connection_info):
        """更新kernel_manager的连接信息（如果需要SSH隧道等）。"""
        # 如果远程平台提供直接网络可达性，不需要SSH隧道
        # 如果需要SSH隧道，调用_create_ssh_tunnel等基类方法
        # 此处假设远程端口直接可达
        self.kernel_manager._connection_info = connection_info

    def poll(self):
        """
        检查远程内核进程是否存活。
        返回None表示存活，返回int表示退出码。
        """
        if self.remote_job_id is None:
            return None  # 未启动

        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            response = requests.get(
                f"{self.api_endpoint}/{self.remote_job_id}/status",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            status = response.json().get("status", "unknown")
            
            if status in ("running", "starting"):
                return None  # 存活
            elif status in ("completed", "succeeded"):
                return 0  # 正常退出
            else:
                return 1  # 异常退出
        except requests.RequestException:
            return 1  # 查询失败，视为进程已退出

    async def kill(self):
        """强制终止远程内核进程。"""
        await self._kill_remote_job()
        self.cleanup()

    async def terminate(self):
        """优雅终止远程内核进程。"""
        # 先尝试优雅关闭
        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            requests.post(
                f"{self.api_endpoint}/{self.remote_job_id}/terminate",
                headers=headers,
                timeout=10
            )
            # 等待进程退出
            for _ in range(10):
                if self.poll() is not None:
                    break
                await asyncio.sleep(1)
            else:
                # 超时后强制杀死
                await self._kill_remote_job()
        except Exception:
            await self._kill_remote_job()

    async def _kill_remote_job(self):
        """调用远程API杀死任务。"""
        if self.remote_job_id is None:
            return
        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            requests.delete(
                f"{self.api_endpoint}/{self.remote_job_id}",
                headers=headers,
                timeout=10
            )
        except Exception as e:
            self.log.warning(f"Failed to kill remote job {self.remote_job_id}: {e}")

    def send_signal(self, signum):
        """向远程进程发送信号。"""
        if self.remote_job_id is None:
            return
        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            requests.post(
                f"{self.api_endpoint}/{self.remote_job_id}/signal",
                json={"signal": signum},
                headers=headers,
                timeout=10
            )
        except Exception as e:
            self.log.warning(f"Failed to send signal {signum} to {self.remote_job_id}: {e}")

    def get_process_info(self):
        """返回进程信息用于HA持久化。"""
        info = super().get_process_info()
        info["remote_job_id"] = self.remote_job_id
        return info

    def load_process_info(self, process_info):
        """从持久化数据恢复进程状态。"""
        super().load_process_info(process_info)
        self.remote_job_id = process_info.get("remote_job_id")

    def cleanup(self):
        """清理资源。"""
        self.log.info(f"Cleaning up custom process proxy for {self.kernel_manager.kernel_id}")
        super().cleanup()
```

## 配置kernelspec使用自定义ProcessProxy

创建kernelspec目录和kernel.json：

```bash
mkdir -p /usr/local/share/jupyter/kernels/python_custom
```

创建 `/usr/local/share/jupyter/kernels/python_custom/kernel.json`：

```json
{
  "argv": [
    "python",
    "/opt/launchers/launch_ipykernel.py",
    "--kernel-id", "{kernel_id}",
    "--port-range", "{port_range}",
    "--response-address", "{response_address}",
    "--public-key", "{public_key}"
  ],
  "display_name": "Python on My Platform",
  "language": "python",
  "metadata": {
    "process_proxy": {
      "class_name": "my_package.my_custom_process_proxy.MyCustomProcessProxy",
      "config": {
        "api_endpoint": "https://my-compute-platform.example.com/api/kernels",
        "api_token": "${MY_PLATFORM_TOKEN}",
        "launch_timeout": 60
      }
    }
  }
}
```

关键要点：
- `class_name` 必须是Python可导入的完整类路径
- `config` 字典会作为 `proxy_config` 参数传递给ProcessProxy构造函数
- argv中的 `{response_address}`, `{public_key}`, `{port_range}`, `{kernel_id}` 由RemoteKernelManager.format_kernel_cmd()替换

## 注册自定义ProcessProxy包

确保包含MyCustomProcessProxy的Python包安装在EG的Python环境中：

```bash
pip install -e /path/to/my_package  # 开发模式
# 或
pip install my_package              # 正式安装
```

## 验证

1. 重启EG
2. 查看kernelspec列表：
   ```bash
   curl http://localhost:8888/api/kernelspecs | python -m json.tool
   ```
   应该看到 `python_custom` kernelspec

3. 创建内核：
   ```bash
   curl -X POST http://localhost:8888/api/kernels \
     -H "Content-Type: application/json" \
     -d '{"name": "python_custom", "env": {"KERNEL_USERNAME": "testuser"}}'
   ```

4. 观察EG日志，确认MyCustomProcessProxy被实例化并调用了自定义API

## Launcher要求

你的远程计算平台上的launcher必须：
1. 接收 `--response-address`, `--public-key`, `--port-range`, `--kernel-id` 命令行参数
2. 启动内核进程（ipykernel/IRkernel/Toree）
3. 在port-range内选择5个ZMQ端口
4. 使用RSA+AES加密将连接信息回传到response-address

如果你想复用EG标准launcher，可以使用 `etc/kernel-launchers/` 下的launch_ipykernel.py等脚本。加密回传协议参见 [加密通信机制](../concepts/06-response-manager.md)。

## 设计要点

1. **授权检查**：在launch_process开头调用 `_enforce_authorization()` 确保用户权限
2. **启动超时**：confirm_remote_startup中必须有超时逻辑，防止永久等待
3. **失败检测**：使用 `detect_launch_failure()` 检查本地启动进程异常退出
4. **HA支持**：实现get_process_info/load_process_info以支持HA模式
5. **资源清理**：在kill/terminate/cleanup中确保远程资源被释放
6. **日志记录**：关键操作添加日志，便于排查问题

## 不使用SSH隧道的场景

如果你的远程平台提供直接网络可达性（如容器overlay网络），不需要SSH隧道。在这种情况下：
- 不需要设置self.tunnel_sockets等
- 只需要将connection_info中的ip设为远程主机可达地址
- ZMQChannelsHandler会直接连接该IP的端口

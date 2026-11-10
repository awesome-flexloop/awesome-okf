---
type: spec
title: "SWE-ReX 事实清单"
---

# SWE-ReX 事实清单

> 信源根目录：`D:/spaces/SpecWeave/external/dao/SWE-agent/SWE-ReX/`
> 采集日期：2026-11-10。所有事实带文件路径与行号（相对信源根目录），只记录代码/文档中存在的文本与结构，不含因果推断。

## 项目元信息与规模

F-001: `pyproject.toml` 第7行，项目名 `swe-rex`；第9行描述 "Sandboxed code execution for AI agents, locally or on the cloud."；第11行 `requires-python = ">=3.10"`。

F-002: `pyproject.toml` 第30行分类器 `License :: OSI Approved :: MIT License`；`pyproject.toml` 第13行 `license = {file = "LICENSE"}`。

F-003: `pyproject.toml` 第33-41行，运行时依赖 8 项：`fastapi`、`uvicorn`、`requests`、`pydantic>=2`、`pexpect`、`bashlex`、`python-multipart`、`rich`。

F-004: `pyproject.toml` 第60-69行，可选依赖组 `modal`（`modal>=1.0`、`boto3`）、`fargate`（`boto3`）、`daytona`（`daytona`、`daytona-sdk >= 0.21`）。

F-005: `pyproject.toml` 第92行控制台脚本 `swerex-remote = "swerex.server:main"`。

F-006: `src/swerex/__init__.py` 第1行 `__version__ = "1.4.0"`；第4行 `REMOTE_EXECUTABLE_NAME = "swerex-remote"`；第5行 `PACKAGE_NAME = "swe-rex"`。

F-007: 源码快照 `git describe --tags --always` 输出 `v1.4.0-18-g5c995c3`；HEAD commit `5c995c365dfb1fd5bc56fda688be5d8538f9931f`，提交时间 2026-03-02；`v1.4.0` 标签指向提交日期 2025-08-13。

F-008: `CHANGELOG.md` 第3行最新条目为 `## 1.2.1 (03/04/25)`；文件内没有 1.3.0、1.4.0 条目。

F-009: 脚本统计 `src/` 下 `.py` 文件 29 个、总行 3,715 行、非空行 3,052 行。

F-010: 脚本统计仓库内 `.py` 与 `.md` 文件合计 5,328 行（排除 `.git/`）。

F-011: 脚本统计 `tests/` 下 `.py` 文件 13 个，`def test_` / `async def test_` 用例 89 个。

F-012: 测试用例按文件分布：`test_execution.py` 50、`test_runtime.py` 12、`test_docker_deployment.py` 9、`test_get_deployment.py` 6、`test_server.py` 3、`test_fargate_deployment.py` 2、`test_local_runtime.py` 2、`test_modal_deployment.py` 2、`test_dummy_deployment.py` 1、`test_local_deployment.py` 1、`test_remote_deployment.py` 1。

F-013: `docs/` 下 Markdown 文件 20 个（含 `_footer.md`、`SECURITY.md` 与 17 个页面/API 存根）。

F-014: `src/swerex/runtime/remote.py` 第12行 `import aiohttp`；`pyproject.toml` 第33-41行依赖列表不含 `aiohttp`。

F-015: 10 个源码文件从 `typing_extensions` 导入 `Self`（daytona/docker/dummy/fargate/local/modal/remote 的 deployment 文件，runtime/dummy.py、runtime/local.py、runtime/remote.py）；`pyproject.toml` 依赖列表不含 `typing_extensions`。

F-016: `tests/test_server.py` 第1行 `import requests`；`src/` 下无 `requests.` 调用（脚本统计 0 处）。

## 部署抽象（Deployment）

F-017: `src/swerex/deployment/abstract.py` 第11行 `class AbstractDeployment(ABC)`；第16行 `add_hook`；第19行 `is_alive`；第28行 `start`；第32行 `stop`；第37行 `runtime` 属性。

F-018: `src/swerex/deployment/abstract.py` 第44-60行 `__del__` 在对象删除时尝试创建 `stop()` 任务或运行事件循环；异常被捕获后忽略。

F-019: `src/swerex/deployment/local.py` 第54-56行 `LocalDeployment.start()` 直接创建 `LocalRuntime(logger=self.logger)`；第58-62行 `stop()` 调用 `runtime.close()`。

F-020: `src/swerex/deployment/docker.py` 第233-283行 `DockerDeployment.start()` 依次执行：拉取镜像、可选构建 standalone Python 镜像、分配空闲端口、生成容器名与 token、`docker run -p <port>:8000`、启动 `RemoteRuntime(host=docker_internal_host, port=port)`、等待 alive。

F-021: `src/swerex/deployment/docker.py` 第120-131行启动命令为 `swerex-remote --auth-token <token> || (python3 -m pip install pipx && python3 -m pipx ensurepath && pipx run swe-rex --auth-token <token>)`；若配置 `python_standalone_dir`，改用 `<dir>/python3.11/bin/swerex-remote`。

F-022: `src/swerex/deployment/docker.py` 第149-194行 `glibc_dockerfile` 属性在 `python:3.11.9-slim-bookworm` 构建阶段编译 Python 3.11.8 到 `/root/python3.11`，复制到目标镜像并安装 `swe-rex`。

F-023: `src/swerex/deployment/config.py` 第23-58行 `DockerDeploymentConfig` 默认值：`image="python:3.11"`、`startup_timeout=180.0`、`pull="missing"`、`remove_container=True`、`container_runtime="docker"`、`exec_shell=["/bin/sh","-c"]`、`docker_internal_host="http://127.0.0.1"`。

F-024: `src/swerex/deployment/config.py` 第60-87行 `validate_platform_args` 把 `docker_args` 中的 `--platform` 值迁移到 `platform` 字段，同时指定两者时抛出 `ValueError`。

F-025: `src/swerex/deployment/modal.py` 第208-247行 `ModalDeployment.start()` 调用 `modal.Sandbox.create.aio`，通过 `sandbox.tunnels.aio()` 取端口隧道 URL，再创建 `RemoteRuntime(host=tunnel.url)`。

F-026: `src/swerex/deployment/config.py` 第95-127行 `ModalDeploymentConfig` 默认值：`image="python:3.11"`、`startup_timeout=180.0`、`runtime_timeout=60.0`、`deployment_timeout=3600.0`、`install_pipx=True`。

F-027: `src/swerex/deployment/modal.py` 第32-108行 `_ImageBuilder.auto()` 接受 `modal.Image`、Dockerfile 路径、ECR 地址（含 `amazonaws.com`）或 registry 镜像名；`install_pipx` 为真时追加 `pipx` 安装。

F-028: `src/swerex/deployment/config.py` 第135-152行 `FargateDeploymentConfig` 默认值：`port=8880`、`cluster_name="swe-rex-cluster"`、`container_timeout=900.0`、`runtime_timeout=60.0`、`log_group="/ecs/swe-rex-deployment"`。

F-029: `src/swerex/deployment/fargate.py` 第105-118行启动命令为 `timeout <container_timeout>s bash -c 'swerex-remote --port <port> || (apt-get update -y && apt-get install pipx -y && pipx ensurepath && pipx run swe-rex --port <port> --auth-token <token>)'`。

F-030: `src/swerex/deployment/fargate.py` 第123-164行 `start()` 调用 `_init_aws()` 创建/复用 ECS cluster、IAM execution role、task definition、默认 VPC/子网、安全组，提交 Fargate task 后用 `tasks_running` waiter 等待，读取公网 IP 并连接 `RemoteRuntime`。

F-031: `src/swerex/deployment/daytona.py` 第97-140行 `start()` 创建 Daytona sandbox，创建 session 并以 `runAsync=True` 执行启动命令，用 `get_preview_link(port)` 得到 URL，再创建 `RemoteRuntime(host=..., port=None)`。

F-032: `src/swerex/deployment/config.py` 第198-208行 `DaytonaDeploymentConfig` 默认值：`api_key=""`、`target="us"`、`port=8000`、`container_timeout=900.0`、`runtime_timeout=60.0`、`image="python:3.11"`。

F-033: `src/swerex/deployment/remote.py` 第15-72行 `RemoteDeployment` 只包装 `RemoteRuntime`：`start()` 创建 `RemoteRuntime(auth_token, host, port, timeout)`，`stop()` 调用 `runtime.close()`。

F-034: `src/swerex/deployment/dummy.py` 第14-49行 `DummyDeployment` 在构造时创建 `DummyRuntime`；`start()`/`stop()` 为空操作；`runtime` 属性可读写。

F-035: `src/swerex/deployment/config.py` 第211-219行 `DeploymentConfig` 联合类型包含 7 个配置类：`LocalDeploymentConfig`、`DockerDeploymentConfig`、`ModalDeploymentConfig`、`FargateDeploymentConfig`、`RemoteDeploymentConfig`、`DummyDeploymentConfig`、`DaytonaDeploymentConfig`；第226-229行 `get_deployment(config)` 调用 `config.get_deployment()`。

F-036: 7 个部署配置类均设置 `model_config = ConfigDict(extra="forbid")`（`config.py` 第14、58、91、133、158、182、204 行）。

F-037: `src/swerex/deployment/hooks/abstract.py` 第1-3行 `DeploymentHook` 只定义 `on_custom_step(message: str)`；第6-17行 `CombinedDeploymentHook` 按加入顺序转发该回调。

F-038: `src/swerex/deployment/hooks/status.py` 第6-16行 `SetStatusDeploymentHook` 把 `on_custom_step` 消息转交给构造时传入的 `callable(id, message)`。

## 运行时抽象（Runtime）

F-039: `src/swerex/runtime/abstract.py` 第234行 `class AbstractRuntime(ABC)`；第244-287行定义 9 个抽象方法：`is_alive`、`create_session`、`run_in_session`、`close_session`、`execute`、`read_file`、`write_file`、`upload`、`close`。

F-040: `src/swerex/runtime/abstract.py` 第8-20行 `IsAliveResponse` 含 `is_alive: bool`、`message: str`，并实现 `__bool__` 返回 `is_alive`。

F-041: `src/swerex/runtime/abstract.py` 第23-36行 `CreateBashSessionRequest` 字段：`startup_source: list[str]`、`session: str = "default"`、`session_type: Literal["bash"]`、`startup_timeout: float = 1.0`。

F-042: `src/swerex/runtime/abstract.py` 第51-87行 `BashAction` 字段：`command`、`session`、`timeout`、`is_interactive_command`、`is_interactive_quit`、`check: Literal["silent","raise","ignore"]="raise"`、`error_msg`、`expect: list[str]`、`action_type="bash"`。

F-043: `src/swerex/runtime/abstract.py` 第90-106行 `BashInterruptAction` 字段：`session="default"`、`timeout=0.2`、`n_retry=3`、`expect`、`action_type="bash_interrupt"`。

F-044: `src/swerex/runtime/abstract.py` 第109-123行 `BashObservation` 字段：`output`、`exit_code`、`failure_reason`、`expect_string`、`session_type="bash"`。

F-045: `src/swerex/runtime/abstract.py` 第143-176行 `Command` 字段：`command: str | list[str]`、`timeout`、`shell=False`、`check=False`、`error_msg`、`env`、`cwd`、`merge_output_streams=False`；第179-183行 `CommandResponse` 含 `stdout`、`stderr`、`exit_code`。

F-046: `src/swerex/runtime/abstract.py` 第185-221行定义文件与上传模型：`ReadFileRequest(path, encoding, errors)`、`ReadFileResponse(content)`、`WriteFileRequest(content, path)`、`WriteFileResponse`、`UploadRequest(source_path, target_path)`、`UploadResponse`、`CloseResponse`。

F-047: `src/swerex/runtime/abstract.py` 第224-231行 `_ExceptionTransfer` 字段：`message`、`class_path`、`traceback`、`extra_info`。

F-048: `src/swerex/runtime/abstract.py` 第51、95、115、140、151、157、163、169、176 行使用 `Literal`/discriminator 或联合注释；模块内 `CreateSessionRequest`、`Action`、`Observation` 等均为 `Annotated[..., Field(discriminator=...)]` 联合类型（第36、107、124 行）。

F-049: `src/swerex/runtime/local.py` 第365-383行 `LocalRuntime` 持 `_sessions: dict[str, Session]`，`sessions` 属性返回该字典。

F-050: `src/swerex/runtime/local.py` 第390-401行 `create_session()` 在 session 名已存在时抛 `SessionExistsError`；仅识别 `CreateBashSessionRequest`，其他类型抛 `ValueError`。

F-051: `src/swerex/runtime/local.py` 第403-408行 `run_in_session()` 在 session 不存在时抛 `SessionDoesNotExistError`，否则委托给对应 `Session.run()`。

F-052: `src/swerex/runtime/local.py` 第129-176行 `BashSession.start()` 用 `pexpect.spawn("/usr/bin/env bash", encoding="utf-8", echo=False)` 启动 shell，环境变量设 `PS1=SHELLPS1PREFIX`、`PS2=""`、`PS0=""`；先 `sleep 0.3`，按需 `source` 启动文件，再重置 PS1/PS2/PS0，最后 `expect(self._ps1)`。

F-053: `src/swerex/runtime/local.py` 第274-351行 `_run_normal()` 三步：`_check_bash_command()` 语法检查、`_split_bash_command()` 拆分并用 ` ; ` 连接、发送命令并 `expect(expect_strings + [PS1])`、再发送 `echo EXITCODESTART$?EXITCODEEND` 提取退出码。

F-054: `src/swerex/runtime/local.py` 第301-311行 bashlex 抛任何异常时，在命令尾部追加 `TMPEXITCODE=$? ; sleep 0.1; echo -n 'UNIQUESTRING29234' ; (exit $TMPEXITCODE)`，改用唯一字符串作为终止标记。

F-055: `src/swerex/runtime/local.py` 第245-272行 `_run_interactive()` 发送命令并 `expect(action.expect + [PS1])`；`is_interactive_quit` 为真时先 `stty -echo`、等待唯一字符串与 PS1；否则从输出中剥离回显的命令。

F-056: `src/swerex/runtime/local.py` 第186-216行 `interrupt()` 最多 `n_retry` 次发送 `SIGINT` 并等待 expect 字符串；全部失败后发送 Ctrl-Z、`kill -9 %1`。

F-057: `src/swerex/runtime/local.py` 第59-94行 `_split_bash_command()` 用 `bashlex.parse()` 解析，按 AST 的 `pos` 范围截取原始子串；空输入或全注释输入返回空列表。

F-058: `src/swerex/runtime/local.py` 第101-116行 `_check_bash_command()` 用 `/usr/bin/env bash -n << 'SOUNIQUEEOF'` 执行语法检查，失败时抛 `BashIncorrectSyntaxError`，`extra_info` 含 `bash_stdout` 与 `bash_stderr`。

F-059: `src/swerex/runtime/local.py` 第96-98行 `_strip_control_chars()` 用正则删除 ANSI 转义序列并把 `\r\n` 替换为 `\n`。

F-060: `src/swerex/runtime/local.py` 第419-453行 `LocalRuntime.execute()` 调用 `subprocess.run(...)`：`stdin=DEVNULL`，`stderr=STDOUT` 当 `merge_output_streams=True`，超时抛 `CommandTimeoutError`，`check=True` 且非零退出码抛 `NonZeroExitCodeError`。

F-061: `src/swerex/runtime/local.py` 第455-472行 `read_file()` 用 `Path.read_text(encoding, errors)`；`write_file()` 先创建父目录再 `write_text`；`upload()` 目录用 `shutil.copytree`、文件用 `shutil.copy`。

F-062: `src/swerex/runtime/remote.py` 第44-62行 `RemoteRuntime` 构造时若 `host` 不以 `http` 开头则加 `http://` 前缀并记录 warning。

F-063: `src/swerex/runtime/remote.py` 第66-81行 `_get_timeout()` 在未指定时返回配置 `timeout`；`_api_url` 在 `port` 为 `None` 时只返回 host，否则拼接 `host:port`；`_headers` 在 `auth_token` 非空时返回 `{"X-API-Key": token}`。

F-064: `src/swerex/runtime/remote.py` 第165-197行 `_request()` 为每次请求生成 `uuid4` 并放入 `X-Request-ID`；失败重试 `num_retries` 次，延迟从 0.1s 指数退避并加 `uniform(0,0.5)` 抖动，上限 5s。

F-065: `src/swerex/runtime/remote.py` 第84-115行 `_handle_transfer_exception()` 从 `class_path` 拆分模块与类名，必要时 `__import__`，反射构造异常实例并设置 `extra_info`；构造失败时回退为 `SwerexException`。

F-066: `src/swerex/runtime/remote.py` 第117-126行 `_handle_response_errors()` 对 HTTP 511 解析 `swerexception` 并重抛；对 `>=400` 记录 critical 日志并 `raise_for_status()`。

F-067: `src/swerex/runtime/remote.py` 第128-160行 `is_alive()` 连接失败或非 200 时返回 `IsAliveResponse(is_alive=False, message=...)`，不抛异常；511 例外会重抛。

F-068: `src/swerex/runtime/remote.py` 第223-261行 `upload()` 对目录用 `shutil.make_archive` 打 zip，multipart 字段 `file`/`target_path`/`unzip=true`；对文件直接上传并设 `unzip=false`。

F-069: `src/swerex/runtime/dummy.py` 第33-55行 `DummyRuntime` 的 `run_in_session_outputs` 可为单个 `BashObservation` 或列表；列表模式每次 `pop(0)`，空列表抛 `DummyOutputsExhaustedError`。

F-070: `src/swerex/runtime/dummy.py` 第57-93行 `DummyRuntime` 的 `is_alive` 恒真，`execute` 返回空 stdout/stderr 与退出码 0，文件读写与上传为空操作。

F-071: `src/swerex/runtime/config.py` 第8-58行定义 3 个运行时配置：`LocalRuntimeConfig`、`RemoteRuntimeConfig`（`auth_token` 必填、`host="http://127.0.0.1"`、`timeout=0.15`）、`DummyRuntimeConfig`；第58行 `RuntimeConfig` 为三者联合；第60-61行 `get_runtime()` 分发。

## HTTP 服务端与协议

F-072: `src/swerex/server.py` 第10行创建 `FastAPI()`；第11行创建全局 `LocalRuntime()`；第34行 `AUTH_TOKEN = ""`；第35行 `APIKeyHeader(name="X-API-Key")`。

F-073: `src/swerex/server.py` 第67-75行认证中间件：`AUTH_TOKEN` 非空时读取 `X-API-Key`，不匹配返回 HTTP 401 "Invalid API Key"。

F-074: `src/swerex/server.py` 第77-103行请求 ID 中间件：读取 `X-Request-ID`，命中 `ResponseManager` 缓存则直接返回旧响应；否则执行请求、读取完整响应体、重建 `Response` 并按 request id 缓存。

F-075: `src/swerex/server.py` 第42-61行 `ResponseManager` 只保存 `last_processed_request_id` 与 `last_processed_response` 各一个；类 docstring 写明多并发客户端时幂等性不保证。

F-076: `src/swerex/server.py` 第105-119行全局异常处理器：把非 HTTP 异常序列化为 `_ExceptionTransfer`，以 HTTP 511 返回 `{"swerexception": {...}}`。

F-077: `src/swerex/server.py` 第122-190行注册 10 个路由：`GET /`、`GET /is_alive`、`POST /create_session`、`POST /run_in_session`、`POST /close_session`、`POST /execute`、`POST /read_file`、`POST /write_file`、`POST /upload`、`POST /close`。

F-078: `src/swerex/server.py` 第162-185行 `/upload` 接收 multipart `file`、表单 `target_path`、`unzip`；先写入临时目录，`unzip=true` 时用 `zipfile.ZipFile.extractall(target_path)`，否则 `shutil.move`。

F-079: `src/swerex/server.py` 第193-217行 `main()`：`-v/--version` 单独使用时打印 `__version__`；`--host` 默认 `0.0.0.0`、`--port` 默认 `8000`、`--auth-token` 设 `required=True` 且默认空字符串；设置全局 `AUTH_TOKEN` 后 `uvicorn.run(app, host, port)`。

F-080: `src/swerex/server.py` 第38-39行 `serialize_model()` 优先调用 `model_dump()`，否则调用 `dict()`。

F-081: `tests/conftest.py` 第24-52行 `remote_server` fixture 通过 `find_free_port()` 选端口，在后台线程运行 `uvicorn.run(swerex.server.app)`，设置 `swerex.server.AUTH_TOKEN = "testkey"`。

F-082: `tests/conftest.py` 第55-73行 `remote_runtime` 与 `runtime_with_default_session` fixture 分别构造 `RemoteRuntime(port, auth_token="testkey")` 与默认 bash session，并在结束时关闭。

F-083: `tests/test_server.py` 第20-41行对 10 个路由发起无 API key 的 GET 请求，断言状态码 403。

## 异常与失败处理

F-084: `src/swerex/exceptions.py` 第4-52行共 12 个异常类：`SwerexException`、`SessionNotInitializedError`、`NonZeroExitCodeError`、`BashIncorrectSyntaxError`、`CommandTimeoutError`、`NoExitCodeError`、`SessionExistsError`、`SessionDoesNotExistError`、`DeploymentNotStartedError`、`DeploymentStartupError`、`DockerPullError`、`DummyOutputsExhaustedError`。

F-085: `src/swerex/exceptions.py` 第16-26行 `BashIncorrectSyntaxError.__init__` 接收 `extra_info` 并保存到实例属性。

F-086: `src/swerex/exceptions.py` 第28行 `CommandTimeoutError` 同时继承 `SwerexException`、`RuntimeError`、`TimeoutError`；第37行 `SessionDoesNotExistError` 同时继承 `SwerexException`、`ValueError`。

F-087: `src/swerex/deployment/docker.py` 第133-147行 `_pull_image()` 在 `pull="never"` 时跳过；`pull="missing"` 且 `docker inspect` 成功时跳过；失败抛 `DockerPullError`。

F-088: `src/swerex/deployment/docker.py` 第106-115行 `_wait_until_alive()` 超时后读取容器 stdout/stderr 记录日志、调用 `stop()` 并重抛 `TimeoutError`。

F-089: `src/swerex/utils/wait.py` 第6-36行 `_wait_until_alive()` 在 `timeout` 内循环调用 `function(timeout=function_timeout)`，每次间隔 `sleep=0.25`；超时抛 `TimeoutError`，消息包含尝试次数与最后一次响应。

F-090: `src/swerex/utils/free_port.py` 第11-27行 `find_free_port()` 最多尝试 10 次，绑定 `("", 0)` 取端口，并用 `_REGISTERED_PORTS` 集合与锁去重。

F-091: `src/swerex/utils/log.py` 第22行从环境变量 `SWE_REX_LOG_STREAM_LEVEL` 读取日志级别；第58行从 `SWE_AGENT_LOG_TIME` 决定是否显示时间；第45行 `get_logger(name, emoji="🦖")` 默认 emoji 为恐龙。

F-092: `src/swerex/utils/aws.py` 第8-262行包含 10 个函数：`get_name_hash`、`get_container_name`、`get_execution_role_arn`、`get_task_definition`、`get_cluster_arn`、`get_default_vpc_and_subnet`、`get_security_group`、`run_fargate_task`、`get_public_ip`、`get_cloudwatch_log_url`。

F-093: `src/swerex/utils/aws_teardown.py` 第26-215行提供 `get_confirmation`、`has_target_tag`、`delete_iam_roles`、`delete_task_definitions`、`delete_ecs_clusters`、`delete_security_groups`、`main` 等清理入口；第40-54行按 `swe-rex` 目标标签筛选资源。

## 官方文档与导航

F-094: `README.md` 第12行称 SWE-ReX 是 "a runtime interface for interacting with sandboxed shell environments"；第15行称可并行运行 100 个 agent；第19-21行列三项能力：识别命令结束并提取输出/退出码、支持 `ipython`/`gdb` 等交互式工具、并行多个 shell session。

F-095: `README.md` 第25-30行称项目来自 SWE-agent 与 SWE-agent enigma 的经验，支持大规模并行、非 Linux/无 Docker 平台，并把 agent 逻辑与基础设施解耦；第32行称展示 SWE-agent 在 30 个 SWE-bench 实例上并行运行。

F-096: `README.md` 第41-49行安装方式：`pip install swe-rex`，以及 `[modal]`、`[fargate]`、`[daytona]`、`[dev]` 可选组。

F-097: `docs/architecture.md` 第3-6行描述五步流程：选择 Deployment → `start()` 启动容器/实例 → 得到 `RemoteRuntime` → 容器内 FastAPI Server 把请求转给 `LocalRuntime` → `Runtime` 提供文件读写、`execute`、`run_in_session`。

F-098: `docs/architecture.md` 第18-20行写明 `LocalRuntime` 与 `RemoteRuntime` 接口完全相同、可互换，并透明传输 `LocalRuntime` 中发生的异常。

F-099: `docs/usage.md` 第16-39行第一个示例用 `LocalDeployment`：`start()`、`execute(Command(["echo","Hello, world!"]))`、`create_session(CreateBashSessionRequest())`、`run_in_session(BashAction(command="export MYVAR='test'"))`、`run_in_session(BashAction(command="echo $MYVAR"))`、`stop()`。

F-100: `docs/usage.md` 第33行注释写明一次性命令与 session 命令的差别是 "environment state persists"。

F-101: `docs/usage.md` 第51-57行第二个示例只把 `LocalDeployment()` 换成 `DockerDeployment(image="python:3.12")`，复用同一个 `run_some_stuff` 函数。

F-102: `docs/usage.md` 第67行示例日志显示容器命令包含 `docker run --rm -p 59647:8000 --name python3.12-<uuid> python:3.12 /bin/sh -c 'swerex-remote --auth-token <uuid> || (... pipx run ...)'`。

F-103: `docs/usage.md` 第79-80行说明 `swerex-remote` 由 pipx 安装在容器内虚拟环境，`DockerDeployment` 用 `RemoteRuntime` 连接该服务器。

F-104: `docs/usage.md` 第84-100行 Modal 示例使用 `ModalDeployment(image="python:3.12", startup_timeout=60, deployment_timeout=3600)`。

F-105: `docs/installation.md` 第3-15行列出稳定版安装：`swe-rex`、`[modal]`、`[fargate]`、`[dev]`；开发版为 `git clone` 后 `pip install -e '.[dev]'`；贡献者还需 `pre-commit install`。

F-106: `mkdocs.yml` 第66-71行 Deployment 导航列出 Local、Remote、Docker、Modal、Fargate、Dummy 六项，未列 Daytona；`docs/api/deployments/` 目录无 `daytona.md`。

F-107: `docs/SECURITY.md` 第3-7行只给出四位维护者的联系邮箱，用于报告漏洞。

F-108: `docs/examples.py` 第10-22行是本地 runtime 的手工脚本：创建默认 session，依次运行不存在命令、`ls`、进入 `python` 交互、执行 `print('hello world')`、`quit()`、`echo`、关闭 session。

## 测试与验证事实

F-109: `tests/test_execution.py` 第1-50行覆盖：server alive、文件读写、`execute` 输出/空串/前导空格/`echo -n`、session 内多行输出、超时、创建/关闭 session、退出码 `127`/`1`、`check` 三态、交互式命令、`bashlex` 异常回退、上传文件/目录、1MB 文件读取、多 session 隔离、`merge_output_streams`、断行/heredoc/循环/子 shell、中断 session 与 pager。

F-110: `tests/test_runtime.py` 第1-12行覆盖 `_split_bash_command` 的普通多命令、转义换行、heredoc、空行、引号内换行、多 heredoc，以及 `_check_bash_command` 的合法/非法输入。

F-111: `tests/test_get_deployment.py` 第1-6行验证 6 个配置到部署类的映射：Local、Docker、Modal、Remote、Fargate、Daytona；未包含 Dummy。

F-112: `tests/test_local_runtime.py` 第1-9行验证本地 runtime 的 `_split_bash_command` 与 `_check_bash_command`。

F-113: `tests/test_docker_deployment.py` 共 9 个用例、`test_fargate_deployment.py` 2 个、`test_modal_deployment.py` 2 个、`test_remote_deployment.py` 1 个，分别覆盖对应部署的启动/停止/执行路径（按文件内 `def test_` 统计）。

F-114: `tests/test_execution.py` 第155行 `test_run_in_shell_multiple_interactive_and_normal_commands` 标记 `@pytest.mark.xfail`。

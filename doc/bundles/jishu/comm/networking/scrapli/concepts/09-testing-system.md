---
type: Concept
title: 测试体系与 golden 文件法
description: scrapli2 双层测试体系——functional 容器测试床、unit 离线回放、golden 文件命名模式与 --update 重写机制、dummy_ssh_server
tags: [scrapli, testing, golden-files, pytest, ci, dummy-ssh-server]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

scrapli2 的测试体系分为两层：`tests/functional/` 面向 containerlab 启动的真实容器测试床，`tests/unit/` 通过 TEST Transport 从文件回放会话数据实现离线测试。两层共用同一套 **golden 文件测试法**——把清洗后的实际输出与仓库中的期望文件逐字比对。

## 测试目录总览

```text
tests/
├── conftest.py          # 注册 --record / --update / --skip-slow 选项，输出清洗函数
├── functional/          # 真实设备（容器测试床）测试
│   ├── conftest.py      # cli / netconf / *_assert_result fixture
│   ├── test_cli.py
│   ├── test_netconf.py
│   ├── test_transport_bin.py
│   ├── test_transport_ssh2.py
│   ├── test_examples.py
│   ├── fixtures/        # SSH 测试密钥与 ssh_config（bin transport proxy jump 用）
│   └── golden/          # 期望输出（cli/ 与 netconf/ 分目录）
└── unit/                # 离线回放测试
    ├── conftest.py      # 基于 TEST Transport 的 fixture
    ├── dummy_ssh_server/  # Go 编写的假 SSH 服务器（main.go / go.mod / go.sum）
    ├── fixtures/        # TEST Transport 回放的会话数据（cli/ 与 netconf/ 分目录）
    └── golden/          # 期望输出（cli/ 与 netconf/ 分目录）
```

根级 `tests/conftest.py` 通过 `pytest_addoption` 注册三个自定义选项：

- `--record`：从真实设备录制单元测试数据（写入 fixtures 文件）
- `--update`：重写 golden 期望文件
- `--skip-slow`：跳过慢速测试（如超长输出用例）

同一文件还定义了输出清洗函数 `clean_cli_output` 与 `clean_netconf_output`——比对前先把 `user@host`、时间戳、密码行、NETCONF 的 session-id / counter / statistics 等易变内容替换为占位符（如 `__PASSWORD__`、`__TIMESTAMP__`），使 golden 文件在时间与凭据变化下保持稳定。

## 功能测试：fixture 按参数注入 Transport

`tests/functional/conftest.py` 的 `cli` fixture 接收 `platform` 与 `transport` 两个参数化参数：

```python
if transport == "bin":
    transport_options = TransportBinOptions()
else:
    transport_options = TransportSsh2Options()

return Cli(
    definition_file_or_name=definition_file_or_name,
    host=host,
    port=port,
    auth_options=auth_options,
    session_options=SessionOptions(operation_timeout_s=300),
    transport_options=transport_options,
)
```

- `platform == "arista_eos"` 时连接 cEOS 容器（172.20.20.17，darwin 走 localhost:22022），凭据 admin/admin，`LookupKeyValue(key="enable", value="libscrapli")` 提供升降级密码；`docker ps` 中没有 ceos 容器时直接 `pytest.skip`
- 其余（nokia_srl）连接 SR Linux 容器（172.20.20.16，darwin 走 localhost:21022），凭据 admin/NokiaSrl1!

`netconf` fixture 同样按 platform/transport 构造 `Netconf`：arista_eos 与 nokia_srl 之外的平台连接 netopeer NETCONF 服务器（172.20.20.18，root/password，`NetconfOptions(close_force=True)`）。

测试床本身由仓库根目录的 `make run-clab-ci` 启动（containerlab 拓扑包含 srlinux、netopeer 与 dummy linux container），CI 中的 functional 测试以 `--skip-slow` 跳过超长输出用例（`SLOW_TESTS` 中的 `nokia-srl-*-enormous-output` 系列同时被列入 `CLI_NO_GOLDEN`——这些用例只做结构性断言，不比对 golden）。

## golden 文件测试法

golden 比对 fixture（`cli_assert_result` / `netconf_assert_result`）根据测试函数名生成 golden 路径：

```python
filename = originalname.removeprefix("test_").replace("_", "-")
f = f"{golden_dir}/{filename}"
if id_ := ...:  # 参数化用例再拼接 pytest id
    f = f"{f}-{id_}"
```

`--update` 时把清洗后的实际输出直接写入该文件并返回；否则读取 golden 并断言相等：

```python
if request.config.getoption("--update"):
    with open(file=f, mode="w") as _f:
        _f.write(clean_cli_output(actual.result))
    return

with open(file=f, mode="r", newline="") as _f:
    golden = _f.read()

assert clean_cli_output(actual.result) == golden
```

这形成"录制-回放-锁定"闭环：真实设备输出被清洗归一化后固化为 golden 文件，任何回归都会在逐字比对中暴露。

### 目录命名模式

CLI golden 目录命名为 `<操作>[-async]-<平台>-<transport>[-变体]`，NETCONF 为 `<rpc 操作>[-async]-<服务器>-<transport>[-变体]`。三个真实例子：

| golden 目录名 | 分解 |
|---|---|
| `send-input-arista-eos-bin-same-mode-pagination-retain-input-and-trailing-prompt` | 操作 send-input · 平台 arista-eos · transport bin · 变体 same-mode-pagination-retain-input-and-trailing-prompt |
| `enter-mode-arista-eos-bin-escalate-with-password` | 操作 enter-mode · 平台 arista-eos · transport bin · 变体 escalate-with-password |
| `raw-rpc-create-subscription-async-netopeer-ssh2-simple` | 操作 raw-rpc-create-subscription · async · 服务器 netopeer · transport ssh2 · 变体 simple |

命名完全由"测试函数名 + 参数化 id"机械拼接而来，无需手工维护。注意 id 中的平台写法不完全一致（arista-eos 用连字符、nokia_srl 用下划线），golden 目录名如实保留了这种差异（如 `enter-mode-nokia_srl-bin-escalate`）。NETCONF golden 中 `kill-session` 系列对应 nokia-srl 服务器，其余主要对应 netopeer。

NETCONF 比对还支持相似度阈值：`test_get`/`test_get_async` 的 netopeer 用例输出中动态内容过多，改用 `SequenceMatcher` 比率 ≥ 0.8（`NETCONF_NON_EXACT_GOLDEN_MATCH_THRESHOLD`）的模糊匹配。

## 单元测试：fixtures/golden 一一对应与 TEST Transport

`tests/unit/` 的核心是 **fixtures 与 golden 目录的对应机制**：同名目录（如 `send-input-simple-requires-pagination`）同时存在于 `tests/unit/fixtures/cli/` 与 `tests/unit/golden/cli/`——前者存放 TEST Transport 回放的会话数据，后者存放期望输出。fixtures/cli 覆盖的操作包括 send-input（simple/retain-\*/input-handling-\*/requires-pagination/acquire-non-default-mode 等变体）、send-inputs、send-inputs-from-file、send-prompted-input、enter-mode（escalate/deescalate/multi-stage-change/no-change 及 async 变体）、get-prompt、read（simple/user-sized）、read-with-callbacks。对应关系并非绝对一一对应：fixtures/netconf（46 个目录）比 golden/netconf（42 个）多出 `get-next-notification`、`get-next-subscription`、`session-id` 等目录——这些用例只做断言、不比对 golden；fixtures/cli 的 `read-user-sized`、`_inputs_from_file_multi/single` 同样无 golden 对应。

回放机制由 `TransportKind.TEST` 实现。`TransportKind` 枚举中 `TEST = "test_"`，编码到 FFI 层为 `c_uint8(3)`；`Options.transport_kind` 属性在选项对象既非 Bin/Ssh2 也非 Telnet 时判定为 TEST。对应的 `TransportTestOptions` 只有一个关键字段 `f`——**TEST Transport 从该文件读取会话数据**，使整个 Zig 协议栈在无网络条件下跑完整流程：

```python
transport_options = TransportTestOptions(f=f)  # f 指向 tests/unit/fixtures/... 下的会话数据文件
```

unit conftest 的 `cli` fixture 同样按测试名推导 fixtures 路径，并以 `--record` 切换两种模式：

```python
if request.config.getoption("--record"):
    port = SSH_PORT_RECORD  # 22022，连接真实设备
    session_options = SessionOptions(recorder_path=f)  # 录制会话到 f
    transport_options = TransportBinOptions()
else:
    port = SSH_PORT  # 22，TEST Transport 不实际建连
    session_options = SessionOptions(read_size=1)
    transport_options = TransportTestOptions(f=f)
```

录制模式连接真实 arista_eos 设备（definition_file_or_name="arista_eos"，admin/admin，enable lookup 为 libscrapli），用 bin transport 把会话流写入 fixture 文件；日常模式则用 TEST Transport 逐字节回放。netconf 侧另有 `netconf`（netopeer、root/password）与 `netconf_srl`（srl、admin/NokiaSrl1!）两个 fixture，回放时设置 `read_size=1`、`operation_max_search_depth=32`，并因 CI runner 较慢而放宽 `operation_timeout_s=30`。

## dummy_ssh_server

`tests/unit/dummy_ssh_server/main.go` 是一个 Go 编写的极简 SSH 服务器，为并发等无 golden 场景提供真实 TCP/SSH 端点：

- 监听 `0.0.0.0:2222`，每次启动时用 `crypto/ed25519` 现场生成 host key
- `PasswordCallback` 只接受 `admin/password` 凭据，其余一律拒绝
- 只接受 `session` channel（其他 channel 类型直接拒绝），连接建立后写入 `router> ` 提示符
- 输入处理：收到含 `show version` 的行时返回模拟的 C3560CX 版本输出（随机延迟 0-500ms，换行转为 `\r\n`）；收到 `exit` 时断开连接；其他输入回显并重新显示提示符

conftest 中的 `dummy_ssh_server` fixture（module 作用域）以 `go run .` 启动该程序——无 go 工具链时 `pytest.skip`；启动后循环探测 2222 端口最长 120 秒（给拉取依赖留时间），探测失败或进程提前退出则抛错。teardown 通过 `os.killpg` + SIGKILL 杀掉整个进程组（`go run` 会再派生子进程，只杀父进程会泄漏）。`concurrency_cli` fixture 基于它构造指向 localhost:2222 的 `Cli` 工厂，bin transport 以 `extra_open_args=["-F", "/dev/null"]` 隔离用户 ssh config，且每次调用都新建 transport options——options 对象 apply 后持有每连接的 C 字符串状态，不能跨并发连接共享。

## 参数化矩阵：ENTER_MODE

`tests/functional/test_cli.py` 用三段式常量声明 `enter_mode` 的参数矩阵：

```python
ENTER_MODE_ARGNAMES = (
    "requested_mode",
    "post_open_requested_mode",
    "platform",
    "transport",
)
```

`ENTER_MODE_ARGVALUES` 覆盖 arista_eos × bin/ssh2/telnet 的升降级组合（no-change、escalate-with-password、multi-escalate-with-password、deescalate）与 nokia_srl × bin/ssh2 的 no-change/escalate 组合；`ENTER_MODE_IDS` 为每组取值给出可读 id（如 `arista-eos-bin-escalate-with-password`、`nokia_srl-bin-escalate`），这些 id 正是 golden 目录名的后缀来源。测试体先按 `post_open_requested_mode` 预置起始模式，再调用 `c.enter_mode(requested_mode=...)` 并做 golden 比对；同步与 `test_enter_mode_async` 复用同一矩阵。`test_get_prompt` 的 `GET_PROMPT_*` 常量采用同样的 argnames/argvalues/ids 三段式组织。

## CI 工作流

`.github/workflows/` 含 7 个工作流文件（cicd、test、lint、docs、publish、release、validate）。入口 `cicd.yaml` 在 push（main 分支）、pull_request、workflow_dispatch 时触发，本身不定义步骤，只复用两个可复用工作流：

```yaml
jobs:
  lint:
    uses: ./.github/workflows/lint.yaml

  test:
    uses: ./.github/workflows/test.yaml
```

被复用的 `test.yaml` 以 `workflow_call` 触发，含两个 job：

- **unit**：`version`（3.10~3.14）× `os`（ubuntu-latest、macos-latest、ubuntu-24.04-arm）矩阵（max-parallel 15），setup-go 1.26 并在 dummy_ssh_server 目录 `go mod tidy`，安装 dev 依赖后执行 `make test`
- **functional**：仅在 main 分支或指向 main 的 PR 上运行，先 `make run-clab-ci` 启动 containerlab 测试床并等待节点就绪，再以 `make test-functional-ci ARGS="--skip-slow"` 执行

## 相关概念

- [传输层](/concepts/02-transport-layer.md) — TransportKind.TEST 的位置与四种 transport 的选型
- [CLI 驱动](/concepts/04-cli-driver.md) — 被测的 send_input/enter_mode 等核心 API
- [仓库示例](/concepts/12-repository-examples.md) — functional 测试床与 examples 共用的 containerlab 拓扑

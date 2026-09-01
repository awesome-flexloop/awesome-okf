---
type: Example
title: 代理跳转连接
description: bin transport 走 ssh_config 的 ProxyJump，ssh2 用 proxy_jump_* 参数经堡垒机跳连目标设备
tags: [scrapli, example, proxy-jump, bastion, ssh, transport]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

## 场景说明

proxy jump（代理跳转）指先连接一台 bastion host（堡垒机），再经由这条中间连接到达最终目标主机。bin 与 ssh2（libssh2）两种 transport 都支持该行为，但两者的实现完全独立、互不共享，从功能对等角度不会、也不会计划做到 1:1（F-023、F-042）。

官方提供两个示例：`examples/cli/proxy_jump_cli/`（CLI 版）与 `examples/netconf/proxy_jump_netconf/`（Netconf 版——证明 NETCONF 连接同样支持 ProxyJump，F-037）。

## 运行前提

示例面向 "scrapli_clab" containerlab 测试拓扑的 "ci" 变体——该拓扑专门包含一个用于测试 proxy-jump ssh 行为的 dummy linux container（F-004）。在仓库根目录运行 make 目标启动拓扑（需要 docker，F-002）：

```bash
make run-clab-ci
```

示例假定从仓库根目录运行（这样 ssh config 中密钥的相对路径才能解析），且需提前为测试密钥补上权限位（git 不跟踪权限）：

```bash
chmod 600 tests/functional/fixtures/libscrapli_test_ssh_key
chmod 600 tests/functional/fixtures/libscrapli_test_ssh_key_passphrase
chmod 600 tests/functional/fixtures/scrapli-jumper-key
```

## bin transport：SSH config 中的 ProxyJump

bin transport 就是字面上的 `/bin/ssh`：把 proxyjump 按最普通的方式写进一份 ssh config 文件，再通过 `TransportBinOptions(ssh_config_path=...)` 传给 scrapli 即可（F-024）。

官方示例自带的 `ssh_config_linux`（darwin 变体为 `ssh_config_darwin`，差异只在地址与端口）：

```text
Host *
  # 忽略指纹确认，避免 proxy jump 测试被交互提示挂住
  # 注意：bin transport 默认只对初始连接忽略该确认，跳转段仍需自行处理
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null

Host jumper
  HostName 172.20.20.19
  User scrapli-key
  IdentityFile tests/functional/fixtures/scrapli-jumper-key

Host srl
  HostName 172.20.20.16
  User admin
  ProxyJump jumper
```

对应 Python 代码（基于 examples/cli/proxy_jump_cli/main.py 改写）：

```python
import sys
from pathlib import Path

from scrapli import AuthOptions, Cli, TransportBinOptions

ssh_config_file_path_base = f"{Path(__file__).resolve().parent}/ssh_config"

if sys.platform == "darwin":
    ssh_config_path = ssh_config_file_path_base + "_darwin"
else:
    ssh_config_path = ssh_config_file_path_base + "_linux"

bin_cli = Cli(
    definition_file_or_name="nokia_srlinux",
    # 与其他示例不同：这里 host 用的是 ssh config 中的别名 "srl"，而非 IP
    host="srl",
    auth_options=AuthOptions(
        username="admin",
        password="NokiaSrl1!",
    ),
    transport_options=TransportBinOptions(
        ssh_config_path=ssh_config_path,
    ),
)

with bin_cli as c:
    result = c.send_input(input_="show version")

    print(result)
```

跳转的全部细节——堡垒机地址与密钥（`Host jumper`）、目标主机真实地址（`HostName 172.20.20.16`）、`ProxyJump jumper` 指令——都由 ssh config 描述，scrapli 侧唯一的动作是把该文件路径传给 `ssh_config_path`。

## ssh2 transport：proxy_jump_* 参数

libssh2 的思路相反：像普通连接一样把 `host`/`port`/`auth_options` 配到**堡垒机**上，再用 `TransportSsh2Options` 的 `proxy_jump_*` 参数描述"最终跳到哪台主机、如何认证"（F-024）：

```python
from scrapli import AuthOptions, Cli, TransportSsh2Options

ssh2_cli = Cli(
    definition_file_or_name="nokia_srlinux",
    # host/port 指向堡垒机（jumper）本身
    host="172.20.20.19",
    port=22,
    auth_options=AuthOptions(
        username="scrapli-pw",
        password="scrapli-123-pw",
    ),
    transport_options=TransportSsh2Options(
        # 跳转目标：clab 拓扑中的 srlinux 设备
        proxy_jump_host="172.20.20.16",
        proxy_jump_username="admin",
        proxy_jump_password="NokiaSrl1!",
        # 也可改用本地密钥认证最终主机，对应参数名为 proxy_jump_private_key_path
    ),
)

with ssh2_cli as c:
    result = c.send_input(input_="show version")

    print(result)
```

### proxy_jump_* 参数一览

`TransportSsh2Options` 的全部 proxy jump 参数（定义见 scrapli/transport.py）：

| 参数 | 说明 |
|------|------|
| `proxy_jump_host` | 要跳转到的最终目标主机 |
| `proxy_jump_port` | 最终目标主机端口（NETCONF 场景即 830） |
| `proxy_jump_username` | 认证最终目标主机的用户名 |
| `proxy_jump_password` | 认证最终目标主机的密码 |
| `proxy_jump_private_key_path` | 认证最终目标主机的私钥路径 |
| `proxy_jump_private_key_passphrase` | 私钥口令 |
| `proxy_jump_libssh2_trace` | 为 proxy jump 的"内层"会话开启 libssh2 trace |

## Netconf 连接同样支持

`examples/netconf/proxy_jump_netconf/main.py` 与 CLI 版几乎相同——`Cli` 换成 `Netconf`、`send_input` 换成 `get_config`，ssh2 版多了一个 `proxy_jump_port=830`（F-038）：

```python
from scrapli import AuthOptions, Netconf, TransportBinOptions, TransportSsh2Options

# bin transport：同样走 ssh config（路径选择逻辑与 CLI 版一致）
bin_nc = Netconf(
    host="srl",
    auth_options=AuthOptions(
        username="admin",
        password="NokiaSrl1!",
    ),
    transport_options=TransportBinOptions(
        ssh_config_path="ssh_config_linux",
    ),
)

with bin_nc as nc:
    result = nc.get_config()

    print(result.result[0:250])

# ssh2 transport：proxy_jump_* 参数
ssh2_nc = Netconf(
    host="172.20.20.19",
    port=22,
    auth_options=AuthOptions(
        username="scrapli-pw",
        password="scrapli-123-pw",
    ),
    transport_options=TransportSsh2Options(
        proxy_jump_host="172.20.20.16",
        proxy_jump_port=830,
        proxy_jump_username="admin",
        proxy_jump_password="NokiaSrl1!",
    ),
)

with ssh2_nc as nc:
    result = nc.get_config()

    print(result.result[0:250])
```

## 两种方式怎么选

- **bin transport**：跳转逻辑集中在一处 ssh config，可直接复用现有运维配置（IdentityFile、KnownHosts、ProxyJump 链），行为与命令行 `ssh` 完全一致
- **ssh2 transport**：不依赖外部 ssh 可执行文件与 config 文件，跳转参数程序化内联，适合不便落盘 ssh config 的环境

两者实现完全独立、特性面不对齐（F-023），在两种 transport 之间迁移时不要假设配置一比一对应。

## 相关概念

- [/concepts/02-transport-layer.md](/concepts/02-transport-layer.md) — bin/ssh2/telnet 三种 transport 的机制与适用场景
- [/concepts/12-repository-examples.md](/concepts/12-repository-examples.md) — 官方示例体系、clab 拓扑契约与学习路径
- [/examples/basic-connect.md](/examples/basic-connect.md) — 不经跳转的基础连接与命令发送

---
type: concept
title: 05 - 高级资源、异常体系与工程治理
description: Quadlets v5.8 / Pods / Secrets / Volumes / Networks / System 7直接方法；8类异常继承链；AGENTS.md 7大AI陷阱；测试双态 skipif/pnext；覆盖率双轨 80% vs 85%；DCO 签名与 git-validation；pylint 不默认
tags: [podman-py, quadlets, exceptions, AGENTS-pitfalls, testing-governance, DCO, coverage-dual-track, pods, secrets]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-quadlets
    resource: external/dao/action/Containers/podman-py/podman/domain/quadlets.py
    title: QuadletsManager 源码 — v5.8 新增 install/delete/list/get/get_contents/print_contents/report/show/create
  - id: src-exceptions
    resource: external/dao/action/Containers/podman-py/podman/errors/exceptions.py
    title: 异常体系源码 — APIError/NotFound/ImageNotFound/DockerException/PodmanError/BuildError/ContainerError/InvalidArgument/StreamParseError
  - id: src-agents-pitfalls
    resource: external/dao/action/Containers/podman-py/AGENTS.md
    title: podman-py AGENTS.md L198-L207 Common pitfalls for AI agents + L190-L196 覆盖率双轨 + DCO make validate
  - id: src-ssh-adapter
    resource: external/dao/action/Containers/podman-py/podman/api/ssh.py
    title: SSHSocket connect() shell-out ssh -N -L 隧道源码
---

# 05 - 高级资源、异常体系与工程治理

## 5.1 QuadletsManager：v5.8 新增 systemd 单元管理

Quadlet 是 Podman 5 起的 systemd 原生集成机制（`.container`/`.volume`/`.network`/`.kube`/`.image` 文件→systemd unit）。

### 5.1.1 Quadlet 资源模型 6 属性 + 3 方法

| `@property` | 来源键名（兼容双写） | 含义 |
|---|---|---|
| `.name` | `Name` / `name` | quadlet 文件名（含扩展名） |
| `.unit_name` | `UnitName` / `unitName` | 对应 systemd unit 名（如 `myapp.service`） |
| `.path` | `Path` / `path` | 磁盘绝对路径 |
| `.status` | `Status` / `status` | running / stopped / failed / generated |
| `.application` | `App` / `app` | 所属应用分组标识 |

Quadlet 实例方法：
- `delete(force=False, ignore=False, reload_systemd=True)` → `list[str]` 删除的文件名
- `get_contents()` → `str` 完整文件内容
- `print_contents()` → `None` 打印到 stdout（strip 头尾空白换行）

### 5.1.2 QuadletsManager CRUD 速查

```
QuadletsManager(Manager)
 ├── exists(key) → bool              (HEAD /quadlets/{key}/exists 404→False)
 ├── list(filters={"name":"my*"}) → list[Quadlet]
 ├── get(name) → Quadlet             ( NotFound 如果空 )
 ├── get_contents(name) → str
 ├── print_contents(name) → None
 ├── report() / show() / create()    ( 系统级报告与预览 )
 └── delete(name=None, all=False, **) → list[str]
        ├── name 或 all=True 必须有一个
        ├── force=True：先 stop 再删 running quadlet
        ├── ignore=True：不存在不抛错（幂等删除）
        └── reload_systemd=True：删完 daemon-reload
 └── install(files, *, replace=False, reload_systemd=True) → dict
        ├── files: 单文件或 list，元素支持 3 种形态：
        │     (a) str/PathLike：磁盘路径直接上传
        │     (b) tuple[str, str|bytes]：(文件名, 内容) 内存构造
        │     (c) 单个 .tar/.tar.gz 路径：直接 POST x-tar
        ├── 每个请求必须恰好 1 个 quadlet 文件（.container 等扩展名识别）
        └── 返回 {"InstalledQuadlets":{}, "QuadletErrors":{}}
```

**install 多形态示例**（对应 [quadlets.py#L276-L288](../../../external/dao/action/Containers/podman-py/podman/domain/quadlets.py#L276-L288)）：

```python
# 形态 a：磁盘路径
client.quadlets.install("/etc/containers/systemd/myapp.container")

# 形态 b：内存构造 + 附带 Containerfile 资产
client.quadlets.install([
    ("myapp.container", "[Container]\nImage=alpine:3\nPublishPort=8080:80\n"),
    ("Containerfile", "FROM alpine:3\nRUN apk add nginx\n"),
], replace=True)

# 形态 c：tarball 打包好直接传
client.quadlets.install("./myapp-quadlets.tar.gz", replace=True)
```

> **G2 洞察四元组 #4：不要混淆 `delete(name=None, all=True)`**
> 必须提供 `name` **或** `all=True`，两个都不提供 → `PodmanError: Quadlet name, or 'all=True' should be provided`。
> 清理所有 demo quadlet 的幂等写法：
> ```python
> client.quadlets.delete(all=True, force=True, ignore=True, reload_systemd=True)
> ```

## 5.2 其他高级管理器（70% 对齐 docker-py）

除 containers/images/quadlets 外，SDK 还有 6 个管理器，**70% API 签名与 docker-py 对齐**，直接迁移无压力：

| 管理器 | 核心方法（与 docker-py 相同语义） | Podman 扩展 |
|---|---|---|
| **PodsManager** | `list / get / create(name,infra=..,publish=..,memory=..)`；`start / stop / kill / restart / pause / unpause / exec_run(cmd, **)`；`remove / prune` | `inspect` 字段多 infra_name / cgroup_parent |
| **SecretsManager** | `list / get / create(name,data,labels,driver) / remove` | `data` 接受 bytes 或 str（自动编码） |
| **VolumesManager** | `list / get / create(name,driver,opts,labels) / remove / prune` | `recreate` 参数 |
| **NetworksManager** | `list / get / create(name,driver,options,ipam,labels,internal) / remove / prune` | `dns_enabled` Podman-only 字段 |
| **ManifestsManager** | `list / get / create(name,all) / add(target,platform) / remove(target) / push(auth) / inspect` | 完全对齐 OCI spec，和 docker-py 签名一致 |
| **SystemManager** | 7 个直接方法：`df / info / version / ping / login / events / close`（PodmanClient 薄门面转发） | `df` 返回字典键名是 libpod 风格不是 docker 风格 |

> **Swarm 不支持提示**：`client.services / client.configs / client.nodes / client.secrets.external` 一律返回 `NotImplementedError`（R1-陷阱延伸）。不要 try/except 后假装成功，检测方法：
> ```python
> if hasattr(client, "services"):   # 永远 True，薄门面有 cached_property
>     try:
>         client.services.list()
>     except NotImplementedError:
>         print("Podman 不支持 Swarm services")
> ```

## 5.3 8 类异常继承链全景图

```
requests.exceptions.HTTPError
  └── APIError (L15)
        ├── status_code / explanation / is_client_error() / is_server_error()
        ├── NotFound (L72)          ← 404 资源不存在（通用）
        └── ImageNotFound (L79)     ← 404 镜像不存在（专门化，isinstance 更精准）

builtins.Exception
  └── DockerException (L83)          ← docker-py 兼容基类，迁移判断根节点
        └── PodmanError (L90)        ← podman-py 业务异常基类
              ├── BuildError (L94)        → .msg + .build_log (Iterable[str])
              ├── ContainerError (L109)   → .container + .exit_status + .command + .image + .stderr
              └── InvalidArgument (L144)  → 参数校验失败（load()传两个等）

builtins.RuntimeError
  └── StreamParseError (L148)  ← _stream_helper JSON 解析 / UTF-8 解码失败 .msg
```

### 5.3.1 推荐分层捕获模板

```python
from podman import PodmanClient
from podman.errors import (
    APIError, NotFound, ImageNotFound,
    BuildError, ContainerError, InvalidArgument,
    DockerException, PodmanError, StreamParseError,
)
import requests

with PodmanClient() as client:
    try:
        run_complex_pipeline(client)
    except ContainerError as e:
        print(f"[业务失败]{e.exit_status=} cmd={e.command} img={e.image}")
        if e.stderr: print(f"  stderr: {bytes(e.stderr).decode(errors='replace')}")
    except BuildError as e:
        print(f"[构建失败]{e.msg}")
        for l in list(e.build_log)[-20:]: print(f"  build: {l}")
    except ImageNotFound as e:
        print(f"[镜像缺失]{e}，需要 images.pull(...)")
    except NotFound as e:
        print(f"[资源不存在]{e.status_code=}: {e.explanation or e}")
    except InvalidArgument as e:
        print(f"[参数错]{e}（e.g. load()传了data又传file_path）")
    except StreamParseError as e:
        print(f"[流解析失败]{e.msg}（libpod 响应异常 / 网络中断）")
    except APIError as e:
        if e.is_client_error():   print(f"[客户端4xx]{e.status_code=} {e}")
        elif e.is_server_error(): print(f"[服务端5xx]{e.status_code=} {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"[连接失败] 检查 socket/PODMAN_HOST/SSH 隧道: {e}")
    except requests.exceptions.Timeout:
        print(f"[超时] 调大 timeout 参数或检查 daemon 健康")
    except DockerException:
        print(f"[通用 podman-py/docker 兼容层]")
```

## 5.4 AGENTS.md 7 大 AI 陷阱（原文数字 1-7 → 本文档 R1-R7 锚定便于引用）

[AGENTS.md L199-L207](../../../external/dao/action/Containers/podman-py/AGENTS.md#L199-L207) 明确定义了 AI 开发者最高频的 7 类错误（原文为 `1. ... 7.` 数字编号，本文档统一用 **R1-R7** 作为稳定锚点编号以便跨文档交叉引用）：

| 编号 | 陷阱原文 | 典型场景 | 正确实践 |
|---|---|---|---|
| **R1** | **Wrong repository** – Go 的 `containers/podman/pkg/bindings` 不是本项目；PyPI 名 `podman` = 本仓库 | 从 chatgpt 旧回答抄来 `github.com/containers/podman/v5/pkg/bindings/python` 不存在的包 | `pip install podman`，import `from podman import PodmanClient` |
| **R2** | **Only make OR only tox dogma** – Makefile 内部调用 tox；CONTRIBUTING 以 tox 为权威 | CI 只跑 `make lint` 跳过单元测试；或只 `tox` 不跑 `make validate` DCO | `make lint && tox -e coverage && make validate` 三件套 |
| **R3** | **80%(tox) vs 85%(CONTRIBUTING)** – tox.ini/Makefile 用 `--fail-under=80`，但 CONTRIBUTING 合并红线是 85% | PR 写了新代码覆盖率 82%，tox 过了但被 reviewer 打回 | **取严 85%**，core 模块（images/containers/api）自测覆盖目测≥85% |
| **R4** | **API drift** – 客户端路径/负载必须匹配 live **libpod API 文档** | SDK 版本旧，新 Podman daemon 返回新字段代码里没处理 | 升级前 `client.version()` 比对 daemon 版本，对 libpod API 文档 diff |
| **R5** | **SSH hanging** – `Waiting on podman-forward-*.sock` 通常是 `ssh localhost` 不通 | CI 环境没配免密 ssh key，StrictHostKeyChecking 拦截 | **先跑 `ssh <host> exit` 必须 0 秒通**；生产用 `known_hosts` 预配置不用 `StrictHostKeyChecking=no` |
| **R6** | **Rootful vs rootless** – 同一个测试在两种 daemon 模式下结果不同 | Rootless 跑端口 <1024 绑定失败；Rootful 跑 systemd --user Quadlet 找不到 | `skipif=(os.geteuid()==0)` / `skipif=(os.geteuid()!=0)` 显式标注 |
| **R7** | **Redundant ignore files** – `.gitignore` 规则不要复制到 IDE 专属 ignore | `.vscode/ignore` 复制了整个 `.gitignore` 几百行，新增 pattern 漏两边同步 | IDE ignore 只写 IDE 专属目录，**公共规则统一扩展 `.gitignore`** |

> **G2 洞察四元组 #1（延伸）：薄门面迁移三坑 + R1-R7 合计十坑是 podman-py 知识包 V2.0 的核心价值**。docker-py 用户迁移到 podman-py：前三个坑来自代码 API 差异；后七个来自工程治理。少踩一个坑等于少一个 PagerDuty 午夜告警。

## 5.5 测试治理双态：unit vs integration

podman-py 测试分两层（AGENTS.md Quick Start 明确区分）：

### 5.5.1 Unit：纯 mock HTTP 响应

```python
# podman/tests/unit/ 下 不需要真实 Podman daemon
import pytest
from unittest.mock import patch

def test_images_get_404_to_ImageNotFound():
    with patch("podman.api.client.APIClient.get") as m:
        m.return_value.status_code = 404
        # requests-mock 或 Mock 构造 Response 对象
        # 然后断言 client.images.get("nonexist") 抛 ImageNotFound
```

### 5.5.2 Integration：需要 `PODMAN_BINARY` + SSH 预断言

```python
# podman/tests/integration/base.py 会在 setUpClass 执行：
# 1. 断言 podman --version ≥ required_min
# 2. 断言 ssh localhost exit 0 (exit code 0, <0.5s)（R5 防挂）
# 3. Rootless：断言 XDG_RUNTIME_DIR 存在且 socket 可达
```

### 5.5.3 `@pytest.mark.skipif` 三元组 + `@pytest.mark.pnext`

```python
import os
import pytest

PODMAN_VERSION = os.environ.get("PODMAN_VERSION", "0.0.0")
OS_RELEASE = os.environ.get("OS_RELEASE", "unknown")
IS_ROOTFUL = os.geteuid() == 0

@pytest.mark.skipif(
    tuple(int(x) for x in PODMAN_VERSION.split(".")) < (5, 8),
    reason="quadlets API 仅 Podman ≥5.8",
)
def test_quadlets_install_from_memory_tuple(client):
    ...

@pytest.mark.skipif(
    "fedora" not in OS_RELEASE.lower() or int(OS_RELEASE.split(":")[-1]) < 42,
    reason="仅 Fedora 42+ 系统测试此 Cgroup v2 特性",
)
def test_systemd_managed_quadlet_autostart(client):
    ...

@pytest.mark.skipif(
    not IS_ROOTFUL,
    reason="Rootless 无法绑定 <1024 端口",
)
def test_publish_port_80_nginx(client):
    ...

# pnext = "planned next"：下一版本实现的前瞻用例，默认跳过
# 只有 pytest --pnext 才执行
@pytest.mark.pnext
def test_manifest_annotations_v5_9(client):
    ...
```

## 5.6 覆盖率双轨与 pylint 非默认（R3 延伸）

```
工程文档 (CONTRIBUTING.md)       自动化 (tox.ini / Makefile)
───────────────────────          ─────────────────────────
85% 合并红线 ← 严格            ← 宽松 → 80% --fail-under
       ↑                                ↑
   审稿人手工打回                 CI 自动通过
```

**处理策略（避免"我代码 tox 过了为啥被拒"）**：
- 自动化层：tox -e coverage 过 80%（确保 PR 最低质量）
- 人工审核前：对核心模块（client.py / domain/* / errors/*）运行 `coverage report -m` 单独看，目测核心分支 ≥ 85%
- diff 文件单独跑：`pytest --cov=podman.domain.images --cov-fail-under=85` 跑新增模块

**pylint 不在 pre-commit 里**（R2 延伸）：`.pre-commit-config.yaml` 只含 `ruff` + `mypy` + `tmt` + `yaml` 4 项。pylint 在两种时机跑：
1. Reviewer 明确要求 `pylint podman/domain/xxx.py`
2. 大重构之前做质量基准（`pylint --disable=C,R podman/` 只看错误/警告）

## 5.7 DCO 签名 + make validate + git-validation

```bash
# 每笔 commit 必须 DCO Signed-off-by
git commit -s -m "feat(images): add progress bar fallback for rich missing"

# make validate 会调用 git-validation 检查：
#   - DCO Signed-off-by 是否存在
#   - subject 长度 ≤ 90 chars
#   - 其他合规性
# ⚠️ git-validation 二进制必须在 PATH 中，否则 make validate 直接失败
#    安装：go install github.com/vbatts/git-validation@latest
#          或从 release 下载二进制放入 ~/.local/bin
make validate
```

> **陷阱：CI 环境 `make validate` 报 `command not found: git-validation`**
> 安装 git-validation 不是 Python 依赖，不能 `pip install`。CI Dockerfile 必须加一层安装。

## 5.8 本节 G3 可迁移模式总表（工程治理版）

| 模式名 | 触发场景 | 核心步骤 | 反模式 |
|---|---|---|---|
| **R3 双轨达标** | coverage tox 过了但被 reviewer 打回 85% 红线 | ① 跑 coverage report -m 核心模块 ② 目测分支≥85% ③ 补全 pnext 标记的未来用例 | 只信 tox.ini 里的 80 |
| **R5 SSH 预检** | integration test 挂 Waiting on podman-forward-*.sock | ① setUpClass 先 `subprocess.run(["ssh",host,"exit"],timeout=0.5)` 断言 rc=0 ② 生产 known_hosts 预配置③ 检查身份文件权限 ≤600 | StrictHostKeyChecking=no 偷懒到生产 |
| **R6 Rootful/Rootless 双跑** | 一个模式过一个模式挂 | ① skipif 三元组显式标注 ② 两个模式 CI matrix 都跑 ③ 文档标注受限场景 | 测了 rootless 就说全部 pass |
| **R7 单源 ignore** | `.vscode/ignore` / `.idea/ignore` 跟 `.gitignore` 不同步 | 公共规则只扩展 `.gitignore`，IDE ignore 只保留 IDE 专属目录 | copy-paste 几百行重复 |
| **异常分层 9 行模板** | 裸 `except Exception` 无法定位 | `ContainerError→BuildError→NotFound→ImageNotFound→InvalidArgument→APIError 4xx→5xx→ConnectionError→Timeout` 顺序捕获 | `except Exception as e: log(e)` 吞细节 |

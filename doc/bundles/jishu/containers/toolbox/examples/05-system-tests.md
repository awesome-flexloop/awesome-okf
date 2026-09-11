---
type: Example
title: "运行与扩展 BATS 系统测试"
description: "在本地/多发行版环境运行 Toolbx 的 22 个 BATS 测试文件：依赖准备、TOOLBX/TMPDIR 变量、内嵌认证 registry、用例编写约定与 CDI 夹具使用。"
tags: [toolbx, toolbox, bats, testing, system-tests, ci, ansible, registry, cdi, example]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T14:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T14:40:00+08:00 }
status: stable
stale_after: 2027-09-11
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
    title: 实现层源码地图
  - id: docs-man
    resource: /references/docs-man-source.md
    title: 官方手册、设计目标与版本演进信源
---

# 运行与扩展 BATS 系统测试

Toolbx 的系统测试在真实容器/镜像层面保证工具与 Podman 演进不回归（22 个 .bats 文件，见 [/concepts/10-build-and-tests.md](../concepts/10-build-and-tests.md)）。本篇给出本地运行、CI 复用与新增用例的操作指南。

## 环境准备

依赖清单（test/system/README.md 权威）：

- 运行时：`podman`、`skopeo`、`toolbox`；
- 测试工具：`bats`（要求 ≥1.10.0，用例 setup 中 `bats_require_minimum_version` 强制）、`awk`、GNU coreutils；
- registry 夹具：`httpd-tools`（htpasswd）、`openssl`；
- bats 库：子模块形式内嵌，先初始化：

```bash
cd <toolbox-source-root>
git submodule update --init test/system/libs/bats-support test/system/libs/bats-assert
```

rootless 用户还需有效 subuid/subgid 范围（否则 create 用例在 preRun 即失败）。

## 运行测试

```bash
# 推荐：镜像缓存放磁盘而非 tmpfs
export TMPDIR=/var/tmp

# 用系统安装的 toolbox/podman/skopeo
bats ./test/system/

# 用刚编译出的本地 toolbox 二进制
TOOLBX=./toolbox bats ./test/system/
```

注意 README 强调的顺序要求：输出中 `test suite: [job]` 类任务必须先成功（setup_suite.bash 负责整套环境：镜像 mock、registry 启动），其余 job 才可信。

只跑一个文件/一个用例：

```bash
bats ./test/system/101-create.bats
bats ./test/system/230-cdi.bats -f "Smoke test"
```

测试不影响宿主持有容器/镜像：setup/teardown 调 `cleanup_all` 清理测试资源，并把 $HOME 隔离（NEWS 0.2 记录"Isolated the host's HOME from the system tests"）。

## 内嵌认证 registry

夹具在 `localhost:50000` 起一个带认证的 OCI registry：

- 账号/密码：`user` / `user`（htpasswd 由 httpd-tools 生成，openssl 出证书）；
- 默认仅推送一个镜像 `fedora-toolbox:34`，镜像 mock 自动完成以避免网络波动；
- 手工复现拉取：

```bash
podman login --username user --password user "$DOCKER_REG_URI"
podman pull "$DOCKER_REG_URI/fedora-toolbox:34"
```

因此系统测试在无外网环境也能跑（create 的 --authfile 路径在 101/501 用例中被覆盖）。

## 用例编写约定

- 命名：`@test "<command>: <test description>"`，预期失败的用例描述以 **"Try to..."** 开头；非显而易见的输出放标题末尾括号；
- 每个用例 `setup()` 从干净环境开始、`teardown()` 清理，保证用例间无依赖；
- 头部 `load 'libs/bats-support/load'`、`load 'libs/bats-assert/load'`、`load 'libs/helpers'`；
- 断言用 bats-assert 的 `assert_success`/`assert_failure`/`assert_output`/`assert_line`；
- 与工具交互统一用 `$TOOLBX` 变量而非硬编码 `toolbox`。

最小新增用例模板：

```bats
# shellcheck shell=bats
load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/helpers'

setup() {
  bats_require_minimum_version 1.10.0
  cleanup_all
}

teardown() {
  cleanup_all
}

@test "create: try to use an invalid release" {
  run --keep-empty-lines --separate-stderr "$TOOLBX" create -d ubuntu -r 24.13
  assert_failure
  assert_output --partial "invalid argument for '--release'"
}
```

## 使用 CDI 夹具测试 GPU 分支

无 GPU 的 CI 机器通过预置 JSON 夹具也能覆盖 init-container 的 CDI 解析逻辑：

1. `create_default_container`；
2. 建 `$XDG_RUNTIME_DIR/toolbox`（0700），把 `data/cdi-*.json` 拷为 `cdi-nvidia.json`（0644）；
3. 执行 `"$TOOLBX" run true` 触发入口应用 spec；
4. 若真实硬件导致文件被新 spec 覆盖（`cmp` 不一致），自动 skip；
5. 否则断言符号链接/ldcache 配置符合夹具预期。

夹具分四组共 29 个：`cdi-empty.json`（1 个空 spec）、`cdi-hooks-{00,01,02,10,11,12,14,15}.json`（8 个通用钩子）、`cdi-hooks-create-symlinks-{00..08,30..37}.json`（17 个链接边界）、`cdi-mounts-{10,11,12}.json`（3 个挂载映射）。新增分支时同步在 data/ 添加夹具并在 230-cdi.bats 加用例。

## 用 Ansible playbooks 复现 CI 环境

playbooks/ 把 CI 的多发行版环境编排声明式化，可在本地 VM 复用：

| playbook | 用途 |
|---|---|
| `setup-env.yaml` | 基础环境 |
| `dependencies-common.yaml` | 跨发行版公共依赖 |
| `dependencies-fedora.yaml` / `-fedora-coreos.yaml` / `-fedora-restricted.yaml` / `dependencies-centos-9-stream.yaml` | 各目标系统依赖 |
| `unit-test.yaml` | Go 单测 |
| `system-test-commands-options.yaml` | 101-108 命令/选项组 |
| `system-test-runtime-environment-arch-fedora.yaml` / `-ubuntu.yaml` | 201-270 运行环境组（ipc/network/user/ulimit/dbus/cdi/kerberos/rpm） |
| `build.yaml` | 发行构建 |

## 相关概念与示例

- [/concepts/10-build-and-tests.md](../concepts/10-build-and-tests.md)
- [/concepts/09-nvidia-cdi.md](../concepts/09-nvidia-cdi.md)
- [/examples/03-multi-distro.md](03-multi-distro.md)

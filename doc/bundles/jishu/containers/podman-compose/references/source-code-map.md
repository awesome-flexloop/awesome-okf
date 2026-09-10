---
type: Reference
title: podman_compose.py 源码信源登记
description: podman-compose 单文件源码的版本固定信息、结构地图与核心符号索引，供源码级概念文档溯源
tags: [podman, compose, source-code, reference, architecture]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# podman_compose.py 源码信源登记

本文件登记 podman-compose 主体源码 `podman_compose.py` 的版本固定信息与结构地图。本束概念文档中涉及内部实现（类名、函数名、行号、执行流程）的陈述，均以本信源为依据。

## 版本固定

| 项目 | 值 |
|------|-----|
| 脚本内版本号 | `__version__ = "1.6.0"` |
| Git 描述 | `v1.6.0-97-ge3df104`（v1.6.0 标签之后 97 个提交） |
| 固定 commit | `e3df10472e194ab6d547b5ad25542c5c79e1a5fb` |
| 提交日期 | 2026-08-11 |
| 代码规模 | 约 5534 行，单文件 |
| 许可证 | GPL-2.0（SPDX 头声明） |
| 运行依赖 | Python ≥ 3.9、PyYAML、python-dotenv、系统 podman 可执行文件 |

> 版本固定纪律：文档验证基于上述 commit 的源码内容。引用的 API、函数签名与行号均对应该快照；后续版本若重构，需重新核验。

## 源码结构地图

`podman_compose.py` 虽为单文件，但内部按职责可分为 8 个逻辑层（行号为近似区间）：

| 行号区间 | 逻辑层 | 核心内容 |
|----------|--------|---------|
| 1–160 | 头部与工具函数 | imports、`__version__`、`is_list`、`try_int/try_float`、`str_to_seconds`、版本比较 `strverscmp_lt`、正则常量、`PODMAN_CMDS` 元组 |
| 162–580 | 配置预处理 | 短挂载解析 `parse_short_mount`、卷名补全 `fix_mount_dict`、变量插值引擎 `var_interpolate`、递归替换 `rec_subs`、`norm_as_list/norm_as_dict/norm_ulimit` |
| 582–1342 | 资源描述翻译 | 卷创建断言 `assert_volume`、挂载参数 `mount_desc_to_*`、密钥 `create_secrets_from_environment/get_secret_args`、资源限制 `container_to_*_res_args`、端口归一化 `norm_ports`、网络参数 `get_network_create_args/assert_cnt_nets/get_net_args*` |
| 1344–1622 | 服务翻译主函数 | `container_to_args`：service dict → `podman create/run` argv 的完整映射 |
| 1625–1810 | 依赖图与 YAML 标签 | `ServiceDependencyCondition`/`ServiceDependency`、`rec_deps/calc_dependents/flat_deps`、`OverrideTag`（`!override`）、`ResetTag`（`!reset`） |
| 1811–2076 | CLI 包装层 | `wait_with_timeout`、`ExistingContainer` dataclass、`Podman` 类（`output/run/exec/network_ls/volume_ls/existing_containers`） |
| 2078–2417 | 归一化与合并 | `normalize_service/normalize/normalize_final`、`rec_merge_one/rec_merge`、`load_yaml_or_die`、`resolve_extends`、`dotenv_to_dict`、`find_compose_files_recursively`、`COMPOSE_DEFAULT_LS` |
| 2419–3275 | 主编排类 | `PodmanCompose` 类：`run` 入口、`config_hash`、pod 解析、命名、`_parse_x_podman_settings`、`_parse_compose_file` 加载管线、`_resolve_profiles`、`_resolve_context_dependencies`、`_parse_args/_init_global_parser` |
| 3276–4936 | 子命令实现 | 装饰器 `cmd_run/cmd_parse`；`ls/version/wait/systemd/pull/push/build/up/down/ps/run/cp/exec/start/stop/restart/logs/config/port/pause/unpause/kill/stats/images` |
| 4943–5534 | 参数解析与入口 | 各子命令的 `*_parse` argparse 定义、`PullPolicyAction`、`async_main/main` |

## 核心符号索引

| 符号 | 行号 | 职责 |
|------|------|------|
| `main()` / `async_main()` | 5532 / 5528 | 进程入口，`asyncio.run` 启动 |
| `podman_compose`（模块级单例） | 3270 | `PodmanCompose()` 实例，装饰器注册目标 |
| `PodmanCompose.run()` | 2480 | 运行时入口：解析参数 → 探测 podman → 加载 compose → 分发子命令 |
| `PodmanCompose._parse_compose_file()` | 2652 | 配置加载管线主逻辑（文件发现、env、插值、合并、服务展开） |
| `PodmanCompose._parse_x_podman_settings()` | 2604 | `x-podman.*` 与 `PODMAN_COMPOSE_*` 环境变量设置解析 |
| `PodmanCompose.config_hash()` | 2525 | 服务配置的 sha256 哈希，驱动容器重建判定 |
| `PodmanCompose.get_podman_args()` | 2469 | 全局/每命令自定义 podman 参数组装 |
| `Podman` 类 | 1845 | podman CLI 的 asyncio 子进程包装 |
| `Podman.output()` | 1858 | 执行命令并捕获 stdout，非零退出抛异常 |
| `Podman.run()` | 1940 | 执行命令，支持日志前缀着色、抑制输出、dry-run、取消时 terminate/kill |
| `Podman.exec()` | 1928 | `os.execlp` 替换当前进程（用于 `wait` 等直接接管） |
| `Podman.existing_containers()` | 2046 | 按项目标签查询现存容器，解析为 `ExistingContainer` |
| `container_to_args()` | 1344 | service dict → podman argv 翻译主函数（约 280 行） |
| `container_to_build_args()` | 3580 | build 描述 → `podman build` argv |
| `var_interpolate()` | 275 | bash 风格变量插值引擎（tokenizer + 6 种操作符） |
| `rec_subs()` | 473 | 对 dict/list/str 递归做变量替换 |
| `rec_merge_one()` / `rec_merge()` | 2225 / 2311 | 多 compose 文件深合并（含 `!override/!reset` 语义） |
| `normalize_service()` | 2078 | 服务配置短语法归一化为长语法 |
| `resolve_extends()` | 2329 | `extends` 继承解析（同文件或外部文件） |
| `flat_deps()` / `rec_deps()` / `calc_dependents()` | 1719 / 1685 / 1709 | 依赖图构建：`_deps` 递归展开、`_dependents` 反向计算 |
| `ServiceDependencyCondition` | 1625 | 12 种依赖条件枚举（含 docker 条件名映射） |
| `check_dep_conditions()` | 3863 | 启动前依赖条件等待（`podman wait --condition` 轮询） |
| `compose_up()` | 4158 | up 生命周期：备镜像 → 重建判定 → 创建 → 启动 |
| `compose_down()` | 4445 | down 生命周期：停止 → 删除 → 卷/镜像/pod/网络清理 |
| `prepare_images()` / `pull_images()` | 4076 / 4039 | 镜像预拉取与构建调度（含 pull 策略优先级） |
| `create_pods()` | 3772 | pod 创建（默认参数 `--infra=false --share=`） |
| `compose_systemd()` | 3412 | systemd 用户单元注册/卸载/生成 |
| `cmd_run` / `cmd_parse` | 3280 / 3305 | 子命令与参数解析的装饰器注册器 |

## 关键版本门槛

源码中按 podman 版本做能力降级的判断点：

| podman 版本 | 影响的功能 | 实现位置 |
|-------------|-----------|---------|
| < 4.6.0 | 忽略 `healthy`/`unhealthy` 依赖条件检查（仅告警）；忽略 `--wait` | `check_dep_conditions`、`wait_for_container_running_healthy` |
| ≥ 5.6.0 | up 前显式 `podman pull --policy` 预拉取镜像（减少停机） | `prepare_images` |

## 相关信源

- [官方 README](readme-source.md)：项目介绍、安装方法与依赖说明（用户视角）

---
type: Concept
title: CLI 翻译层与标签状态
description: 源码视角解析 service dict 到 podman argv 的翻译主函数、卷网络密钥参数生成，以及标签即数据库的无状态设计
tags: [podman, compose, source-code, cli, labels, translation]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# CLI 翻译层与标签状态

podman-compose 最核心的代码资产不是任何"容器管理"逻辑，而是一个约 280 行的纯异步函数 `container_to_args()`（L1344-1622）：它把归一化后的 service dict 逐字段翻译成 `podman create/run` 的 argv 列表。本文解析这个翻译层，并说明一个配套设计——**标签即状态**。

## 翻译主函数 container_to_args

函数签名与开头：

```python
async def container_to_args(
    compose: PodmanCompose, cnt: dict[str, Any],
    detached: bool = True, no_deps: bool = False,
) -> list[str]:
    podman_args = [f"--name={cnt['name']}"]
    if detached:
        podman_args.append("-d")
```

随后按字段顺序向 `podman_args` 追加参数。主要映射分组如下（只列有实质转换的字段，原样透传的从略）：

| service 字段 | 翻译结果 / 转换逻辑 |
|--------------|--------------------|
| `pod` | `--pod=<pod 名>` |
| `_deps`（内部） | 所有依赖容器名拼接为 `--requires=<csv>`（`no_deps` 时省略） |
| `security_opt` / `annotations` / `labels` / `cap_add` / `cap_drop` / `group_add` / `devices` | 逐项 `--security-opt/--annotation/--label/--cap-add/...` |
| `env_file` | 读取文件（dotenv 解析）后逐行展开为 `-e KEY=VAL`；`required: false` 的缺失文件可跳过 |
| `environment` | 短格式（无 `=`）从 `compose.environ` 取宿主值后展开为 `-e` |
| `volumes` | 逐个 `await get_mount_args()`：生成 `-v`、`--mount` 或 `--tmpfs`，并顺带确保卷/宿主目录存在 |
| `networks` / `network_mode` | 先 `assert_cnt_nets()` 确保网络存在，再生成 `--network=...` |
| `logging` | `--log-driver=<driver>`（默认 `k8s-file`）与若干 `--log-opt` |
| `secrets` | 逐个 `get_secret_args()`（形态见下文） |
| `ports` / `expose` / `publishall` | dict 长语法经 `port_dict_to_str` 归一化后 `-p`；`publishall` → `-P` |
| `stop_grace_period` | `str_to_seconds()` 解析 `1m30s` 类时长为整数秒 → `--stop-timeout`（podman 只收 int） |
| `sysctls` | dict → `--sysctl k=v`，list 逐项透传 |
| `healthcheck` | 字符串 test 视为 `CMD-SHELL`；list 首元素决定 `NONE/CMD/CMD-SHELL`；interval/timeout/start_period/start_interval/retries 分别映射 |
| `ipc` | `host/none/private/shareable` 透传；`service:<名>` 翻译为 `container:<对方容器名>` |
| `entrypoint` | 字符串先 `shlex.split`，再 `json.dumps` 为单个参数 |
| `x-podman.uidmaps/gidmaps` | `--uidmap/--gidmap`；`x-podman.no_hosts` → `--no-hosts`；`x-podman.rootfs` → `--rootfs`（此时不追加 image） |
| `pull_policy` | 非 `build` 时 → `--pull=<policy>` |
| `image` + `command` | 追加在 argv 末尾；字符串 command 经 `shlex.split`，list 逐项字符串化 |

### 资源限制：v2/v3 双轨合并

`container_to_cpu_res_args()`（L1013）同时识别两套 Compose 语法：v2 的 `cpus/cpu_shares/mem_limit/mem_reservation` 与 v3 的 `deploy.resources.limits/reservations`，**v3 优先**，映射为 `--cpus/--cpu-shares/-m/--memory-reservation`。`pids_limit` 与 `deploy.resources.limits.pids` 若同时出现且不一致直接报错。

GPU 通过 `deploy.resources.reservations.devices` 中 `driver: nvidia` 且 `capabilities` 含 `gpu` 的设备声明翻译为 `--device nvidia.com/gpu=<id|all>`，并附加 `--security-opt=label=disable`。

### 网络：两种声明路径

- `network_mode`（L1199）：`none/host/private` 直接透传；`slirp4netns/pasta/ns:` 等 podman 特有模式透传；`service:<名>` 与 `container:<名>` 统一为 `--network=container:<容器名>`；`bridge` 模式补服务名 alias 与 mac。`networks` 与 `network_mode` 同时存在直接报错。
- `networks`（L1255）：每个网络生成一条 `--network=<名>:<选项>`，选项包括 `interface_name/ip/ip6/mac/alias`；服务级别名与网络级别名合并；容器级 `mac_address` 只应用到第一个网络，若网络级也声明了 mac 则报冲突。

### 卷：-v 与 --mount 的选择

`get_mount_args()`（L769）默认偏好 `-v`（`prefer_volume_over_mount = True`），但 `image`、`glob`、`volume` 三种类型强制走 `--mount`（部分选项只有 `--mount` 能表达，如 volume 的 `subpath`、tmpfs 的 size/mode 结构化选项）。

短语法 `src:dst:opts` 由 `parse_short_mount()`（L162）解析：源路径以 `~`、`/`、`.` 开头判为 bind（并转绝对路径），否则判为具名卷。卷名由 `fix_mount_dict()`（L224）补全：

- 匿名卷（只有容器内路径）：`fix_mount_dict()` 生成名为 `<项目>_<服务>_<目标路径 sha256>` 的卷；
- 具名卷：external 卷沿用原名，普通卷加项目前缀 `<项目>_<卷名>`。

bind 源路径不存在时 `assert_volume()`（L582）默认 `os.makedirs` 创建，除非声明 `bind.create_host_path: false`；具名卷 `volume inspect` 失败才 create，并打上项目标签、driver 与 driver_opts；external 卷缺失则报错提示手工创建。

### 密钥的三种形态

`get_secret_args()`（L838）按密钥来源分流：

| 来源 | build 时 | run 时 |
|------|----------|--------|
| `environment:` | `--secret id=<id>,env=<变量名>`，先由 `podman secret create --env` 建出 | `--secret <项目>_<密钥名>` |
| `file:` | `--secret id=<id>,src=<绝对路径>`，target 不允许含目录分隔符 | bind 挂载到 `/run/secrets/<名>`，选项固定 `ro,rprivate,rbind`，可加 z/Z 重标记 |
| `external:` 或具名 | `--secret <名>,uid=,gid=,mode=,type=,target=` 直传 podman | 同左 |

文件密钥上声明 `uid/gid/mode` 在 run 路径不被支持，仅输出告警。

## 标签即数据库：无状态的另一面

daemon-less 意味着编排器进程退出后没有任何常驻状态。podman-compose 的解法是把**身份与配置全部写进容器/网络/卷的标签**，之后所有查询都靠标签反向检索。

### 写入：服务展开时打标

`_parse_compose_file()` 为每个容器注入两类标签（L2964-3031）：

```text
io.podman.compose.project=<项目>
io.podman.compose.version=<podman-compose 版本>
io.podman.compose.service=<服务>
io.podman.compose.config-hash=<服务配置 sha256>
com.docker.compose.project=<项目>
com.docker.compose.project.working_dir=<项目目录>
com.docker.compose.project.config_files=<compose 文件列表>
com.docker.compose.service=<服务>
com.docker.compose.container-number=<序号>
PODMAN_SYSTEMD_UNIT=podman-compose@<项目>.service
```

同时兼容 `io.podman.compose.*` 与 `com.docker.compose.*` 两套前缀；网络与卷在创建时也带 `io.podman.compose.project` 标签。

### 读取：一切资源发现都走 label filter

- `Podman.existing_containers()`：`podman ps -a --filter label=io.podman.compose.project=<项目> --format json`，解析出 `ExistingContainer`（含 config_hash 与 image_id）。
- `network_ls()` / `volume_ls()`：同样以项目标签过滤。
- `down --remove-orphans`：标签查到的项目容器减去当前 compose 文件定义的服务，差额即为孤儿。

### 判定：config-hash 驱动幂等更新

`config_hash()`（L2525）对服务配置做稳定序列化（过滤 `_` 开头的内部键与 `!override/!reset` 标签对象后 `json.dumps(sort_keys=True)`）再 sha256。up 时比较现存容器标签里的 hash 与当前配置的 hash，结合镜像 ID 变化决定是否重建（完整判定流程见[依赖图与 up/down 生命周期](07-dependency-lifecycle.md)）。

## 实践含义

- **排障翻译结果**：`podman-compose --dry-run --verbose up` 会打印全部生成的 podman 命令行，任何"compose 行为不符合预期"的问题都可以先翻译成 argv 再判断是翻译层还是 podman 本身的问题。
- **手工操作可被纳管**：只要资源带有相同项目标签，podman-compose 的 ps/down/ls 就能识别；反之，手工修改容器后标签中的 config-hash 仍是旧值，下次 up 会判定配置漂移而重建。
- **扩展点是 x-podman.***：翻译层中 podman 独有的能力（uidmap/gidmap/rootfs/passwd/no_hosts、网络的 dns/routes/disable_dns）全部挂在 `x-podman.*` 扩展字段，保证标准 Compose 字段与厂商扩展在形式上分离。

## 相关概念

- [单文件架构与 asyncio 执行模型](04-source-architecture.md)：翻译层所处的分层位置
- [配置加载管线](06-config-pipeline.md)：进入翻译层之前的 service dict 如何形成
- [依赖图与 up/down 生命周期](07-dependency-lifecycle.md)：标签与 config-hash 在重建判定中的使用
- [rootless 模式下的网络与卷](02-rootless.md)：网络与卷参数的用户视角
- [源码信源登记](../references/source-code-map.md)：行号与符号索引

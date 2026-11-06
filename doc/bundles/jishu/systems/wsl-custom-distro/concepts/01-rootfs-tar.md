---
type: Tutorial
title: "01 准备与打包根文件系统 tar"
description: "rootfs 来源、两份配置文件的落位、官方 tar 命令逐段解释、根目录语义、gzip 兼容性、去宿主化清单与打包后验证"
tags: [wsl, rootfs, tar, gzip, packaging, custom-distro]
generated: { by: "reference_agent/trae-solo", at: "2026-11-06T00:00:00Z" }
status: draft
stale_after: "2027-05-31"
sources:
  - id: facts
    resource: /references/facts.md
    title: 事实清单（81 条）
  - id: ms-zh
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro
    title: 为 WSL 生成自定义 Linux 分发版（中文）
---

# 01 准备与打包根文件系统 tar

本节只做一件事：把一个**可移植的 Linux 根文件系统**装进 `tar.gz`。发行版的安装体验由后续章节的配置决定，但载荷不干净，后面所有配置都救不回来。

## 一、tar 里到底装什么

官方定义：TAR 文件包含 Linux 发行版的根文件系统（所有发行版文件）以及 WSL 配置文件；WSL 配置文件告诉 Windows 如何安装和启动发行版（F-009、F-010）。

因此 tar 的顶层应该是 `/` 的内容：

```text
install.tar.gz
├── bin/
├── etc/
│   ├── wsl.conf
│   ├── wsl-distribution.conf
│   └── ...
├── home/
├── usr/
└── var/
```

而不是：

```text
install.tar.gz
└── rootfs/          ← 错误：多套了一层目录
    ├── bin/
    └── etc/
```

官方原文：tar 的根应为文件系统的根，而不是包含根文件系统的目录（F-012）。

## 二、rootfs 从哪里来

| 来源 | 做法 | 备注 |
|---|---|---|
| 现有 Linux 发行版 | 在目标系统内清理后直接打包 | 最容易带入宿主耦合，务必做第五节的去宿主化检查 |
| 离线 rootfs / 发行版最小根 | 解压后写入配置再打包 | 最干净，推荐用于正式发布 |
| Docker 容器导出 | 参考官方「导入任意 Linux 发行版」文档中的容器导出指导（F-014） | 容器 rootfs 天然较少宿主耦合，但仍需检查内核/`resolv.conf` |

> 官方页面只给出「如何获取现有发行版 tar」的入口（F-014），不展开容器导出命令；本教程不扩写未核验的命令。

## 三、把两份配置文件放进 rootfs

打包前，rootfs 内必须已经存在：

- `/etc/wsl-distribution.conf`：发行版维护者契约（F-016）
- `/etc/wsl.conf`：运行期全局设置（F-017）

两份文件都应归 `root:root` 所有，权限 `0644`（F-073）。最小落位示例：

```bash
# 在 rootfs 内执行（chroot 或离线挂载均可）
sudo install -o root -g root -m 0644 /dev/null /etc/wsl-distribution.conf
sudo install -o root -g root -m 0644 /dev/null /etc/wsl.conf
```

文件内容分别见 [02 发行版配置文件](02-wsl-distribution-conf.md) 与 [04 wsl.conf 与 systemd](04-wsl-conf-systemd.md)。

## 四、官方推荐打包命令逐段解释

```bash
cd /path/to/rootfs
tar --numeric-owner --absolute-names -c * | gzip --best > ../install.tar.gz
```

| 片段 | 作用 | 依据 |
|---|---|---|
| `cd /path/to/rootfs` | 进入根文件系统目录，保证归档成员以根为起点 | F-011、F-012 |
| `--numeric-owner` | 以数值 UID/GID 记录属主，避免目标环境用户名映射差异 | 官方命令（F-011） |
| `--absolute-names` | 等价 `-P`，告知 tar 不剥离成员名的前导斜杠、保留绝对路径语义 | 官方命令（F-011） |
| `-c` | 创建归档 | 官方命令（F-011） |
| `*` | 由 shell 展开为当前目录下的非隐藏条目 | 官方命令（F-011）；隐藏文件行为为本库工程提示 |
| `gzip --best` | 以最高压缩级别输出 gzip 流 | F-013 |
| `> ../install.tar.gz` | 输出到 rootfs 目录之外，避免把归档自身打进去 | 官方命令（F-011） |

**压缩格式**：官方推荐 gzip，并提示其他压缩格式可能破坏与旧版 WSL 的兼容性（F-013）。不要为了体积改用 zstd/xz。

> **工程提示（本库推断，源页面未展开）**：`*` 不会匹配以 `.` 开头的顶层条目（如 `.dockerenv`、`.bashrc` 之外的顶层隐藏目录）。若 rootfs 顶层存在有意义的隐藏条目，需要显式追加；是否影响你的发行版取决于实际目录结构，建议打包后用 `tar -tzf` 核对顶层清单。

## 五、去宿主化检查：打包前必须排除的东西

官方建议中有四条直接决定载荷能否跨机器使用：

| 检查项 | 要求 | 依据 |
|---|---|---|
| `/etc/resolv.conf` | **不要**包含在 rootfs 中 | F-076 |
| 内核与 initramfs | 归档**不应**包含 | F-079 |
| `/etc/shadow` | 不应有密码哈希 | F-078 |
| `/etc/passwd` | 应包含 UID 为 0 的 root 用户 | F-077 |

打包前自检：

```bash
# 1) resolv.conf 不应存在
test ! -e /path/to/rootfs/etc/resolv.conf && echo "OK: no resolv.conf"

# 2) 不应存在内核/initramfs 文件
find /path/to/rootfs -maxdepth 2 \
  \( -name 'vmlinuz*' -o -name 'initrd*' -o -name 'initramfs*' \) -print

# 3) shadow 不应有密码哈希（第二字段非 * 或 ! 以外的内容需人工确认）
sudo awk -F: '$2 !~ /^[*!]*$/ {print $1}' /path/to/rootfs/etc/shadow

# 4) passwd 必须有 uid 0 的 root
awk -F: '$3 == 0 {print $1}' /path/to/rootfs/etc/passwd
```

> 第 3、4 条命令是本库为落地官方建议而写的检查示例，非源页面原文；判定标准以官方建议（F-077、F-078）为准。

## 六、打包后验证

```bash
# 顶层结构
tar -tzf install.tar.gz | awk -F/ '{print $1}' | sort -u | head -30

# 配置文件是否在归档内
tar -tzf install.tar.gz | grep -E '^etc/(wsl\.conf|wsl-distribution\.conf)$'

# 危险项是否混入
tar -tzf install.tar.gz | grep -E '(^etc/resolv\.conf$|(^|/)vmlinuz|(^|/)initrd|(^|/)initramfs)' || echo "OK: no host-coupled files"
```

三项都通过，再进入安装入口章节（[06](06-wsl-file-install.md)）。

## 七、常见错误

| 现象 | 根因 | 修复 |
|---|---|---|
| 安装后 shell 里看不到 `/etc/wsl-distribution.conf` | 打包时多套了一层目录（`rootfs/...`） | 回到 rootfs 根目录重新打包，确认 `tar -tzf` 顶层是 `etc/` 等 |
| 安装后网络配置异常 | 把宿主 `/etc/resolv.conf` 打进 rootfs | 删除该文件后重新打包（F-076） |
| 旧版 WSL 无法安装 | 使用了非 gzip 压缩 | 改用 `gzip --best`（F-013） |
| 文件属主错乱 | 未使用 `--numeric-owner` | 按官方命令重打（F-011） |
| 归档体积异常大 | 把 `/proc`、`/sys`、`/dev` 等伪文件系统内容打入 | 在离线 rootfs 或容器导出层打包，不要直接打包运行中系统的全部挂载点（本库工程提示） |

## 八、小结

- tar 的顶层必须是 `/` 的内容，不是包含 rootfs 的父目录（F-012）。
- 用官方命令：`--numeric-owner --absolute-names` + `gzip --best`（F-011、F-013）。
- 打包前完成四项去宿主化检查（F-076~F-079）。
- 打包后用 `tar -tzf` 做三项机械验证，再进入下一步。

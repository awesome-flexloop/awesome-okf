---
type: Tutorial
title: "04 编写 /etc/wsl.conf 并处理 systemd"
description: "运行期契约：/etc/wsl.conf 的 [boot] systemd 开关、发行版作者的默认值决策、9 个应禁用或屏蔽的 systemd 单元与落地命令"
tags: [wsl, wsl-conf, systemd, boot, custom-distro]
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

# 04 编写 /etc/wsl.conf 并处理 systemd

`/etc/wsl.conf` 与 `/etc/wsl-distribution.conf` 都在 rootfs 的 `/etc` 下，但作用时点不同：前者控制**每次启动**的系统行为，后者控制**首次安装/启动**的配置（F-016、F-017）。本节聚焦最常被改动的一项：systemd 默认开关。

## 一、两个文件的分工

| 维度 | `/etc/wsl-distribution.conf` | `/etc/wsl.conf` |
|---|---|---|
| 责任主体 | 发行版维护者（F-016） | 用户相关的全局设置（F-017） |
| 作用时点 | 首次使用 WSL 启动时（F-016） | 控制发行版启动方式（F-017） |
| 典型内容 | OOBE、默认 UID、默认名称、快捷方式、终端模板（F-019） | `[boot] systemd` 等系统设置（F-039） |
| 是否常改 | 发布时定稿 | 运行期可能被用户/发行版调整 |

## 二、最小示例

官方示例（F-039）：

```ini
# /etc/wsl.conf

[boot]
systemd=true|false
```

`systemd` 取 `true` 表示默认启用，取 `false` 表示不启用；由发行版作者决定（F-040）。`/etc/wsl.conf` 的全部受支持设置见官方 WSL 高级设置文档（F-042）。

## 三、怎么选：启用还是不启用

官方没有给出「必须启用」或「必须关闭」的结论，只规定：

- 若选择默认启用 systemd，须参考 Systemd 建议（F-041）；
- 若启用，应禁用或屏蔽可能导致 WSL 问题的单元（F-080）。

选择时可以考虑（**以下为本库判断，非官方口径**）：

| 发行版形态 | 倾向 | 理由 |
|---|---|---|
| 面向服务器/开发环境，用户预期 systemd 可用 | 启用 + 屏蔽问题单元 | 满足 `systemctl` 生态与用户预期 |
| 极简 rootfs、单进程工具环境 | 不启用 | 减少启动面与单元冲突 |
| 上游发行版默认启用 | 跟随上游 + 屏蔽清单 | 降低与发行版文档的偏差 |

## 四、9 个应禁用或屏蔽的单元

官方列出的已知问题单元（F-080），同时适用于 system 与 user 单元（F-081）：

| # | 单元 | 类型 |
|---|---|---|
| 1 | `systemd-resolved.service` | system |
| 2 | `systemd-networkd.service` | system |
| 3 | `NetworkManager.service` | system |
| 4 | `systemd-tmpfiles-setup.service` | system |
| 5 | `systemd-tmpfiles-clean.service` | system |
| 6 | `systemd-tmpfiles-clean.timer` | system（timer） |
| 7 | `systemd-tmpfiles-setup-dev-early.service` | system |
| 8 | `systemd-tmpfiles-setup-dev.service` | system |
| 9 | `tmp.mount` | system（mount） |

> 官方页面只说明这些单元「已知会导致 WSL 分发中的问题」，未逐项给出原因（F-080）。本教程不补写未核验的因果解释。

## 五、在 rootfs 内屏蔽

屏蔽必须在**打包前**完成；安装后再改属于对已安装实例的修补，不会影响其他用户。

```bash
# 在 rootfs 内（chroot 或离线环境）执行
for unit in \
  systemd-resolved.service \
  systemd-networkd.service \
  NetworkManager.service \
  systemd-tmpfiles-setup.service \
  systemd-tmpfiles-clean.service \
  systemd-tmpfiles-clean.timer \
  systemd-tmpfiles-setup-dev-early.service \
  systemd-tmpfiles-setup-dev.service \
  tmp.mount
do
  systemctl mask "$unit"
done
```

> **命令说明（本库建议）**：官方原文只要求「禁用或屏蔽」（disable or mask），未给出命令。`systemctl mask` 通过符号链接到 `/dev/null` 阻止启动，比 `disable` 更强；若你的构建环境不允许运行 systemctl，可在离线 rootfs 中手工创建同名链接，或使用发行版的预设（preset）机制。

## 六、验证

打包前：

```bash
# 已屏蔽的单元应显示 masked
for unit in systemd-resolved.service systemd-networkd.service NetworkManager.service; do
  printf '%-40s %s\n' "$unit" "$(systemctl is-enabled "$unit" 2>&1)"
done
```

安装后（进入发行版 shell）：

```bash
systemctl is-system-running 2>&1 || true
systemctl is-enabled systemd-resolved.service 2>&1
```

> 这两组验证命令是本库为落地官方建议而写，非源页面原文；`is-system-running` 的输出随环境不同（如 `running`、`degraded`），不应把单一值当作验收标准。

## 七、常见错误

| 现象 | 可能原因 | 修复 |
|---|---|---|
| 安装后 systemd 相关服务异常 | 启用了 systemd 但未屏蔽 9 个单元（F-080） | 在 rootfs 内 mask 后重打 |
| 改了 `/etc/wsl.conf` 但启动行为不变 | 改的是已安装实例；或存在用户级覆盖 | 修改 rootfs 后重新安装；检查实例内配置 |
| 打包后配置权限不对 | 未设置 `root:root 0644`（F-073） | 打包前 `chown`/`chmod` |
| 不确定还有哪些设置 | 只看了本文 | 查官方 WSL 高级设置文档（F-042） |

## 八、小结

- `/etc/wsl.conf` 是运行期契约，`[boot] systemd` 的默认值由发行版作者决定（F-039、F-040）。
- 启用 systemd 就必须处理 9 个已知问题单元（F-080、F-081），并在打包前完成屏蔽。
- 两个 `/etc` 配置文件都要 `root:root 0644`（F-073）。

下一步：[05 生成 Windows Terminal 配置](05-terminal-profile.md)。

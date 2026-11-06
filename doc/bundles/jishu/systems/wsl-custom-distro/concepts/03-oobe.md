---
type: Tutorial
title: "03 编写 OOBE 首次启动脚本"
description: "OOBE 的运行时机与失败语义、官方示例脚本的语义重建、幂等短路、创建/加组/回滚链、设计检查表与测试矩阵"
tags: [wsl, oobe, user-creation, bash, adduser, custom-distro]
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

# 03 编写 OOBE 首次启动脚本

OOBE（开箱体验，out of box experience，F-028）是发行版安装后的**唯一一次用户创建窗口**。它由 `/etc/wsl-distribution.conf` 的 `oobe.command` 指定，在用户第一次打开交互式 shell 时运行；返回非零即判定失败，用户将无法打开 shell（F-020）。

## 一、执行语义

| 项 | 规则 | 依据 |
|---|---|---|
| 触发时机 | 用户首次在发行版中打开交互式 shell | F-020 |
| 运行身份 | 以 `oobe.defaultUid` 作为默认 UID | F-021 |
| 成功条件 | 命令退出码为 0 | F-020 |
| 失败后果 | 用户无法打开 shell | F-020 |
| 幂等要求 | 脚本需自行处理「用户已存在」 | F-030（官方示例做法） |

> **这不是「可选装饰」**：OOBE 失败是单点否决。一个只在特定用户名下失败的脚本，会让发行版在部分用户机器上表现为「装好了但进不去」。

## 二、官方示例脚本（语义重建版）

> **来源说明**：官方中英文页面的代码块均存在换行丢失（F-032、D-03）：`DEFAULT_UID` 定义与后续 `echo` 合并、`fi while` 合并、`fi done` 合并。以下版本按 Bash 语法重建语义，**不是逐字复制**；变量值、命令顺序与回滚逻辑与原文一致（F-029~F-031）。

**损坏形态与重建结果逐行对照（S-03）**

| 官方原文（损坏形态） | 重建后的语义 |
|---|---|
| `DEFAULT_UID='1000' echo 'Please create ...'` | 先定义 `DEFAULT_UID`，再执行后续两条 `echo` |
| `fi while true; do` | 结束幂等判断的 `if`，再进入用户名输入循环 |
| `fi done` | 依次结束内层 `if` 与外层 `while` |

```bash
#!/bin/bash
# 注意：本脚本是官方示例的语义重建版（源页面代码块换行丢失），逐行对照见上表
set -ue

DEFAULT_GROUPS='adm,cdrom,sudo,dip,plugdev'
DEFAULT_UID='1000'

echo 'Please create a default UNIX user account. The username does not need to match your Windows username.'
echo 'For more information visit: https://aka.ms/wslusers'

# 幂等短路：该 UID 已存在则跳过创建
if getent passwd "$DEFAULT_UID" > /dev/null ; then
  echo 'User account already exists, skipping creation'
  exit 0
fi

while true; do
  # 读取用户名
  read -p 'Enter new UNIX username: ' username

  # 创建用户
  if /usr/sbin/adduser --uid "$DEFAULT_UID" --quiet --gecos '' "$username"; then
    if /usr/sbin/usermod "$username" -aG "$DEFAULT_GROUPS"; then
      break
    else
      # 加组失败：回滚已创建的用户
      /usr/sbin/deluser "$username"
    fi
  fi
done
```

## 三、逐段解释

| 片段 | 作用 | 设计意图 |
|---|---|---|
| `set -ue` | 遇未定义变量或命令失败即退出 | 让失败尽早暴露，避免带病继续 |
| `DEFAULT_GROUPS` | 默认附加组：`adm,cdrom,sudo,dip,plugdev` | 提供 sudo、网络管理等基础权限（F-029） |
| `DEFAULT_UID='1000'` | 与 `oobe.defaultUid` 对齐 | 官方建议两者都设为 1000（F-074） |
| `getent passwd "$DEFAULT_UID"` | 按 UID 查询是否已存在 | 幂等：重复启动不重复建用户（F-030） |
| `read -p` | 交互式读取用户名 | 首次启动需要 TTY；非交互场景会失败 |
| `adduser --uid ... --quiet --gecos ''` | 创建用户并固定 UID | Debian 系工具；`--gecos ''` 跳过全名等字段（F-031） |
| `usermod -aG` | 追加附加组 | 不覆盖用户已有组（F-031） |
| `deluser` | 加组失败时回滚 | 避免留下「无权限的半成品用户」（F-031） |
| `while true` | 直到创建成功才退出 | 输错用户名可重试（F-031） |

## 四、幂等、回滚与可诊断

**幂等**：官方示例用 UID 查询做短路（F-030）。这解决「用户已存在」的重复执行问题，但不解决「用户名已存在但 UID 不同」的情况——`adduser` 会失败并进入循环。是否额外检查用户名，取决于你的发行版策略。

**回滚**：官方示例只在 `usermod` 失败时 `deluser`（F-031）。如果 `adduser` 本身部分成功（例如创建了 home 但未写 passwd），脚本不会清理。更稳妥的做法是把「创建」与「验证」分开，并在失败分支输出可诊断信息。以下为**本库建议，非官方原文**：

```bash
if ! /usr/sbin/adduser --uid "$DEFAULT_UID" --quiet --gecos '' "$username"; then
  echo "OOBE: adduser failed for '$username'" >&2
  continue
fi
if ! /usr/sbin/usermod "$username" -aG "$DEFAULT_GROUPS"; then
  echo "OOBE: usermod failed for '$username', rolling back" >&2
  /usr/sbin/deluser "$username" || true
  continue
fi
break
```

**可诊断**：OOBE 失败时用户看不到 shell，错误信息可能无处可看。把关键失败写到 stderr，并在发行版文档中给出「如何用 root 进入排查」的说明（本库建议）。

## 五、设计检查表

- [ ] 脚本首行 shebang 正确（`#!/bin/bash`），并设置 `set -ue`
- [ ] `DEFAULT_UID` 与 `oobe.defaultUid` 一致（官方建议均为 1000，F-074）
- [ ] 有「UID 已存在」的幂等短路（F-030）
- [ ] 创建成功后追加默认组（F-029）
- [ ] 加组失败时有回滚（F-031）
- [ ] 每个失败分支都有 stderr 输出
- [ ] 在目标发行版上确认 `/usr/sbin/adduser`、`/usr/sbin/usermod`、`/usr/sbin/deluser` 存在（非 Debian 系可能路径不同）
- [ ] 脚本权限可执行，路径与 `oobe.command` 一致

## 六、测试矩阵

| 用例 | 预期 | 验证点 |
|---|---|---|
| UID 1000 已存在 | 立即退出 0 | 不重复创建（F-030） |
| 正常用户名 | 创建用户、加入 5 个组、进入 shell | 主路径 |
| 用户名非法（含空格/特殊字符） | `adduser` 失败，循环重新提示 | 不退出、不半成品 |
| `usermod` 失败（可人为注入） | 回滚用户，循环继续 | 不留下无权限用户（F-031） |
| 非交互执行（stdin 关闭） | `read` 失败 → 脚本非零退出 | 符合「失败即拒绝 shell」（F-020） |
| 重复安装/重复首次启动 | 短路成功 | 幂等 |

## 七、常见坑

| 坑 | 表现 | 处理 |
|---|---|---|
| 把脚本写成「尽力而为」 | 某条命令失败但脚本继续，最终退出 0，用户拿到残缺账户 | 关键步骤必须显式判断并回滚 |
| 忘记 `exit 0` 短路 | 已存在用户时继续走 `read`，阻塞或失败 | 按官方示例先 `getent` 再 `exit 0` |
| UID 与 `defaultUid` 不一致 | 启动 UID 与创建 UID 错位，权限异常 | 两处都锚定 1000（F-074） |
| 使用非 Debian 系工具路径 | `adduser`/`usermod` 不存在，OOBE 直接失败 | 按目标发行版替换命令并实测 |
| 只在开发机测过 | 特定用户名/组缺失时才失败 | 按第六节矩阵覆盖 |

## 八、小结

- OOBE 是「一次性、可否决」的安装期钩子（F-020）。
- 官方示例的核心是：幂等短路 → 创建 → 加组 → 失败回滚（F-030、F-031）。
- 把 `DEFAULT_UID` 与 `oobe.defaultUid` 都锚到 1000（F-074），并按测试矩阵验证。

下一步：[04 wsl.conf 与 systemd](04-wsl-conf-systemd.md)。

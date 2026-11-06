---
type: Tutorial
title: "06 创建 .wsl 文件并安装"
description: "把 tar 重命名为 .wsl、双击安装的 defaultName 前提、--from-file 安装、wsl --list --online 与 wsl --install 三种入口对比"
tags: [wsl, .wsl, installation, from-file, double-click, custom-distro]
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

# 06 创建 .wsl 文件并安装

打包完成后，最后一步安装入口简单到只有一次重命名：把 `.tar` 改成 `.wsl`，文件就被标记为 WSL 发行版（F-043）。但「能装」和「装得对」之间还有 `oobe.defaultName` 这个前提（F-045）。

## 一、重命名为 `.wsl`

```powershell
# Windows PowerShell
Rename-Item .\install.tar.gz my-distro.wsl
```

- 重命名即标记，不需要专用打包工具（F-043）。
- 重命名后，在文件资源管理器中双击即可安装（F-044）。
- 双击安装要求 `/etc/wsl-distribution.conf` 中存在 `oobe.defaultName`（F-045）。

> 扩展名从 `.tar.gz` 直接改为 `.wsl` 不影响内容；WSL 按 tar 读取（F-007）。若你的构建产物是 `.tar` 而非 `.tar.gz`，同样改名为 `.wsl`。

## 二、三种安装入口

| 入口 | 命令/操作 | 前置条件 | 适用场景 |
|---|---|---|---|
| 直接安装文件 | `wsl --install --from-file <fileLocation>` | `.wsl` 文件可访问 | 拿到文件后本地/脚本安装（F-049） |
| 双击安装 | 资源管理器中双击 `.wsl` | `oobe.defaultName` 已设置（F-045） | 面向普通用户分发 |
| 在线列表安装 | `wsl --list --online` → `wsl --install <distroName>` | 发行版已进入清单（F-046~F-048） | 已上架官方或企业清单 |

三种入口最终都落成同一个安装动作；区别在于「发行版如何被发现」。

## 三、用 `--from-file` 安装

```powershell
wsl --install --from-file .\my-distro.wsl
```

- 参数 `<fileLocation>` 替换为文件实际位置（F-049）。
- 安装后在开始菜单/终端中应出现发行版条目（取决于 `shortcut.enabled` 与 `windowsterminal.enabled`）。
- 若安装后首次打开 shell 失败，优先检查 OOBE 脚本退出码（F-020）。

## 四、双击安装

1. 确认 `/etc/wsl-distribution.conf` 有 `oobe.defaultName`：

   ```ini
   [oobe]
   defaultName = my-distro
   ```

2. 将 `.wsl` 文件交给用户，双击。
3. 安装过程中系统会按配置创建开始菜单快捷方式与终端配置文件（F-024、F-026）。

> 缺少 `defaultName` 时，双击体验不工作（F-045）；这种情况下改用 `--from-file` 仍可能安装成功，但注册名与预期可能不同。正式分发建议两者都保证。

## 五、用在线列表安装

```powershell
wsl --list --online
wsl --install my-distro
```

- `wsl --list --online` 展示可用发行版（F-046）。
- `wsl --install <distroName>` 按清单选择版本（F-047）。
- 列表由清单文件控制（F-048）；清单结构与本地覆盖见 [07](07-manifest-local-test.md)。

## 六、安装后验收

| 检查项 | 命令/观察点 | 依据 |
|---|---|---|
| 发行版已注册 | `wsl --list --verbose` | 通用 WSL 命令；本页未展开 |
| 默认名称正确 | 列表名称与 `oobe.defaultName` 一致 | F-022、F-045 |
| 首次启动能进 shell | 打开该发行版 | F-020 |
| 用户已创建且在 sudo 组 | 进入后 `id` | F-029、F-031 |
| 终端配置已生成 | Windows Terminal 中出现该发行版配置 | F-033、F-036 |
| 快捷方式已生成 | 开始菜单中出现条目 | F-024 |

> 第一行 `wsl --list --verbose` 属 WSL 通用命令，不是本页原文；其余检查点均可回溯到官方事实。

## 七、常见错误

| 现象 | 可能原因 | 修复 |
|---|---|---|
| 双击无反应 | 缺 `oobe.defaultName`（F-045） | 补配置后重新打包 |
| `--from-file` 报文件无效 | 文件不是 tar 或扩展名/内容不匹配 | 用 `tar -tzf` 验证内容，再改名 |
| 安装成功但首次启动直接退出 | OOBE 返回非零（F-020） | 修正 OOBE 脚本 |
| 列表里有但安装失败 | 清单 URL/SHA256/架构不匹配（F-052、F-057） | 核对清单条目与文件摘要 |
| 安装后名称与预期不同 | 用了 `--name` 覆盖或 `defaultName` 不一致（F-022） | 统一命名策略 |

## 八、小结

- `.wsl` 就是 tar 改名（F-043），双击安装额外要求 `defaultName`（F-045）。
- 三条安装入口：`--from-file`、双击、`wsl --install <distro>`（F-049、F-047）。
- 装完按验收表检查注册名、首次启动、用户、终端配置与快捷方式。

下一步：[07 清单结构与本地测试](07-manifest-local-test.md)。

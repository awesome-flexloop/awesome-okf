---
okf_version: "0.2"
type: Example
title: "安装 Agent Reach 并完成首次体检"
description: "Python 3.10+ 前置检查、pipx/venv 安装、一句话安装、install 三档授权、doctor/--json 体检、OpenClaw 前置与干净卸载的可照做流程"
tags: [agent-reach, install, pipx, doctor, openclaw, uninstall]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-08T12:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# 示例 00：安装 Agent Reach 并完成首次体检

> 可复现流程。命令以官方 docs/install.md 与 README 为准（F-065/F-066），博文命令（F-045~F-047）经逐字核验。
> ⚠️ 本知识包未在本机实际执行安装，以下为官方文档口径的照做流程；动手前建议先通读，先 dry-run 再真装。

## 前置条件

- **Python 3.10+**（F-006/F-059）。检查：

```bash
python3 --version    # macOS/Linux
py -3 --version      # Windows（见下方 Windows 说明）
```

- 推荐用 **pipx** 安装以避免污染系统 Python（F-045）。没有 pipx 时先装 pipx（`pip install --user pipx` 后 `pipx ensurepath`），或使用虚拟环境：

```bash
python3 -m venv .venv && source .venv/bin/activate   # macOS/Linux
py -3 -m venv .venv; .venv\Scripts\Activate.ps1      # Windows PowerShell
```

- **Windows 特别说明（F-048）**：如果敲 `python3` 弹出 Microsoft Store，那是 Windows 的 Store alias，不是真正的 Python，请改用 **`py -3`** 调用 Python 启动器。

> 🚫 **供应链警告（F-069）**：官方明确**不要从 PyPI 安装同名包**。请使用下面的 GitHub archive 地址，或让 Agent 读取官方 install.md 安装。

## 第一步：安装 CLI（两条路任选）

### 路径 A：pipx 直接装（博文推荐，F-045）

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
```

> 该命令逐字出自官方 **docs/install.md**（F-066）。README 正文本身不出现 pipx 字样，它主推路径 B。

### 路径 B：把"一句话"发给 Agent（官方主推，F-041）

在 Claude Code / Cursor / OpenClaw 中直接发送：

```text
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Agent 会读取该文档，自行决定安装内容、顺序与失败重试路径（F-041）。

**OpenClaw 用户前置（F-068）**：OpenClaw 需要先开启 exec 权限，Agent 才能执行安装命令：

```bash
openclaw config set tools.profile "coding"
```

## 第二步：按三档授权执行 install

安装 CLI 本体后，执行环境检查与上游工具接线。务必理解三档语义（F-034/F-035，见 [概念 02](../concepts/02-doctor-health-and-security-model.md)）：

```bash
agent-reach install --env=auto               # ① 默认只读：只列出缺什么，不装包、不写配置
agent-reach install --env=auto --dry-run     # ② 预览：把将执行的全部动作列出，一个字节不改
agent-reach install --env=auto --system      # ③ 显式授权：确认预览无误后，才真正动系统安装
```

建议顺序：先跑①看缺口 → 再跑②看计划 → 确认后才跑③。`--env=auto` 表示自动探测当前 shell/Agent 环境；README 另有 `--safe` 开关（F-065）。

## 第三步：体检（文本 + JSON 两种看法）

```bash
agent-reach doctor         # 人读的文本报告
agent-reach doctor --json  # 给 Agent 的结构化报告
```

doctor 会**真实执行**各渠道上游命令，按 `missing` / `broken` / `timeout` 三态报告并给出安装/重装/网络凭据处方（F-020）。JSON 中的 `active_backend` 标明每个渠道当前实际使用的后端，为 `null` 表示该渠道暂无可用后端（F-021/F-065）。

在 Agent 工作流中，官方 SKILL.md 定的纪律是"动手调用某渠道前先 `doctor --json` 确认 `active_backend`"（F-040）。

## 第四步：按需解锁渠道

默认激活的 6 个零配置渠道（网页/YouTube/GitHub/RSS/Exa/V2EX）体检通过即可用，见 [示例 01](01-zero-config-channels.md)。其余渠道直接对 Agent 说"帮我配 XXX"，按引导完成：

- 一句话解锁：Twitter/X、雪球、小宇宙、LinkedIn、Boss直聘
- 需登录态：小红书、Reddit、Facebook、Instagram（配置与 Cookie 安全见 [示例 02](02-login-channels-and-cookie-safety.md)）

## 干净卸载

```bash
agent-reach uninstall --dry-run      # 先预览会删除什么
agent-reach uninstall                # 确认后真删：配置目录、各 Agent 的 skill 文件、MCP 配置
```

需要保留凭据以便日后重装时加 `--keep-config`（F-037/F-047）。凭据文件位于 `~/.agent-reach/config.yaml`（Windows 为 `%USERPROFILE%\.agent-reach\config.yaml`），权限 600（F-036）。

## 排障速查

| 现象 | 处理 |
|------|------|
| `python3` 弹出 Microsoft Store | Windows Store alias，改用 `py -3`（F-048） |
| doctor 报某后端 `missing` | 按输出给出的安装命令装对应上游（如 bili-cli/gh），或对 Agent 说"帮我配 XX" |
| doctor 报 `broken`（如 shebang 失效） | 按输出的重装处方重建上游工具的虚拟环境（F-020） |
| doctor 报 `timeout` | 检查网络/代理；登录态渠道检查 Cookie/Token 是否过期（F-020/F-068） |
| OpenClaw 中 Agent 不执行安装 | 先 `openclaw config set tools.profile "coding"` 开 exec 权限（F-068） |
| 装了 PyPI 同名包 | 官方警告该渠道不可信，卸载后改用 GitHub archive / install.md 重装（F-069） |

## 下一步

- [示例 01：零配置渠道实操](01-zero-config-channels.md)
- [示例 02：登录态渠道与 Cookie 安全](02-login-channels-and-cookie-safety.md)

---
okf_version: "0.2"
type: Example
title: "安装 Oracle 并跑通 Browser Mode 首次登录"
description: "Node 24+ 前置检查、brew/npm/npx 三种安装、manual-login 首次登录、dry-run 预演与常见平台坑"
tags: [Oracle, 安装, Browser Mode, manual-login, Node.js, 实战]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/_J1BzyqyoNWuj_998DLo1g
  - id: docs-install
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/install.md
  - id: docs-browser
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/browser-mode.md
---

# 安装 Oracle 并跑通 Browser Mode 首次登录

> **可复现性声明**：博文（「Leon学AI」2026-08-30）作者是工具推荐者，行文为"有人开源做好了"，**未声明一手实测**；本篇步骤以官方仓库 `docs/install.md`、`docs/browser-mode.md`（2026-09-16 main 分支）与 npm 包页为依据整理，博文命令与之逐项核验一致。Oracle 月度级发版（核验时 npm 0.20.2），参数以本机 `oracle --help --verbose` 实际输出为准。

## 0. 前置条件

| 条件 | 要求 | 检查 |
|------|------|------|
| Node.js | **24 或更新**（博文未提，最常见踩坑点） | `node --version` |
| 浏览器 | Google Chrome（Chromium 系亦可，部分路径有差异） | — |
| 系统 | macOS / Linux 可 brew；**Windows 用 npm/npx**；窗口隐藏等特性仅 macOS 完整 | `uname -a` / `winver` |
| 账号 | 可正常登录 chatgpt.com 的订阅账号；具体哪些档位能用 Pro/Thinking 模型以 OpenAI 官方规则为准（官方文档未声明门槛） | 浏览器手登一次确认 |

不满足 Node 24 时先用 nvm/fnm/volta 等升级，再继续。

## 1. 安装（三选一）

**方式 A：Homebrew（macOS / Linux）** —— 博文方式一：

```bash
brew install steipete/tap/oracle
```

**方式 B：npm 全局安装（全平台，含 Windows）** —— 博文方式二：

```bash
npm install -g @steipete/oracle
# 或 pnpm add -g @steipete/oracle
```

**方式 C：免安装试运行（npx，CI/试用推荐）**：

```bash
npx -y @steipete/oracle --help
```

验证安装：

```bash
oracle --version
oracle --help --verbose   # 看清当前版本真实参数集（模型别名等迭代很快）
```

> 博文只给了 A、B 两条命令且未写平台限定（F-012/F-013）：Windows 上没有 brew，直接走 B/C。

## 2. 首次登录：manual-login 持久化会话

博文命令（F-014）：

```bash
oracle --engine browser --browser-manual-login --browser-keep-browser -p "HI"
```

执行后发生什么（官方机制，F-030/F-031）：

1. Oracle 弹出一个 **独立的 Chrome 窗口**，使用持久化自动化 profile（`~/.oracle/browser-profile/`，与你日常 Chrome profile 隔离）
2. 在该窗口里**手动登录 chatgpt.com**；Oracle 轮询会话状态，检测到登录成功后自动继续
3. 它把 `"HI"` 作为一次真实咨询发出——用于验证整条链路
4. 因为带了 `--browser-keep-browser`，跑完 Chrome 窗口保留；以后省略此参数则跑完关窗，但登录态仍保存在磁盘 profile 里

官方文档的等价示例显式指定了模型，可按需采用：

```bash
oracle --engine browser \
  --browser-manual-login \
  --browser-keep-browser \
  --model "GPT-5.5 Pro" \
  -p "Say hi"
```

> 模型名/选择器口径随 ChatGPT 改版变化（核验时官方文档已出现 gpt-5.6-sol/gpt-6-pro 等别名，且 0.15.2 曾有标签归一化缺陷）。不确定时**先不要传 `--model`**，让 ChatGPT 保持当前选择，或查 `oracle --help --verbose` 与官方文档（F-036）。

## 3. 第二次运行：零操作复用登录态

profile 已持久化，直接发真实任务即可，不再需要手动登录（F-015）：

```bash
oracle --engine browser \
  -p "审查这个模块有没有竞态条件，给出修改建议" \
  --file "src/oracle/**/*.ts" \
  --file "!**/*.test.ts"
```

## 4. 官方 Golden path：先预演，再发送

任何正式咨询前，先本地预览 bundle（不联系模型、不花任何额度，F-033）：

```bash
# 预览将解析到哪些文件 + token 估算
oracle --dry-run summary --files-report \
  -p "审查模型运行器的竞态条件" \
  --file "src/oracle/**/*.ts" \
  --file "!**/*.test.ts"

# 只渲染不发送（Render 路径），可人工检查/复制
oracle --render \
  -p "审查包元数据的发布风险" \
  --file package.json
```

文件选择规则（F-032）：`--file` 接文件/目录/glob，可重复、可逗号分隔，`!` 开头排除；默认忽略 `node_modules`/`dist`/`.git` 等并尊重 `.gitignore`；单文件默认上限 1 MB；浏览器路径约 60k 字符以内内联粘贴、超出自动转上传打包。

## 5. 长回答别重跑：会话重连

浏览器路径下 Pro/Thinking 回答可能超过默认等待（F-029）：

```bash
oracle status --hours 72        # 找会话 id
oracle session <id> --render    # 接住已完成/仍在跑的回答
```

## 6. 常见坑

| 现象 | 原因/处理 |
|------|-----------|
| `npm install -g` 后 oracle 报 Node 版本错 | Node 低于 24，升级运行时（F-024） |
| Windows 照抄 brew 失败 | brew 包只发 macOS/Linux；用 npm 或 npx（F-025） |
| 弹的 Chrome 里已登录但轮询不过 | 确认登录发生在 **Oracle 弹出的那个窗口/profile**，不是你日常 Chrome；必要时删 `~/.oracle/browser-profile/` 重走首登 |
| 想直接用日常 Chrome 的登录态 | 用 `--browser-attach-running` 挂已开远程调试（9222）的 Chrome；避免直接拷活 profile cookie（token 轮换可能连累正常会话，F-030） |
| 回答超时就重发 | 禁止；先 `oracle session <id>` 重连，重复提交可能占用账号侧限流（F-033） |
| 传了 `--model` 但报档位不可用 | Pro 档 fail-closed：无法确认选中即中止；换账号可用档位或不传 model（F-036） |

## 7. 卸载/清理

```bash
npm uninstall -g @steipete/oracle    # 或 brew uninstall steipete/tap/oracle
rm -rf ~/.oracle                     # 会话、配置、浏览器 profile 全在此（按需备份）
```

下一步：[实战 01 · 把 Oracle 接进 Codex](01-codex-skill-integration.md)。

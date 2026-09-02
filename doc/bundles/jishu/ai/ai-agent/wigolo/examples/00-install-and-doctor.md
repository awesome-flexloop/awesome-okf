# 实战 00 · 安装、体检与卸载

> 事实锚点：F-022、F-024、F-043、F-044、F-045、F-049
> 命令来源：官方 docs/getting-started.md、docs/troubleshooting.md（2026-09-02 核验）

## 环境要求

| 项 | 要求 |
|----|------|
| Node.js | **20 / 22 / 24 LTS**（过新的非 LTS 版本可能无预编译二进制，会尝试源码编译，需要 C/C++ 工具链） |
| 磁盘 | 约 1.5GB：本地 embedding+reranking 模型约 250MB + 无头浏览器引擎约 0.5–1GB |
| 系统 | macOS / Linux / Windows 均支持；Windows 数据目录为 `%USERPROFILE%\.wigolo` |
| Python | **不需要**（仅可选搜索引擎 sidecar 用得到，"Python 3 not found" 提示可忽略） |

## 第一步：初始化

```bash
npx wigolo init
```

`init` 默认**无人值守**（无交互提示，可安全用于脚本和 CI），它会完成全套设置（F-043）：

1. 下载无头浏览器引擎
2. 下载本地 ranking 与 embedding 模型
3. 逐组件验证并打印报告——失败项会被**大声点名**而不是拖到首次使用才暴露
4. 降级组件**不会**中止安装：报告中列出，init 仍退出 0（Agent 接线、配置落盘都完成），该组件首次使用时懒重试；非零退出只保留给"请求的 Agent 注册失败"这类硬错误

### 常用变体

| 命令 | 用途 |
|------|------|
| `npx wigolo init --agents=claude-code` | 初始化同时接线 Coding Agent（逗号分隔多个，见[实战 01](01-connect-agents.md)） |
| `npx wigolo init --no-warmup` | 跳过全部下载，组件首次使用时懒加载（磁盘紧张/网络差时用） |
| `npx wigolo init --interactive` | 纯文本引导流程（选 Agent、onboarding 问答） |
| `npx wigolo init --wizard` | 富引导 TUI |
| `npx wigolo init --json` | stdout 输出机器可读摘要 |

## 第二步：第一次搜索（不依赖 Agent）

每个工具都能作为一次性 CLI 命令直接跑（F-043）：

```bash
npx wigolo search "css container queries" --limit=2
```

官方文档中的真实输出样例：

```text
Search: "css container queries" (2 results, 1357ms, engines: bing, duckduckgo)
  [1] CSS container queries - CSS | MDN - MDN Web Docs - developer.mozilla.org (score: 1.00)
      CSS container queries Container queries enable you to apply styles to an
      element based on certain attributes of its container ...
  [2] Using container size and style queries - CSS | MDN - developer.mozilla.org (score: 0.85)
      Using container size and style queries Container queries enable you to
      apply styles to elements nested within a specific container ...
```

抓一个页面转 Markdown：

```bash
npx wigolo fetch https://example.com --max-content-chars=400
```

任意工具命令加 `--json` 即可在 stdout 得到机器可读结果，方便接脚本：

```bash
npx wigolo search "local-first web search" --limit=5 --json
```

## 第三步：体检与冒烟测试

```bash
npx wigolo doctor
```

`doctor` 报告（F-044）：数据目录、浏览器引擎、本地模型、已配置的 LLM provider、搜索后端、**逐引擎状态**——包括哪些可选引擎想要 Key 以及具体是哪个环境变量（如 `WIGOLO_GITHUB_TOKEN`、`BRAVE_API_KEY`）。

自动修复已知故障类：

```bash
npx wigolo doctor --fix
```

端到端能力冒烟（真实网络 + 真实抽取；退出码 0 = 全部通过或跳过，1 = 有失败）：

```bash
npx wigolo verify
```

## 故障自助速查

| 症状 | 处理 |
|------|------|
| init 时某组件下载失败 | `npx wigolo warmup --all` 重跑下载（或 `--browser` / `--reranker` / `--embeddings` 只补一个）；失败不阻塞其他组件 |
| Linux 浏览器引擎起不来 | `npx wigolo warmup --browser` 安装系统依赖库；装不了时会打印确切的手动安装命令 |
| `wigolo serve` 提示端口占用 | daemon 故意不自动换端口，报错会给出可用端口，如 `wigolo serve --port 3334` |
| 搜索结果稀薄/某引擎像死了 | 查返回体 `engine_warnings` / `engine_telemetry` / `engine_pool` 与 doctor 逐引擎表 |
| 结果陈旧 | 调用传 `force_refresh: true`，或 `wigolo cache clear --url-pattern="*example.com*"` |
| 公司代理 | 设 `USE_PROXY=true` 和 `PROXY_URL`（凭据进系统钥匙串不落盘）；TLS 审计代理加设 `NODE_EXTRA_CA_CERTS` |
| 慢网/CDN 受限 | 下载断点续跑；浏览器 CDN 可设 `PLAYWRIGHT_DOWNLOAD_HOST` 镜像 |

日志全部走 stderr（默认结构化 JSON；`LOG_FORMAT=text` 人类可读，`LOG_LEVEL=debug` 加细节），没有隐藏日志目录。

## 清理与卸载

```bash
# 回收模型/浏览器占用的磁盘（约 1.5GB），配置保留
npx wigolo config --cleanup

# 完整卸载
npx wigolo config --uninstall --yes
```

## 离线机预置技巧

在联网机器上执行 `npx wigolo warmup --all`，然后把它的 `~/.wigolo` 目录整个拷贝到离线目标机，即可预置模型与浏览器。注意：搜索和抓取在查询时仍需联网，能预置的只是模型/浏览器**下载物**（F-049）。

---

下一篇：[实战 01 · 接入 Agent 与配置 LLM](01-connect-agents.md)

---
okf_version: "0.2"
type: Example
title: "REST API、Docker 自托管与 LLM 配置"
description: "wigolo serve 守护进程、curl 调用 /v1/{tool}、OpenAPI 3.1、Docker stdio/HTTP 两模式、WIGOLO_API_TOKEN fail-closed、Gemini/Ollama 等 LLM 合成层配置"
tags: [wigolo, rest-api, docker, self-hosting, llm, gemini, ollama, openapi]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T21:20:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
  - id: official-installation
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/installation.md
  - id: official-cli
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/cli.md
---

# 示例 02：REST API、Docker 自托管与 LLM 配置

> 对应博文"进阶玩法"与"配 LLM"两节（F-020~F-026）。命令经 README/installation.md/cli.md 逐字核验（F-046~F-050）。

## 1. REST 守护进程

不绑定编辑器时，把 wigolo 当作独立服务跑（博文 F-020）：

```bash
wigolo serve
# 默认监听 127.0.0.1:3333（仅回环，本机访问免 token）
```

可选参数（F-049）：

```bash
wigolo serve --port 4000 --host 127.0.0.1
wigolo serve --host 0.0.0.0 --allow-unauthenticated   # 显式开放（不推荐）
```

curl 调用（博文 F-021 示例，与官方 README 逐字一致）：

```bash
curl -sX POST http://127.0.0.1:3333/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"local-first software","max_results":5}'
```

- `POST /v1/{tool}` 覆盖**全部 10 个工具**（F-049），例如 `/v1/fetch`、`/v1/crawl`、`/v1/research`；
- `GET http://127.0.0.1:3333/openapi.json` 返回 **OpenAPI 3.1** 契约，可直接生成客户端（F-021/F-049）；
- 同一端口还提供 `/mcp` 与 `/sse`，远程 MCP 客户端无需另开服务（F-049）。

## 2. Docker 部署

### 模式 A：MCP stdio（单机单客户端）

博文命令（F-022），与官方 installation.md 逐字一致（F-046）：

```bash
docker run -i --rm -v wigolo-data:/data ghcr.io/knockoutez/wigolo
```

接进 Claude Code 的示例（官方）：

```bash
claude mcp add wigolo -- docker run -i --rm -v wigolo-data:/data ghcr.io/knockoutez/wigolo
```

镜像是 **slim 变体**：浏览器引擎与端侧模型首次使用时下载进 `/data` 命名卷并持久化（缓存、模型、引擎、加密密钥都在卷里，重启不丢）（F-046，博文"slim 镜像懒加载模型"准确）。

### 模式 B：HTTP 服务（多客户端/内网/VPS）

博文给出的形式（F-022）：

```bash
docker run -p 3333:3333 -v wigolo-data:/data \
  -e WIGOLO_API_TOKEN=请替换为长随机字符串 \
  ghcr.io/knockoutez/wigolo serve --host 0.0.0.0
```

官方推荐的等价路径是 compose 文件 `packaging/compose.serve.yml`（F-048）：

```bash
docker compose -f packaging/compose.serve.yml up
```

**安全机制 fail-closed**（F-048，"配个 token 才能安全访问"的强制逻辑）：

- 容器内绑定 `0.0.0.0` 属非回环绑定；
- 未设置 `WIGOLO_API_TOKEN`、也没有显式 `--allow-unauthenticated` 时，守护进程**拒绝启动**——默认失败关闭。

### 关于 `:full`（勘误）

博文称"`:full` 标签预装浏览器引擎、启动更快"（F-023）。官方文档的准确表述（F-047）：

- `full` 是仓库 Dockerfile 的**构建目标**，适合 `--rm`/无卷场景（避免每次重新首次下载）：

```bash
docker build --target full -t wigolo:full .
```

- 官方安装文档**未确认 ghcr 已发布 `:full` 预构建标签**。拉取 `ghcr.io/knockoutez/wigolo:full` 是否可用请以仓库 Packages 页为准；稳妥做法是按上面的命令自行构建。

## 3. 配置 LLM，开启 research/agent 完整成稿

核心 6 工具（search/fetch/crawl/extract/cache/find-similar）完全免 Key（F-040）。要让 `research`、`agent` 与 `search format=answer` 直接产出完整研究报告，配置一个 LLM——博文推荐免费 Gemini（F-024，与官方逐字一致，F-050）：

```bash
export WIGOLO_LLM_PROVIDER=gemini
export GEMINI_API_KEY=你的key    # https://aistudio.google.com/apikey 免费申请，免费额度够用
```

其他选择（博文 F-025，官方 F-050）：

```bash
# 云端 provider（费用发生在 LLM 侧）
export WIGOLO_LLM_PROVIDER=anthropic   # 或 openai / groq

# 或保持全本地、全免费
export WIGOLO_LLM_PROVIDER=ollama      # 任意 OpenAI 兼容端点亦可
```

补充两个官方细节（F-050）：

- 也可用统一变量 `WIGOLO_LLM_API_KEY` 注入密钥；密钥**只从环境变量读取**，不接受命令行 flag（避免进入 shell 历史）；
- 环境变量写入 shell profile 或 Agent MCP 配置的 `env` 块均可。

配置后 research 的行为（博文 F-026，官方 F-041）：自动分解问题 → 并行搜索子查询 → 抓取来源 → 合成**带引用**的报告。REST 下直接调用：

```bash
curl -sX POST http://127.0.0.1:3333/v1/research \
  -H 'Content-Type: application/json' \
  -d '{"question":"对比 2026 年主流本地 MCP 搜索方案","depth":"comprehensive","max_sources":8}'
```

不配置 LLM 也能用：research/agent 会返回 raw brief 与 evidence，交给你的宿主 Agent（Claude/Cursor 自身模型）写结论（F-040）。

## 4. 自托管检查清单

- [ ] 服务仅监听回环（默认）或已设置强随机 `WIGOLO_API_TOKEN`
- [ ] 使用命名卷 `wigolo-data` 持久化 `/data`，避免重复下载 1.5GB 引擎与模型
- [ ] 公网/VPS 前置不要裸露端口——官方默认 fail-closed，但仍建议放反向代理后
- [ ] 需研究成稿时再配 LLM；敏感内网场景优先 Ollama/OpenAI 兼容本地端点，数据不出内网
- [ ] 部署后用 `/health` 与 `wigolo verify` 做存活与端到端验证（F-054）

## 延伸阅读

- [概念 02：四种部署形态架构图](../concepts/02-local-first-architecture.md)
- [示例 00：安装与 Agent 接入](00-install-and-agent-wiring.md)

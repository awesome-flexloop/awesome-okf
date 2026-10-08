# 实战 03 · REST、SDK 与自动化集成

> 事实锚点：F-005、F-028、F-041、F-042
> 命令来源：官方 README、llms.txt、docs/getting-started.md（2026-09-02 核验）

不玩 MCP 也能用 wigolo：同一套十工具通过 REST API、TypeScript/Python SDK 暴露，n8n、定时脚本、自研服务都能接（F-005）。

## 起本地 REST 服务

```bash
npx wigolo serve
```

- 默认监听 `127.0.0.1:3333`（仅本机）
- 工具端点：`POST /v1/{tool}`，如 `/v1/search`、`/v1/fetch`
- 接口契约：`GET /openapi.json`（OpenAPI 3.1，可直接生成客户端）
- 远程 MCP：`/mcp` + `/sse` 端点

curl 调用（博文作者在 n8n 里就是这么 curl 的，F-028）：

```bash
curl -s http://127.0.0.1:3333/v1/search `
  -H "Content-Type: application/json" `
  -d '{"query": "local-first web search", "max_results": 5}'
```

抓页面：

```bash
curl -s http://127.0.0.1:3333/v1/fetch `
  -H "Content-Type: application/json" `
  -d '{"url": "https://example.com", "max_content_chars": 4000}'
```

### 暴露给局域网/远程（fail-closed 安全设计）

daemon 默认**拒绝**绑定非 loopback 地址（F-041）。要提供远程访问，必须显式设置访问令牌：

```bash
$env:WIGOLO_API_TOKEN = "生成一个强随机令牌"
npx wigolo serve --host 0.0.0.0 --port 3333
# 之后请求带 Header：Authorization: Bearer <token>
```

（或明确自担风险使用 `--allow-unauthenticated`。）端口占用时不自动换端口，报错会给出可用端口，如 `--port 3334`。

## n8n / 自动化场景

在 n8n 中用 **HTTP Request 节点**（F-028）：

1. Method：POST；URL：`http://<host>:3333/v1/search`
2. Body：JSON，如 `{"query": "{{ $json.topic }}"}`
3. 远程部署时加 Header `Authorization: Bearer <WIGOLO_API_TOKEN>`

典型流水线：定时触发 → wigolo search/fetch 取资料 → watch webhook 回调触发后续节点 → 写飞书/Notion/邮件。

## TypeScript SDK（零依赖）

```bash
npm install wigolo-sdk
```

SDK 自带 embedded local 模式：自动发现正在运行的 daemon，没有就拉起一个，**无需单独 serve**（F-042）：

```ts
import { createLocalClient } from 'wigolo-sdk/local';

const { client, close } = await createLocalClient();   // 复用 daemon 或自行拉起
const res = await client.search({ query: 'local-first web search', max_results: 5 });
console.log(res.results.map((r) => r.title));
await close();   // 仅当本次调用拉起了 daemon 时才停止它
```

适用于 Node / Bun / Deno / edge 环境。

## Python SDK（纯标准库，sync + async）

```bash
pip install wigolo
```

```python
from wigolo import local_client

with local_client() as client:   # 复用健康 daemon 或自行拉起
    res = client.search(query="local-first web search", max_results=5)
    for r in res["results"]:
        print(r["title"], r["url"])
```

## 框架集成包（官方维护）

| 包名 | 生态 |
|------|------|
| `wigolo-langchain`（PyPI） | LangChain |
| `wigolo-crewai`（PyPI） | CrewAI |
| `wigolo-llamaindex`（PyPI） | LlamaIndex |
| `wigolo-vercel-ai-sdk`（npm） | Vercel AI SDK |

装上后直接把 wigolo 的十工具挂进对应框架，获得框架自带 web-tool 通常没有的 cache / find_similar / research / agent 能力。

## Docker 自托管

官方镜像（F-042）：

```bash
docker run -p 3333:3333 `
  -e WIGOLO_API_TOKEN=<强随机令牌> `
  -v wigolo-data:/root/.wigolo `
  ghcr.io/knockoutez/wigolo serve --host 0.0.0.0
```

> 注意 datacenter IP 的挑战墙通过率低于住宅网络（见[概念 01](../concepts/01-evidence-contract.md) 机制三）；VPS 部署时搜索/普通抓取正常，强反爬站可能返回 `blocked_by_challenge`，可配信誉匹配的代理（`USE_PROXY`/`PROXY_URL`）。

---

实战层结束。回到 [bundle 首页](../index.md) 或查阅 [references 信源层](../references/index.md)。

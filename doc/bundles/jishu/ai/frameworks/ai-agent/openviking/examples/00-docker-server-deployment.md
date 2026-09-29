---
okf_version: "0.2"
type: Example
title: "实战：Linux 服务器 Docker 部署 OpenViking"
description: "按博文实测路径在 Linux 服务器用 Docker 跑起 OpenViking：ov.conf 四块配置（阿里云百炼模型）、镜像/挂载/密钥、健康探针、Web Studio 双密钥配置"
tags: [OpenViking, Docker, 部署, ov.conf, 阿里云百炼, Web Studio]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g
  - id: docs-deploy
    url: https://docs.openviking.ai/en/guides/03-deployment
  - id: docs-config
    url: https://docs.openviking.ai/en/guides/01-configuration
  - id: aliyun-vl
    url: https://help.aliyun.com/zh/model-studio/qwen3-vl-plus
---

# 实战：Linux 服务器 Docker 部署 OpenViking

> 本演练复现博文部署链路（F-011~F-024），并在每个关键步骤标注官方文档口径（核验于 2026-09-16，服务端 0.3.22 时代）。

## 前置条件

- 一台 Linux 服务器（博文示例 IP：`192.168.3.101`，F-011），已装 Docker
- 一个阿里云百炼 API Key（博文 embedding 与 VLM 共用同一个 Key，F-016）；也可换火山/OpenAI/Kimi/GLM/Ollama 等 provider
- 能放行服务器的 1933 端口（仅内网使用时不要暴露公网；官方要求绑 0.0.0.0 时必须设置 root_api_key，F-035）

## 步骤 1：创建 ov.conf

在宿主机建目录并创建配置文件，博文路径为 `/mydata/openviking/ov.conf`（F-012/F-013）：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 1933,
    "root_api_key": "abc123456efg",
    "public_base_url": "http://192.168.3.101:1933"
  },
  "storage": {
    "workspace": "./data",
    "agfs": { "backend": "local" },
    "vectordb": { "backend": "local" }
  },
  "embedding": {
    "dense": {
      "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key": "<你的阿里云百炼 API Key>",
      "provider": "openai",
      "dimension": 1024,
      "model": "text-embedding-v4"
    }
  },
  "vlm": {
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "<你的阿里云百炼 API Key>",
    "provider": "openai",
    "model": "qwen3-vl-plus"
  }
}
```

四块配置职责（F-017）：

| 块 | 职责 | 关键字段 |
|----|------|---------|
| server | 监听地址、端口、管理密钥 | `root_api_key`（Docker 下**必填**，缺失则拒绝启动）；`public_base_url` 让服务端上传文件后回一个客户端可达地址 |
| storage | 记忆与向量数据落盘位置 | workspace ./data；agfs/vectordb 均用 local 后端（单机嵌入式存储） |
| embedding | 文本转向量 | text-embedding-v4，1024 维 |
| vlm | 生成摘要、理解内容，兼作 VikingBot 思考模型 | qwen3-vl-plus（视觉模型，也可处理多模态资源） |

**官方口径补充**（F-042）：

- 博文用的 `provider: "openai"` + 百炼 `/compatible-mode/v1` 是官方支持的 OpenAI 兼容接法；原生写法可直接 `provider: "dashscope"`（api_base 用默认值）
- text-embedding-v4：1024 维、中文优化（F-015/F-046）
- qwen3-vl-plus：百炼在售 Qwen3 视觉模型，文/图/视频输入、256K 上下文，现版本等同快照 qwen3-vl-plus-2025-12-19；华北2原价 ≤32k 档输入 ¥1/输出 ¥10 每百万 token（2026-09 时点，F-046）
- 除百炼外，官方配置向导 `openviking-server init` 支持 Volcengine、OpenAI、Codex OAuth、Kimi、GLM、本地 Ollama 等（F-034）

> ⚠️ 示例密钥 `abc123456efg` 仅为博文演示值，生产环境务必换成强随机密钥。

## 步骤 2：拉取并运行镜像

```bash
docker pull ghcr.io/volcengine/openviking:latest
```

（F-018，镜像发布于 GitHub Container Registry）

```bash
docker run --name openviking \
  -p 1933:1933 \
  -v /mydata/openviking:/app/.openviking \
  -d ghcr.io/volcengine/openviking:latest
```

（F-019）

官方文档口径（F-035）：

- 容器内全部持久态（ov.conf、ovcli.conf、workspace 数据）都在 `/app/.openviking`，**单挂载**即可，与博文挂载方式一致（官方示例挂载 `~/.openviking`）
- 镜像默认启动两个东西：1933 端口的 HTTP 服务（同时承载 `/studio` Web 控制台）与 vikingbot 网关
- 官方命令还建议加 `--restart unless-stopped`；不需要 VikingBot 时可在镜像名后加 `--without-bot` 或设 `-e OPENVIKING_WITH_BOT=0`
- 若平台不支持 `-v` 挂载，可用 `-e OPENVIKING_CONF_CONTENT="$(cat ov.conf)"` 传配置，或 `docker exec -it openviking openviking-server init` 交互式初始化

## 步骤 3：验证服务

```bash
curl http://192.168.3.101:1933/health
```

- 博文实测返回 `status: ok`、`healthy: true`，并带出服务版本与 auth_mode（F-020）
- ⚠️ **官方口径**：现行文档中 `GET /health` 无鉴权、示例仅返回 `{"status":"ok"}`，用作 liveness 探针；组件级就绪状态在另一个探针（F-036）：

```bash
curl http://192.168.3.101:1933/ready
# {"status":"ready","checks":{"agfs":"ok","vectordb":"ok","api_key_manager":"ok","embedding":"ok","ollama":"ok"}}
```

`/ready` 的检查项为 AGFS/VectorDB/APIKeyManager/Embedding/Ollama，**不含独立 VLM 项**；VLM 连通性需实际提交一次摘要/抽取任务验证。排查模型配置时，`/ready` 比 `/health` 更有用。

## 步骤 4：Web Studio 连接与用户配置

打开 `http://192.168.3.101:1933/studio`（F-021）：

1. **首页仪表盘**：展示上下文数据量、Token 用量、检索次数；左侧导航分工作区、活动、设置、资源四个区
2. **连接设置 → Root 或管理员 API 密钥**：填入 ov.conf 的 `root_api_key`（博文值 `abc123456efg`）。填对后"控制台权限"显示正常（F-022）
3. 此时页面提示"还缺少用户 API 密钥"——**管理密钥只管管理操作**，工作台与数据接口需要绑定用户身份的用户密钥（F-022）
4. **用户管理 → 新增用户**：用户名 `macro`、角色 `user`，创建后生成一把用户 API 密钥，**立即保存**（F-023）
5. 回到连接设置，把用户密钥填入"用户 API 密钥"栏，数据访问即打通（F-023）

> 双密钥模型对应服务端的多租户账号隔离能力；生产暴露前还应配置认证与可选资源 ACL（F-043）。

## 步骤 5：认识工作台三栏

| 栏 | 内容 |
|----|------|
| 左：上下文树 | `user` 下放个性化记忆，`resources` 放 Agent 可引用的外部资源（F-024） |
| 中：目录浏览 | viking:// 目录内容（对应概念篇的 L0/L1/L2 文件） |
| 右：会话区 | "终端"与"Agent"两种模式切换 |

Agent 的工具调用会与左侧目录联动——它操作了哪个 viking:// 文件，点击即可在左侧定位、中间打开（F-024）。

## 常见问题速查

| 现象 | 排查方向 |
|------|---------|
| 容器启动即退出 | 最常见原因是 ov.conf 未放对位置或缺少 root_api_key；看 `docker logs openviking`，entrypoint 在缺配置时会打印提示并等待文件出现（F-035） |
| /health 通但记忆不工作 | 查 /ready 的 embedding 等检查项（探针不含独立 VLM 项）；百炼 Key、模型名、网络出域任一不通都会卡住摘要与抽取，VLM 可提交一次实际抽取任务验证 |
| Studio 上传文件后链接打不开 | 核对 server.public_base_url 是否为**客户端可达**地址（F-017） |
| 想改配置 | 改宿主机 `/mydata/openviking/ov.conf` 后重启容器；数据在挂载卷内不丢 |
| 不用 Docker | `pip install openviking`（Python 3.10+）→ `openviking-server init` → `openviking-server doctor` → `openviking-server`（F-034）；生产可用 systemd 或 Helm（F-048） |

## 下一步

- [实战 01：VikingBot 跨会话记忆实测](01-cross-session-memory-walkthrough.md)
- [实战 02：接入 Claude Code 等 Coding Agent](02-agent-integration-mcp-cli.md)

---
type: Example
title: "OpenSEO Docker 与 MCP 路径"
description: "先本地验证，再接入数据 API 和 MCP 客户端的非实测路径"
tags: [OpenSEO, Docker, MCP, SEO]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: official, resource: "https://github.com/every-app/open-seo" }
---

# OpenSEO Docker 与 MCP 路径

**非实测示例**：不要直接暴露默认无认证实例；先在本机或私有网络测试。

```bash
git clone https://github.com/every-app/open-seo.git
cd open-seo
cp .env.example .env
# 编辑 .env，填写 DATAFORSEO_API_KEY 等当前必需变量
docker compose up -d
docker compose logs -f
```

启动后再按当前官方文档配置 MCP 客户端。DataForSEO 请求费用、配额和数据覆盖必须单独记账；OpenSEO 软件开源不意味着 SEO 数据免费。[F-024][F-025]

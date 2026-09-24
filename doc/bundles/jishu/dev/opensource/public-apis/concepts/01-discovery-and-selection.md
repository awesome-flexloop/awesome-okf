---
type: Concept
title: "发现与筛选公共 API"
description: "用目录元数据缩小候选范围，再回到单个服务的官方文档完成选型"
tags: [public-apis, API 选型, Auth, HTTPS, CORS]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: verification, resource: "/references/verification.md" }
  - { id: repo, resource: "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" }
---

# 发现与筛选公共 API

## 推荐的两阶段流程

public-apis 最适合作为“候选生成器”，而不是最终选型器：

1. **按主题找候选**：从天气、金融、新闻、交通、书籍、测试数据等分类进入，先阅读 `Description`。
2. **按接入约束筛选**：查看 `Auth`、`HTTPS`、`CORS`，排除明显不满足运行环境的条目。[F-010～F-011](../references/article-source.md)
3. **回到官方文档**：确认真实 endpoint、请求参数、响应 schema、速率限制、版本、数据来源、免费额度和商用条款。
4. **做最小验证**：只在自己的开发或测试环境验证一个代表性请求，不把目录中的状态当作当前可用性证明。
5. **记录决策**：保存访问日期、服务版本、认证配置、错误处理和替代供应商。

## 为什么 `CORS=Yes` 仍不够

对浏览器练习而言，`HTTPS=Yes` 与 `CORS=Yes` 能减少混合内容和跨域限制带来的障碍；`Auth=No` 也能减少申请密钥的前置步骤。[F-011](../references/article-source.md)

但这三个字段没有覆盖：

- 数据是否适合你的地区、语言和业务口径；
- 是否有速率限制、配额、突发流量策略；
- 是否允许缓存、再分发或商业使用；
- 服务是否持续维护，错误响应是否稳定；
- 返回数据是否包含个人信息或受限制内容。

因此，它们是筛选器，不是质量认证。文章也明确提醒读者逐项查看服务自己的官方页面。[F-020](../references/article-source.md)

## 适用场景

| 场景 | public-apis 的价值 | 交付前还要补什么 |
|---|---|---|
| Demo 和原型 | 快速找到可用数据源候选 | 替代接口、错误提示、最小缓存 |
| 接口练习 | 练习请求、JSON 解析和失败处理 | 选择文档清楚且无敏感数据的接口 |
| 内部小工具 | 快速发现天气、汇率、新闻等来源 | 负责人、预算、合规和可用性检查 |
| 正式产品 | 提供备选供应商线索 | SLA、合同、隐私评估、监控和灾备 |

这一区分是对文章“能少花时间找接口”观点的工程化重述，不是目录对任何具体服务的背书。

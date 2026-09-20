---
type: Concept
title: "开源 AI 知识库的选型维度"
description: "把作者关于门槛上升的判断改写为可迁移的知识库评估框架"
tags: [WeKnora, 选型, RAG, 开源软件评估]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-20T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: official-readme
    resource: https://github.com/Tencent/WeKnora/blob/main/README.md
  - id: official-api
    resource: https://github.com/Tencent/WeKnora/blob/main/docs/api/README.md
---

# 开源 AI 知识库的选型维度

文章结论“赛道没死，但门槛确实被抬高了”（F-014）是作者观点。将它转成可复用方法时，不应比较口号，而应检查以下维度。

## 五维评估表

| 维度 | 关键问题 | WeKnora 文章/官方资料证据 |
|---|---|---|
| 输入 | 能否接入实际文件与外部知识源？ | F-006、F-007、F-017 |
| 检索 | 是否支持向量、全文、混合检索和重排？ | F-003；具体实现仍需查版本文档 |
| 推理 | 是否只有问答，还是支持 Agent 工具调用？ | F-003、F-016 |
| 治理 | 是否能编辑 Chunk、维护版本、回滚 Wiki？ | F-010、F-016 |
| 扩展 | 是否提供稳定 API、模型和存储替换点？ | F-004、F-018；具体兼容矩阵需另行验证 |

## 不应直接推出的结论

- “能力清单完整”不等于所有连接器在每种部署中都生产可用。
- “支持 RAG”不等于检索质量已经优于其他项目。
- “腾讯开源”不等于部署、运维和安全成本为零。
- 作者的赛道判断不能替代带数据、版本和场景约束的对比测试。

## 可迁移检查单

评估任何开源知识库时，先用一组真实文档验证输入覆盖，再用可重复问题集验证检索与回答，最后检查知识维护、权限、审计和 API。这样才能把“产品能力很全”的印象转化为可审计的选型证据。


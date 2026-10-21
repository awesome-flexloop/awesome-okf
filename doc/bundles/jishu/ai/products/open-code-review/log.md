# 更新日志

## 2026-10-21

**Official Docs Layer**: 经 `open-codereview.ai` 官方文档站全站核验，新增「官方文档层」6 页并对既有页面建立口径勘误表（七概念方法论编排：R→I→E→V→C）

- **新增页面 6 个**：`concepts/12-official-runtime-model.md`（官方运行时模型）、`concepts/13-integration-contracts.md`（集成契约）、`concepts/14-verification-playbook.md`（可迁移模式与验证手册）、`references/official-doc-facts.md`（F-001~F-100 编号事实）、`references/official-doc-corrections.md`（E-01~E-11 勘误 + OK-01~OK-03 核对通过）、`references/adversarial-review.md`（四视角 V 记录）
- **既有页面 0 改写**：12 概念 + 5 参考页保持原貌，冲突数值统一由勘误表裁决（引用时以「官方口径」列为准）
- **勘误 11 条**：provider 数 19→**25**（E-01）、`azure-openai` 为虚构内置项（E-02）、协议 3→**4** 种（E-03）、review `max_tokens` 58888→**200000**（E-04）、`--max-tools` 模板默认 30→**100**（E-05）、`--timeout` 10→**15** 分钟（E-06）、`OCR_LLM_MAX_TOKENS` 提示词/输出语义颠倒（E-07）、plan 双阈值（E-08）、官方站点 `/docs/integrations/*` 断链（E-09）、首页动效占位值（E-10）、「六阶段」术语口径差异（E-11）
- **索引对账**：`doc/bundles/jishu/ai/products/index.md` 表头为「知识包 | 束数 | 一句话简介」，每行束数取值为 1，分类首行「本类共 33 个知识包」；本次为**既有 bundle 内部增补**，分类束数 33 与总索引计数**均不变**，仅刷新 open-code-review 行的简介口径
- **质量门**：G1（事实无因果词，100 条）/ G2（4 条洞察四元组完整）/ G3（3 个模式含触发+步骤+反模式+检验标准+迁移）/ G4（行动项原子化）/ V 门（4 视角 6 条意见，3 实质采纳 + 2 条件采纳 + 1 核查后留痕）均通过
- **已知边界**：本次未实机运行 `ocr` 二进制，事实均来自官方文档站与官方仓库静态文本；文档站 15 个可达页面已覆盖，贡献指南类页面无独立导航入口

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/03-agent-platforms-tools 迁入 awesome-okf-xs

三源整合新建：03-code-devtools/open-code-review-wiki（19 章）、根级 open-code-review-wiki（14 章结构化）、分类根散文件（微信文章教程）。去重后保留 12 概念 + 5 参考；各源 log/README/index 属元数据不迁入。

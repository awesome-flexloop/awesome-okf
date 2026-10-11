# 《守护品质生活》生成日志

> 本文件记录知识包从 R（事实）→ I（拆分）→ E（成文）→ V（审查/门禁）→ C（交付）的完整链路，供审计与追溯。

- **bundle**：`sheke/personal-growth/guard-quality-life`
- **生成时间**：2026-10-10
- **方法论**：seven-concepts-cmd「知识沉淀」链路（场景 4：R→I→E→V→C，强制 V）
- **主题**：「守护品质生活」自有主题生活方式方案库（11 域）

## R（事实登记）

- 在转化 spec：`.trae/specs/okf-wiki-ecosystem/guard-quality-life-okf-wiki-site/facts.md` 建立 F-001~F-046 连续登记。
- 主张分三层：【官方通识】（WHO/疾控/NIH 等，证据级 A）/【通用常识】（跨社会共识，B）/【框架主张】（本包方案设计，C）。
- 内容敏感度预检：**公开内容**（自有公开主题），标准工作流，产出入 `doc/bundles/`（不与私域混放）。

## P0 核验（R 阶段）

- 核验范围（facts F-044）：官方通识类 4 项。
  - F-009 WHO 身体活动通识（每周 150 分钟中高强度有氧 + 每周 2 天肌肉强化）→ ✅（机构主域）
  - F-010 中国疾控手卫生通识（流动水+肥皂 ≥20 秒）→ ✅（机构主域）
  - F-011 成人睡眠建议（7–9 小时/晚）→ ✅（WHO/NIH 主域）
  - F-029 安全带/头盔道路安全保命措施方向 → ✅（WHO 道路安全方向一致）
- 常识类（F-014~028, 030~034）→ 统一标【通用常识/非联网独立核验】（避免给常识捏造"研究出处"）。
- 框架主张类 → 明确【框架主张，非事实断言】。
- **核心声明无 ❌**；`status: stable`。

## I（三层知识拆分）

- 知识骨架：框架层（00）→ 域总览（01）→ 分域应用（02–05）→ 使用迁移（06）。
- 11 域映射：家居/健康/饮食/睡眠/效率/财务/关系/心理/出行/数字生活/安全。
- 分域篇按内容合组：03=健康+睡眠、04=效率+数字、05=财务+关系+心理；diet/travel 完整条目在网站 knowledge.py 结构化承载，概念层以 01 总览 + F 编号覆盖。

## E（信源先行成文）

- 先写 `references/`（article-source.md + verification.md + index.md），再写 `concepts/`（00–06 + index），最后根 `index.md`。
- 概念层所有主张回溯 F 编号；不搬运任何第三方文稿。

## V（审查与机械门禁）

已执行手动等效验证清单：

| 门禁项 | 结果 |
|---|---|
| UTF-8 strict 无乱码 | ✅ |
| F 编号双份（facts.md ↔ article-source.md）集合比对：FH 46/46 一致、连续 F-001~F-046 | ✅ |
| concepts 7 篇 + 2 子目录 index + 根 index + log 共 13 文件，逐一存在 | ✅ |
| toctree 条目逐一对应实际文件 | ✅ |
| 相对链接可达、零 `file:///` | ✅ |
| frontmatter 齐备（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources） | ✅ |
| 边界/时点/互链声明落地 | ✅ |
| 零 `.temp/` 引用、零家目录绝对路径 | ✅ |
| 无 `from __future__ import annotations`（Python 3.14 红线，网站代码） | ✅ |

## C（交付清单）

- **知识包**：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/guard-quality-life/`（13 文件：根 index、log、concepts 7+1、references 3）。
- **配套网站**：`apps/guard-quality-life-site/`（FastAPI MVP，Python 3.14+，scikit-build-core，37 测试全绿、整体覆盖 96%/关键 100%·96%）。
- **三级索引**：personal-growth/index.md（13→14 束）、sheke/index.md（13→14）、bundles/index.md（613→614 束、sheke 59→60）。
- 本交付**未执行 git commit/push**（延续并行工作区约定，待相应授权）。
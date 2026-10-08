# 生成日志：ai-app-survival

## 元信息

| 项 | 值 |
|----|----|
| 主信源 | 晚点 LatePost《有用户，有收入，AI 应用却不是好生意》 |
| URL | https://mp.weixin.qq.com/s/EANN8gVcsrRm4opUU3X58Q |
| 文章作者 | 祝颖丽（文）/ 赵磊（编辑） |
| 文章日期 | 2026-08-31 |
| 生成日期 | 2026-09-02 |
| 归属分组 | jishu/ai/ai-agent（产品资讯/商业分析类） |
| 内容敏感度 | 公开内容（公开发布的媒体文章） |
| 方法论 | blog-article-to-okf-wiki 七阶段 + 七概念 R→I→E→V→C 链路 |

## 链路记录

| 阶段 | 产出 | 状态 |
|------|------|------|
| 预检 | 内容敏感度：公开；URL 无访问控制参数 | ✅ |
| 骨架判定 | 商业分析/战略资讯类，无 examples/；index + concepts/(6) + references/(3) + log + assets | ✅ |
| 归属决策 | jishu/ai/ai-agent/，bundle 名 ai-app-survival；参照先例 doubao-work-org-productivity | ✅ |
| R 事实采集 | F-001~F-080 共 80 条事实登记（44 客观/采访、22 观点📝、2 自宣、9 核验✅、3 存疑⚠️） | ✅ |
| R 权威核验 | 12 项 P0 声明：9✅ 3⚠️ 0❌；勘误四张清单（N1 硬错误 1 / N2 口径 2 / N3 存疑 2 / N4 时效 2） | ✅ |
| I 知识拆分 | 6 概念；Mermaid 图 11 张（三难全景图/SaaS对比图/单位经济决策流/吞噬时间线/窗口计算框架/平台下场逻辑链/入口-插件格局图/发心分叉/0-1检查法/路线对比图/逃生决策树） | ✅ |
| I 配图 | Seedream 生成封面 assets/cover.jpg（编辑插画，无文字） | ✅ |
| E bundle 生成 | 信源先行：references(3) → concepts(7) → index → log | ✅ |
| V 对抗审查 | 四视角审查 + 双份 F 编号核对（见下） | ✅ |
| V 索引接入 | 组 index 新增条目；bundles/index 计数同步 | 待部署后执行 |
| C 原子提交 | 子模块提交 → 主仓库 spec/指针提交（不 push） | 待执行 |

## 文件清单（13 文件 + 1 图）

```
ai-app-survival/
├── index.md                         主入口（frontmatter + 核心论点 + 实操路径）
├── log.md                           本文件
├── assets/cover.jpg                 Seedream 封面配图
├── concepts/
│   ├── index.md                     概念索引
│   ├── 00-triple-squeeze.md         三难困境（Mermaid 全景图）
│   ├── 01-token-economics.md        卖 token 经济学（对比图 + 单位经济决策流 + checklist）
│   ├── 02-model-engulfment.md       模型吞噬（时间线 + 窗口计算框架 + checklist）
│   ├── 03-model-as-app.md           模型即应用（逻辑链 + 入口-插件格局图 + 要点）
│   ├── 04-avoidance-trap.md         躲避陷阱（发心分叉 + 0→1 检查法 + checklist）
│   └── 05-two-escape-routes.md      两条逃生路线（对比图 + 决策树 + 核查清单）
├── references/
│   ├── index.md                     信源距离分级 + 12 信源
│   ├── article-source.md            F-001~F-080 事实登记表
│   └── verification.md              P0 核验报告 + 勘误四张清单
```

## 质量门

- G1 信源门：每个客观事实标注信源距离（R1/R2+/📝/【自宣】/⚠️）；✅
- G2 核验门：12 项 P0 全部交叉验证，0 证伪；存疑项已标注并未作为结论支撑；✅
- G3 结构门：无 examples/ 的资讯类骨架；概念文档含事实对应与核验状态；✅
- G4 可操作门：4 个概念含 checklist/决策流/决策树，全文可实操点 ≥ 15；✅

## 双份 F 编号核对

- article-source.md 登记 F-001~F-080，连续无缺号；
- concepts/ 各文档"对应事实"区间：00→F002-008、01→F009-023、02→F024-037、03→F038-049、04→F050-058、05→F059-080，加 F-001 元信息，覆盖 80/80。
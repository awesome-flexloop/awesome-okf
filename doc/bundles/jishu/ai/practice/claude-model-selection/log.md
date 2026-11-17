# 变更日志

## 2026-11-10

- 依据 claude.dev 官方博文《Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku》（2026-11-09，Addy Osmani）生成知识包。
- 采用七概念 R→I→E→V→C 链路：R 采集 77 条事实 → I 拆三层知识 → E 信源先行生成 → V 四视角审查与机械门禁 → C 原子提交。
- 以 anthropic.com 四个模型页、Fable 5.2 发布文与 code.claude.com/model-config 文档核验阵容、价格、缓存价、fast mode、FrontierCode 2.0 结果与 Claude Code 默认 effort。
- platform.claude.com 在核验环境返回 “App unavailable in region”；API 侧 thinking、effort、advisor、preserved thinking、computer toolset 保留为博文单源并在 verification.md 明示。
- 按操作可复现性两问判定设置 `examples/`（子代理配置与自测流程均可照做），收录 2 篇实践。
- 勘误 E-1：博文 Sonnet 5.5 缓存读价 `$0.10` 与官方“最多 90% 节省”推算的 `$0.20` 冲突，正文同列并标注。
- 勘误 E-2：API 默认 effort 与 Claude Code 默认 effort 分栏呈现，避免混为一个口径。
- 勘误 E-3：博文“Opus 5.5 为各计划默认模型”仅部分核验；官方文档确认 Fable 不是任何计划的账户默认。
- 勘误 E-4：benchmark 与内部实验数字统一标注“厂商自述/未独立复算”。
- 事实登记双份比对：`F-001` 至 `F-077` 集合一致、连续无跳号。
- 索引接入：practice/index.md 增至 30 束 / 28 目录；jishu/ai/index.md 增至 292 束；jishu/index.md 与 bundles/index.md 计数同步。
- 机械门禁：check-utf8.py、check-toctrees.py、check-frontmatter.py 全部通过（结果见本次提交说明）。

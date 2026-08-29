# 变更日志

## 2026-08-29 — 初始生成（v1）

- 来源博文：《DeepSeek V4 Pro 也能看图了！》（macrozheng，2026-08-21）
- 按 blog-article-to-okf-bundle 模式 L2 生成（**技术教程完整骨架，含 examples/**，博客系列首个）
- R 阶段：35 条事实登记（F-001~F-035），6 项 P0 核验全部 ✅ 通过，3 项时效性补充
- I 阶段：3 concepts（视觉鸿沟 / 转录架构 / Skill机制）+ 2 examples（安装配置 / 三场景实战）
- E 阶段：生成 12 文件
  - index.md
  - concepts/index.md + 00-problem-vision-gap + 01-transcription-architecture + 02-skill-mechanism
  - examples/index.md + 00-install-and-config + 01-usage-scenarios
  - references/index.md + article-source + verification
  - log.md
- 索引更新：bundles 278→279；ai 域 105→106；ai-agent 组 26→27
- status: verified；stale_after: 2026-11-29

### 关键核验结论

- ✅ 仓库 asuojun/claude-vision-skill 真实存在，含 vision.js/SKILL.md/clipboard.ps1
- ✅ DeepSeek V4 Pro 无视觉 API（官方文档确认）
- ⏰ 博文发布当天 DeepSeek 上线 deepseek-v4-flash-vision-exp（官方视觉模型，实验性）
- ✅ qwen-vl-max / qwen3.5-omni-plus / compatible-mode 端点均核实
- ✅ Claude Code Skill 自动触发机制与官方标准一致
- ⚠️ 两个安装坑已标注：SKILL.md 硬编码他人路径（3处）、dotenv 静默失败

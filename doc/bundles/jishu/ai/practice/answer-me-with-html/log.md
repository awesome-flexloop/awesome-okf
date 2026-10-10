# 变更日志（Log）

## 2026-10-10 · 初始创建

- 经 wechat-public-okf + seven-concepts（场景 4 知识沉淀：R→I→E→V→C）转化公众号「开源星探」2026-10-06《1.4K Star！这个开源 Agent Skill 把一屏文字墙撕成了可视化页面！一看就懂！》；
- 一级信源：公众号博文；二级权威信源：GitHub 官方仓库 README（answer-me-with-html，采集于 2026-10-10）；
- 登记 F-001–F-021 共 21 条事实（references/article-source.md）；
- 完成 14 项 P0 核验：10 ✅ / 4 ⚠️ / 0 ❌，另登记核心勘误 E-1；
- **核心勘误 E-1**：博文「Always-on」用 `answer-me-with-html-always` 插件安装，官方 README 已声明该插件移除、改为规则文件开启（commit `5c53dcf`）；正文按规则文件为准呈现；
- 骨架判定：**可复现操作教程**（有明确安装命令 + CLI 用法 + 配置项，满足两问复现门）。审慎起见未设 examples/（拟以仓库 examples/ 目录为准，避免在 bundle 内复制不稳定的操作示例），采用 index + concepts 5 篇 + references 2 篇 + log 结构；
- 状态：`status: draft`，待独立审查后转 stable；
- 机械门禁说明：本次执行 V 阶段手动等效验证（UTF-8、F 编号一致性、toctree 完整性、相对链接、计数同步）；未运行 `invoke gates.*` 时不声称 gates 通过。
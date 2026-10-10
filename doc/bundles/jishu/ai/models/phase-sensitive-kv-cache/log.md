# 变更日志（log）

## 2026-10-10

- 创建 `phase-sensitive-kv-cache` bundle：将量子位文章《字节找到了DeepSeek时强时弱的原因》（作者闻乐，2026-10-09）经 OKF v0.2 七阶段工作流（blog-article-to-okf-wiki）转化。
- **骨架**：技术综述/实证研究，无 examples/。
- **归属**：`jishu/ai/models/`（基础模型能力分组，非 DeepSeek 生态——被测模型是 DeepSeek，但主题是分块 KV 压缩的通用检索缺陷，归入模型研究方向）。
- **事实采集**：48 条 F 编号（F-001~F-044 文章 + F-045~F-048 核验补充）。
- **P0 核验**：8 项关键成效数字（五组准确率差 + 两组概率）经论文 Figure 1/Figure 2 原图逐项核对通过，无源文硬错误；机理结论（相位专门化/门控/梯度流）标注论文自报口径，单源待独立复核。
- **状态**：stable。
- 文件清单：index.md、log.md、concepts/{index,00,01,02,03}.md、references/{index,article-source,verification}.md。
- V 阶段四视角审查：事实溯源/结构规范/读者可用性/时效边界 通过；双份 F 编号一致性核对通过（本 bundle 未建独立 `facts.md`——按 OKF v0.2 单 bundle 场景，事实登记集中在 references/article-source.md；已核对 F 编号连续无跳号）。
- 工作区复核：等待并行会话结束后开始写入；创建独立分支 `feat/phase-sensitive-kv-cache-bundle`，未触碰 stash 与并行 bundle 产物。
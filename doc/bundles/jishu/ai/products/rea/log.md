# REA 知识包更新日志

## 2026-10-12（第二轮：docs/ 全量深度重建）

- 将 `external/dao/rea/docs/`（固定 commit `eaf88aca`）视为完整信源做全量深挖，覆盖全部 49 个 `.md`（登记信源 `docs-full`）。
- 事实清单新增 F-067~F-131（共 65 条），按新增章节 H~N 组织：JavaScript 应用图与工作流、Web/浏览器域、Native 域、专项 Ghidra、IDA/JEB/Apktool Provider、平台分析域、工程与管理。
- 架构洞察追加洞察五（对分析工具做深：专项 Ghidra 逐格式/逐 ABI 适配矩阵）与洞察六（从一次性逆向工具到可审计重建工程工作流）；知识地图概念文档从 6 个规划扩至 10 个。
- 新增概念文档 4 篇（07-js-web-domains / 08-native-ghidra-specialty / 09-platform-domains-deep / 10-engineering-workflow）+ 实操示例 3 篇（js-reconstruction / platform-deep / reconstruction-workflow）。
- 同步更新 bundle 根 index、concepts/examples/references 子 index、source-manifest（`docs-full` 登记）。
- 事实数量疑义项（F-068 关系词汇 12、F-069 身份策略数量）已在 facts.md 标注"待 V 阶段 Grep 复核"。

## 2026-10-12

- 创建知识包：REA（Reverse Engineer Anything）经 OKF v0.2 source-code-to-okf-wiki 流程转化，基于本地源码 `external/dao/rea`（npm 包 `rea-agents` v6.4.0，MIT，固定 commit `eaf88aca`）+ 官方文档 `rea.tools`。
- 登记信源（references/source-manifest.md）与事实清单（references/facts.md，F-001~F-066）、架构洞察与知识地图（references/insights.md）。
- 生成概念文档 6 篇 + 实操示例 2 篇 + 目录索引（bundle 根 index + concepts/examples/references 三个子 index）+ 本更新日志。
- pending：需在 stale_after（2026-12-31）前复核动态数字（Star 等）快照、npm 版本演进、各分析工具链（Ghidra/IDA/Hopper/JADX 等）接入细节是否与上游 main 一致。
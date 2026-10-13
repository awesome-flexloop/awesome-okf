# REA 知识包更新日志

## 2026-10-12（第四轮：中文官网全站增量）

- 官网 17 页（W01~W17）与 sitemap/站内链接集合对账，新增 F-136~F-180 共 45 条事实；全部事实连续到 180。
- 新增概念 11~13、Notes 首次调查与官网教学实验，扩展五案例证据；总计 13 篇概念、8 篇示例。
- 新增官网逐页台账与验证记录，统一根索引和三个子索引的表格/toctree；子索引去除 frontmatter，sources 统一 resource。
- 修正默认 MCP profile、客户端 ID、Node/CI/引擎版本及命令参数；补齐 Evidence 输入、固件写入和主动运行时边界。固定 docs 计数为 48，旧第二轮“49 份且全部已读”声明不准确，本轮已收窄，不据计数推断阅读覆盖。
- 区分官网快照、6.4.0 固定源码及 4.1.0/6.1.0 历史案例；公开算法验证通过不代表原目标运行通过。未安装分析依赖、未运行原目标，未暂存或提交。

## 2026-10-12（第三轮：README_zh.md 增量扩展）

- 将 `external/dao/rea/README_zh.md`（官方 README 简体中文版，同 commit `eaf88aca`，287 行）纳入信源，登记 `readme-zh`（source-manifest 信源数六→七）。
- 事实清单新增 F-132~F-135（共 4 条，新增 O 章）：F-132 官方 showcase 三案例（DX-Ball 声像计算 / Notion Electron 剪贴板桥 / TH04 DOS 环形子弹）、F-133 能力总表前置依赖聚合、F-134 npm 更新机制、F-135 运行时安全口径。
- 新增实操示例 1 篇（examples/showcase-cases-example.md，三案例详解 + CLI 初探），examples/index 追加该行与 toctree。
- 同步更新 bundle 根 index（sources 新增 `readme-zh`、facts 计数 F-001~F-135、阅读路径补 showcase 示例、核心事实速查补 showcase/运行时口径两行）。
- 遵循 §6.5 多轮增量扩展：新增事实续编号，不重排/不重写前两轮已验证内容。

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

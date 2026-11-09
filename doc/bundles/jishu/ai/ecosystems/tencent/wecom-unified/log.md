# 更新日志

## 2026-11-09（G5 模式沉淀）

- **模式**：企业微信三层接入读法——执行层（wecom-cli）/ 路由层（本束 wecom-unified）/ 协议层（wecom-aibot-python-sdk）分束阅读，束间只做相对链接。
- **触发场景**：同一厂商同时提供 CLI、Skill 与 SDK 时，判断「装了什么」与「能力从哪来」的边界。
- **步骤**：①先确认 Skill 与 CLI 是两条独立交付链；②读前置检查三步门禁；③按意图路由到单一业务域 reference；④脚本只作为物料生成器，接口调用始终回到 CLI。
- **反模式**：①把安装 Skill 成功等同于业务可用；②凭意图描述拼参数而不读 reference；③在输出中外露 `userid`、`docid` 等内部标识；④把 6 个脚本当成独立产品能力。
- **迁移**：同样适用于其他「Skill 契约 + 外部 CLI 运行时」的分离式工具链。

## 2026-11-09（V 阶段独立复核）

- **审查维度**：A 断言真实性（具名实体逐项 Grep）、B F 编号范围与语义一致性、C 事实条数实测、D 结构合规、E Markdown 链接与 toctree 可达性、F 示例免责声明。
- **条数核验**：`references/facts.md` 实测 108 条（F-001–F-108，无跳号、无重复），与 index、references/index、log 所述一致。
- **发现与修复 0 处**：抽检 12 处 F 引用语义一致；实体抽检覆盖 9 个模板 slug、6 个脚本、`build_page.py` 的 `init/template/buildall/build/check/recolor/contrast/fit/imgfit/images` 子命令及 `--set`、`--map`、`--soffice`、`--grid`、`--dpi` 等参数，全部存在且语义相符；实测 133 篇 references、6 个脚本、53 个模板文件、197 个受控文件（198 条归档条目），与事实页一致。
- **结构/链接/免责声明**：12 篇非保留文档 frontmatter 齐全，`okf_version` 仅见于束根 index；相对链接与 toctree 全部可达；3 篇示例均含「未在本机实跑」，0 缺陷。
- **结论**：通过 V 复核；12 篇文档 `status` 由 draft 转 stable 并补写 `verified`。

## 2026-11-09

- **R（事实）**：完成 108 条事实登记（F-001～F-108），覆盖仓库结构、`SKILL.md` 前置检查与路由、references 分类学、scripts 工具链、模板系统、安装与耦合六节；每条附源文件行号与核对命令。
- **I（洞察）**：提炼 6 条四元组洞察（陈述 / 证据 / 反常识 / 行动），均以 F 编号为证据，并附概念文档知识地图。
- **E（表达）**：完成 6 篇概念文档与 3 篇实战示例，配套 concepts、examples、references 三个索引页与 bundle 根索引。
- **基线**：上游 `git@github.com:WecomTeam/wecom-unified.git`，commit `cae8a5befac67d96bfe573b1675c5faab474758e`；许可证 MIT；实质内容位于 `skills/wecom-unified/`。
- **声明**：3 篇示例均为基于源码阅读整理的用法演示，**未在本机实跑**，文中输出一律为示意，不构成运行结果承诺。
- **待办**：V 阶段独立复核后补写各文档 `verified` 字段，并将 `status` 由 `draft` 转 `stable`。
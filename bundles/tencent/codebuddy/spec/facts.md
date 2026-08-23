---
type: spec-facts
title: CodeBuddy 产品矩阵事实清单
---

# CodeBuddy 产品矩阵 Facts

> 本文件包含从 CodeBuddy 官方网站六个公开页面提取的 79 条编号事实。每条事实标注信源（IDE 官网 / IDE 文档 / CLI / NPC / WorkBuddy / Security），作为本知识束唯一事实来源，不做演绎。

## CodeBuddy IDE（产品官网）

- **F-001**: CodeBuddy IDE 定位为"全球首款 AI 驱动的集成产品、设计与开发全栈高级工程师"（信源：IDE 官网 https://www.codebuddy.cn/ide/）。
- **F-002**: IDE 官网标语为 "Where Design Meets Dev in Real-Time"（信源：IDE 官网）。
- **F-003**: IDE 支持自然语言驱动全流程开发，链路为"自然语言 → PRD → 设计原型 → 前后端代码 → 部署"（信源：IDE 官网）。
- **F-004**: IDE 集成腾讯云 CloudBase 与 Supabase 后端，支持一键部署（信源：IDE 官网）。
- **F-005**: IDE 支持 Figma 设计稿一键转代码（信源：IDE 官网）。
- **F-006**: IDE 预置组件库，并支持通过自然语言修改组件（信源：IDE 官网）。
- **F-007**: IDE 支持平台包括 macOS 11.0+（Apple/Intel 双架构）、Windows 10+ x64、Linux .deb（ARM64/x86_64）（信源：IDE 官网）。
- **F-008**: IDE 基于 VSCode 架构，支持插件市场与远程 SSH 开发（信源：IDE 官网）。

## IDE 文档介绍

- **F-009**: CodeBuddy 提供三种产品形态：IDE（产设研一体）、插件（即插即用）、CLI/Code（终端命令行）（信源：IDE 文档 https://www.codebuddy.cn/docs/ide/Introduction）。
- **F-010**: 产品阶段能力包括需求分析与 PRD 生成（信源：IDE 文档）。
- **F-011**: 设计阶段能力包括原型设计、草图转高保真、组件库（信源：IDE 文档）。
- **F-012**: 研发阶段能力包括 Figma 转码、智能补全、单测生成、代码审查（@workspace#Codebase）（信源：IDE 文档）。
- **F-013**: 部署阶段能力包括沙箱部署与公开链接发布（信源：IDE 文档）。
- **F-014**: 内置后端生态为 Supabase 与腾讯 CloudBase（BaaS）（信源：IDE 文档）。
- **F-015**: 内置部署生态为 CloudStudio 与 EdgeOne Pages（信源：IDE 文档）。
- **F-016**: 内置组件库生态为 TDesign、MUI、Shadcn（信源：IDE 文档）。
- **F-017**: 内置多模型支持混元与 DeepSeek（信源：IDE 文档）。
- **F-018**: 高级功能包括 Plan 模式、Subagents、Skills、Hooks、MCP、模型配置、检查点、记忆、规则、智能提交（信源：IDE 文档）。
- **F-019**: 插件兼容 VS Code 1.82+（信源：IDE 文档）。
- **F-020**: 插件兼容 IntelliJ IDEA/PyCharm 等 JetBrains IDE 2022.2+（信源：IDE 文档）。
- **F-021**: 插件兼容 Android Studio Flamingo（信源：IDE 文档）。
- **F-022**: 插件兼容微信开发者工具 1.06+（信源：IDE 文档）。
- **F-023**: 插件兼容 Xcode 14.0+（信源：IDE 文档）。
- **F-024**: 插件兼容 Visual Studio 2022（信源：IDE 文档）。
- **F-025**: CLI 通过 `npm install -g @tencent-ai/codebuddy-code` 安装，要求 Node.js 18.0+（信源：IDE 文档）。（注：CLI官网要求Node.js 22+，IDE文档标注18.0+，以CLI官网22+为准）

## CLI

- **F-026**: CodeBuddy CLI 定位为终端原生 AI 编程工具，具备全仓百万级代码感知能力（信源：CLI 官网 https://www.codebuddy.cn/cli/）。
- **F-027**: CLI 安装命令为 `npm install -g @tencent-ai/codebuddy-code`，要求 Node.js 22+ 与 Git（信源：CLI 官网）。
- **F-028**: CLI 支持终端深度编码（信源：CLI 官网）。
- **F-029**: CLI 提供高级代码智能，包括全代码库分析与语义搜索（信源：CLI 官网）。
- **F-030**: CLI 通过 `/init` 命令生成 CODEBUDDY.md 项目手册（信源：CLI 官网）。
- **F-031**: CLI 支持图片与截图输入，可通过 Ctrl+V 粘贴（信源：CLI 官网）。
- **F-032**: CLI 同时具备 MCP 客户端与服务器能力（信源：CLI 官网）。
- **F-033**: CLI 长期记忆基于 CodeBuddy.md 分层：项目级、用户级、企业级（信源：CLI 官网）。
- **F-034**: CLI 支持 Sub-agents，具备独立上下文、专属提示词与工具权限（信源：CLI 官网）。
- **F-035**: CLI 支持高度自定义，包括分层配置与 CLI 参数（信源：CLI 官网）。
- **F-036**: CLI 跨平台支持 macOS/Linux/Windows，覆盖 50+ 编程语言（信源：CLI 官网）。
- **F-037**: CLI 提供 `/doctor` 命令用于故障排查（信源：CLI 官网）。
- **F-038**: CLI 使用按 Token 消耗计费（信源：CLI 官网）。

## NPC

- **F-039**: NPC 定位为研发流程中的 AI 员工（Cloud Agent），基于 CodeBuddy 打造（信源：NPC 官网 https://www.codebuddy.cn/npc/）。
- **F-040**: NPC 与 CNB 平台（cnb.cool）深度融合（信源：NPC 官网）。
- **F-041**: NPC 理念为"给 NPC 定下目标，下班前验收 Ta 的产出"（信源：NPC 官网）。
- **F-042**: NPC 采用目标驱动模式，用户定义 What 而非 How（信源：NPC 官网）。
- **F-043**: NPC 可自主获取上下文，来源包括 CNB 仓库、ISSUE、流水线（信源：NPC 官网）。
- **F-044**: NPC 支持并行指派，多个 NPC 可在云端并行工作（信源：NPC 官网）。
- **F-045**: NPC 覆盖从需求到 PR 的全流程：规划 → 编码 → PR → 构建 → 预览环境 → 验收合入（信源：NPC 官网）。
- **F-046**: NPC 支持多 NPC 协同，NPC Team 按职能分工（信源：NPC 官网）。
- **F-047**: NPC 可自主修复构建报错：读取日志、查找代码、提交修复直至门禁通过（信源：NPC 官网）。
- **F-048**: NPC 可自动解决合并冲突（信源：NPC 官网）。
- **F-049**: NPC 支持定制，包括职能、SOP、Skill（信源：NPC 官网）。
- **F-050**: NPC 入口为 https://cnb.cool/npc/CodeBuddy（信源：NPC 官网）。
- **F-051**: NPC 定价按量收取 Agent 执行 Token 消耗（信源：NPC 官网）。

## WorkBuddy

- **F-052**: WorkBuddy 定位为在线 AI 助手 Web 应用（腾讯龙虾）（信源：WorkBuddy 官网 https://www.workbuddy.cn/app）。
- **F-053**: WorkBuddy 标语为 "WorkBuddy, 我帮你"（信源：WorkBuddy 官网）。
- **F-054**: WorkBuddy 日常办公场景覆盖幻灯片、视频、深度研究、文档、数据分析、可视化、金融、产品、设计、邮件（信源：WorkBuddy 官网）。
- **F-055**: WorkBuddy 代码开发场景覆盖日常开发、网站、Agent 应用、Skill 开发、CI/CD、文档（信源：WorkBuddy 官网）。
- **F-056**: WorkBuddy 采用对话式交互，支持 @ 引用对话文件、/ 调用技能与指令（信源：WorkBuddy 官网）。
- **F-057**: WorkBuddy 右侧面板提供概览、产物（Artifacts）与引用来源追踪（信源：WorkBuddy 官网）。
- **F-058**: WorkBuddy 支持代码仓库关联与全屏模式（信源：WorkBuddy 官网）。
- **F-059**: WorkBuddy 顶部导航包含 IDE、插件、CLI、文档、定价、博客、API 文档、活动（信源：WorkBuddy 官网）。
- **F-060**: WorkBuddy 当前处于公测阶段（信源：WorkBuddy 官网）。

## Security

- **F-061**: CodeBuddy Security 定位为新一代 AI 代码安全审计平台（信源：Security 官网 https://www.codebuddy.cn/security/）。
- **F-062**: Security 基于腾讯云代码分析 TCA-Xcheck 与 AI 安全 Agent 多引擎驱动（信源：Security 官网）。
- **F-063**: Security 标语为"让每一行代码都值得信赖"（信源：Security 官网）。
- **F-064**: 安全闭环第一步为威胁建模，识别攻击面（信源：Security 官网）。
- **F-065**: 安全闭环第二步为漏洞发现，采用 Xcheck 静态分析与 AI 深度审计多引擎并扫（信源：Security 官网）。
- **F-066**: 安全闭环第三步为对抗审查，先假设误报再证伪，多 Agent 独立论证以消除幻觉（信源：Security 官网）。
- **F-067**: 安全闭环第四步为动静验证，自动生成 PoC 在隔离沙箱中实际运行（信源：Security 官网）。
- **F-068**: 安全闭环第五步为自动修复，生成针对性补丁，建议人工复核（信源：Security 官网）。
- **F-069**: 安全闭环第六步为人工审核（信源：Security 官网）。
- **F-070**: Security 核心特性包括对抗性 AI 审查（信源：Security 官网）。
- **F-071**: Security 具备 AI 规则反哺闭环，验证后的漏洞沉淀为静态规则（信源：Security 官网）。
- **F-072**: Security 支持自动化 PoC 验证（信源：Security 官网）。
- **F-073**: Security 支持多引擎并扫（信源：Security 官网）。
- **F-074**: Security 具备智能成本优化，采用多档模型与缓存（信源：Security 官网）。
- **F-075**: Security 战绩为发现 18 个漏洞，其中 14 个为严重/高危（信源：Security 官网）。
- **F-076**: Security 获得 18 个 CVE 编号（信源：Security 官网）。
- **F-077**: Security 漏洞覆盖 12 个开源项目，包括 Suricata、Apache IoTDB、Model-Optimizer、mermaid、mapserver、FreeRDP、ImageMagick、Megatron-LM、LiteLLM、Langflow、Mastodon、React 等（信源：Security 官网）。
- **F-078**: 相比传统 SAST，Security 优势为高召回率、低误报率、可发现未知漏洞、低规则维护成本、PoC 动态验证、针对性修复补丁（信源：Security 官网）。
- **F-079**: Security 购买入口为 https://buy.cloud.tencent.com/cbsec（信源：Security 官网）。

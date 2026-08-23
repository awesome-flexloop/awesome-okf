---
type: Changelog
scope: opencode
version: "0.1.0"
---

# 变更日志

## 0.1.0 — 2026-08-23

### 新增

- 初始化 OKF v0.2 wiki bundle
- **spec/facts.md**：80 条源码事实，覆盖项目元数据、包结构、运行时、V2 会话核心、V2 工具系统、V2 配置、内置 Agent、部署基础设施、GitHub Action、包依赖架构
- **spec/insights.md**：4 条架构洞察
  - V2 会话"持久化录入与执行分离"架构
  - 多运行时条件导入与严格包依赖方向
  - V2 配置系统大规模重命名（单数→复数）与不兼容别名策略
  - 混合云部署（Cloudflare 面向用户 + AWS 数据湖）
- **concepts/00-introduction.md**：项目定位、技术栈、包结构、安装方式
- **concepts/01-architecture.md**：包依赖方向、infra 模块、Effect 模式、双运行时条件导入、V2 API 规范
- **concepts/02-config-system.md**：配置文件发现、.opencode 目录、11 个配置审查组、MCP 配置、Agent/权限配置
- **concepts/03-session-tools.md**：SessionV2 API、Context Epoch、自动压缩、工具定义/注册/执行/输出限制/失败语义、内置工具、权限系统
- **concepts/04-deployment-infra.md**：SST 配置、阶段环境、Cloudflare 部署、PlanetScale 数据库、Stripe 集成、AWS 数据湖、GitHub Action
- **examples/01-basic-usage.md**：7 个使用示例（安装、TUI 启动、Agent 切换、HTTP 服务器、GitHub Action、配置文件、CLI 命令）
- **references/source.md**：关键源文件索引与事实 ID 映射
- 子目录索引文件：concepts/index.md、examples/index.md、references/index.md、spec/index.md
- 根 index.md：bundle 入口，okf_version 0.2

### 数据源

- 源码路径：`d:\spaces\SpecWeave\external\libs\ai\agents\opencode\`
- 快照日期：2026-08-23
- 核心读取文件：package.json、README.md、AGENTS.md、CONTEXT.md、bunfig.toml、turbo.json、tsconfig.json、sst.config.ts、infra/*.ts、specs/v2/{config,session,tools}.md、specs/project.md、github/index.ts、github/action.yml、.opencode/{tui.json,env.d.ts,opencode.jsonc}、packages/{core,opencode,tui}/package.json、packages/opencode/src/index.ts

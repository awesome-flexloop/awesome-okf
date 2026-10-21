---
type: Changelog
scope: opencode
version: "0.3.0"
---

# 变更日志

## 2026-10-21

### 0.3.0：同快照源码深化

- **新增**：F-115～F-151共37条事实、五条洞察；概念10～15覆盖配置/上下文、codemode、插件、三端持久化、simulation/recorder与云端更新；示例03提供静态源码核验练习。
- **信源**：新增`references/source-deepening-2.0.32.md`，仍固定`6ec56821d63100fe5bda45b759364f561c56b359`。每主题列出代表实现、测试/调用方、正文/片段/未读范围；本机checkout不是活动引用。
- **导航**：内容定稿后追加根与四个子目录索引的人类导航及toctree；只更新本束，不修改共享父级或全局看板。
- **最小修订**：前轮`spec/insights-2.0.32.md`单次模型调用措辞`turn → step`，依据固定源码根AGENTS术语契约；其他旧结论、编号及6/4/29覆盖历史保留。
- **证据修订**：R草稿机械EOF检查修正八处过长行范围，补全skill-file路径；正式事实使用修正坐标，未改变机制结论。
- **内容回验修订**：Task8只读回验后，将F-115明确为返回字段值、F-117明确为URL失败跳过或保留旧副本，F-150区分machine参数与Windows平台差分下载设置；概念10/15同步，files路径明确缓存先返回。补齐合并事实的实际链接范围，F-146 live/redacted测试定位到253-277，旧285-309仅属204/二进制测试。
- **文档自验**：修订后py314 `invoke gates.all`退出0；一次中途失败仅为他方open-code-review六项在途导航，未代修，后续全量重跑通过。从本束内执行主仓链接工具，扫描34份Markdown、172个本地引用全部存在（不声称外网URL实时可达）。独立解析复计37唯一新增事实、10个新增文件，元数据、68唯一固定行段EOF、双导航、旧日志尾部与未修改历史、无暂存及源码clean检查通过。逐事实回验后限定修订回归全部PASS，无范围内残余。
- **构建**：本轮正式`invoke build`等待进程退出后确认exit=0；全站325条警告，本束路径诊断0。修订后的本束另用项目配置定向HTML构建exit=0，无文档诊断，只有jieba依赖弃用提示。独立Review结论由本轮规格审查记录单独承载，未以自验替代。
- **C候选评估**：字段值/对象、参数/平台行为、可点击范围/标签及零扫描假绿等教训已落入本轮勘误与验证纪律；均被既有源码知识化流程覆盖，未形成有独立迁移验证的新模式。故不新增主仓方法论、Prompt模板或Git提交。
- **限制**：未运行OpenCode源码测试、真实模型、云部署或更新；inference鉴权计费、Stats core、完整transport/Drive UI、全部客户端同步等仍未穷尽。不复用前轮成功记录，不宣称穷尽全部源码。

## 0.2.0 — 2026-10-20

### 新增

- 固定 OpenCode `2.0.32` 源码基线：`anomalyco/opencode@6ec56821d63100fe5bda45b759364f561c56b359`
- **spec/facts-2.0.32.md**：续接 F-081～F-114，共 34 条事实；加入 39 个 workspace manifest 覆盖矩阵，并明确深读、入口/接口读取与清单级边界
- **spec/insights-2.0.32.md**：新增 5 条架构洞察及 5 篇概念、1 篇示例的增量学习地图
- **references/source-code-map-2.0.32.md**：登记固定 commit、workspace 范围、覆盖等级与关键源码路径
- **concepts/05-monorepo-package-map.md**：workspace 包图与覆盖等级
- **concepts/06-session-execution-lifecycle.md**：prompt 接纳、唤醒、协调器、runner 与事件投影
- **concepts/07-model-tool-extensibility.md**：Agent/Provider、工具 runtime、MCP、Permission 与 Plugin host
- **concepts/08-protocol-server-client-sdk.md**：Protocol、Server、Client contract 生成与 SDK 导出边界
- **concepts/09-product-surfaces-and-delivery.md**：CLI/TUI/App/Desktop 入口及测试、构建、发布 workflow
- **examples/02-session-prompt-trace.md**：session prompt 固定源码追踪导读（非可运行示例）

### 导航与元数据

- 更新根 index 与 concepts/examples/references/spec 子目录索引的人类导航及 `{toctree}`
- bundle 版本由 `0.1.0` 更新为 `0.2.0`；根索引标注 1.18.21 历史快照与 2.0.32 固定快照的并存边界
- 父级 `ai-agent/index.md` 已包含 `opencode/index`，本轮未改动该父级索引

### 数据源

- 本轮教程及新增事实只依据固定 commit `6ec56821d63100fe5bda45b759364f561c56b359`
- 原有 `concepts/00`～`04`、`examples/01`、`spec/facts.md`、`spec/insights.md` 与 `references/source.md` 保留为 1.18.21 历史快照；本轮未重排旧编号或重写旧结论
- 索引、frontmatter、事实编号和内部链接的独立质量门将在后续验证阶段记录

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

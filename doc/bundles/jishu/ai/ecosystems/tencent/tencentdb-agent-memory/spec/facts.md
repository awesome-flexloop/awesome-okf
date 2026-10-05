---
type: spec-facts
title: TencentDB Agent Memory 事实清单
status: stable
generated: { by: reference_agent/trae-solo, at: 2026-10-04T00:00:00Z }
sources:
  - id: s-repo
    resource: https://github.com/TencentCloud/TencentDB-Agent-Memory
    title: TencentDB-Agent-Memory 仓库本体（学习截面：分支 feat/server_team，commit 8b86874a2daea49e3ff0fb53d699203146c5c77d，git describe = v2.0.2-beta.3-7-g8b86874，采集日 2026-10-04）
  - id: s-readme
    resource: README_CN.md
    title: 仓库根 README（中文）
  - id: s-changelog
    resource: CHANGELOG.md
    title: 变更日志（Keep a Changelog / SemVer）
  - id: s-roadmap
    resource: ROADMAP_CN.md
    title: 中文路线图
  - id: s-install
    resource: INSTALL_CN.md
    title: 中文安装指南
  - id: s-deploy-doc
    resource: README.deployment.md / README.docker.md
    title: 部署形态与 Docker 说明
  - id: s-core-pkg
    resource: MemoryCore/package.json
    title: MemoryCore 包清单
  - id: s-core-readme
    resource: MemoryCore/README_CN.md
    title: MemoryCore 中文 README
  - id: s-core-code
    resource: MemoryCore/src/**
    title: MemoryCore 源码（commit 8b86874）
  - id: s-core-api
    resource: MemoryCore/v3-api-memorycore-doc.md
    title: MemoryCore v3 API 文档
  - id: s-skill-md
    resource: MemoryCore/SKILL.md
    title: MemoryCore 随仓 Skill 说明
  - id: s-know-code
    resource: MemoryKnowledge/**
    title: MemoryKnowledge 源码与包清单（commit 8b86874）
  - id: s-know-doc
    resource: MemoryKnowledge/README.md、v3-api-memoryknowledge-doc.md、openapi.yaml
    title: MemoryKnowledge 文档与 OpenAPI
  - id: s-proxy-code
    resource: MemoryProxy/src/**
    title: MemoryProxy 源码（commit 8b86874）
  - id: s-proxy-doc
    resource: MemoryProxy/README_CN.md、v3-api-memoryproxy-doc.md、config.example.yaml
    title: MemoryProxy 文档与配置样例
  - id: s-panel-code
    resource: MemoryPanel/**
    title: MemoryPanel 源码、包清单与文档（commit 8b86874）
  - id: s-deploy
    resource: deploy/global-images/**
    title: 一键部署脚本与 .env.example
  - id: s-sdk-ts
    resource: sdk/memory-core/typescript/**
    title: 官方 TypeScript SDK
  - id: s-sdk-py
    resource: sdk/memory-core/python/**
    title: 官方 Python SDK
  - id: s-ci
    resource: .github/workflows/pr-ci.yml
    title: PR 持续集成工作流
---

# TencentDB Agent Memory Facts

> 本文件登记从仓库固定截面（commit 8b86874，2026-10-04 采集）提取的 300 条编号事实（F-001 ~ F-300）。代码事实均带文件路径（关键处带行号锚点），文档事实标注对应文件。所有事实为可核验的客观描述；信源间口径差异以「⚠️ 口径」条目并列登记，不做单边删改。

## 一、仓库、版本与分发

- **F-001**: 仓库远程地址为 `git@github.com:TencentCloud/TencentDB-Agent-Memory.git`；学习截面 HEAD 为 commit `8b86874a2daea49e3ff0fb53d699203146c5c77d`（提交时间 2026-09-29 16:48，"Merge PR #1552"），所在分支 `feat/server_team`，采集时工作树干净（信源：s-repo）。
- **F-002**: 该截面 `git describe` 输出 `v2.0.2-beta.3-7-g8b86874`，即位于 tag v2.0.2-beta.3 之后第 7 个提交（信源：s-repo）。
- **F-003**: 仓库以 MIT License 开源，根目录含 LICENSE、CONTRIBUTING_CN.md、INSTALL_CN.md、README_CN.md、CHANGELOG.md、ROADMAP_CN.md 等中文文档（信源：s-repo）。
- **F-004**: 仓库为 pnpm monorepo 形态，顶层组件目录为 MemoryCore、MemoryKnowledge、MemoryPanel、MemoryProxy、sdk、deploy（信源：s-repo 目录树）。
- **F-005**: CHANGELOG 覆盖模块声明为 `MemoryCore` / `MemoryPanel` / `MemoryKnowledge` / `MemoryProxy` / SDK 全部开源模块（CHANGELOG.md:7-8）。
- **F-006**: CHANGELOG 遵循 Keep a Changelog 格式与语义化版本，共登记 5 个版本：2.0.2-beta.1（2026-09-07）、2.0.1（2026-08-25）、2.0.1-beta.1（2026-08-13）、2.0.0（2026-08-03）、2.0.0-beta.1（2026-07-21）（CHANGELOG.md:12、68、147、194、287）。
- **F-007**: 首个公开版本为 2.0.0-beta.1（2026-07-21），SemVer 直接从 2.0.0-beta.1 起步（CHANGELOG.md:287-291）。
- **F-008**: 2.0.0-beta.1 条目说明 npm 包名迁移到 `-v2` 后缀：`@tencentdb-agent-memory/memory-tencentdb-v2`、`memory-sdk-ts-v2`；Docker 镜像 tag 独立于 npm 版本，该次镜像发布为 `:1.0.0-beta.1`（CHANGELOG.md:289-291）。
- **F-009**: 2.0.2-beta.1 新增 MongoDB 存储后端（试验特性、可选、默认关闭），默认存储仍为 sqlite；新增一键入口 `./start-all-mongo.sh`，未配置 `MONGODB_ENDPOINT` 时脚本拉起 `mongodb-atlas-local` 容器（CHANGELOG.md:14-20）。
- **F-010**: MongoDB 启用方式为在 .env 设置 `MEMORY_CORE_STORE_MODE=mongodb`，后续启动保持该后端、不静默回退 sqlite；切换后端不迁移已有数据（CHANGELOG.md:21-25）。
- **F-011**: 2.0.2-beta.1 面板登录侧兼容标准 OAuth2，可对接企业内部 OA/SSO，仓库提供对接骨架与 `authorize`/`token`/`userinfo` 端点配置项（CHANGELOG.md:40-46）。
- **F-012**: 2.0.2-beta.1 数据分析与可观测性默认关闭，开启需 Proxy/Knowledge/Core 三个服务分别配置 ClickHouse：Proxy 与 Knowledge 负责埋点上报、Core 负责查询接口，Panel 通过配置发现接口判断是否启用（CHANGELOG.md:48-57）。
- **F-013**: 2.0.1 新增 OpenCode、DeepSeek Harness（dsh）、Codex CLI、WorkBuddy 四款客户端接入（CHANGELOG.md:70-79）。
- **F-014**: 2.0.1 起支持会话内指令：会话中途一键重置绑定（换团队/Agent/任务）、对话内创建/更新任务（CHANGELOG.md:81-87）。
- **F-015**: 2.0.1 冷启动特性：创建团队或用户即自动生成默认 Agent；管理员可自定义默认 Agent 模板；支持从 IDE 已有 Agent 一键导入资产（CHANGELOG.md:89-94）。
- **F-016**: 2.0.1 面板新增对话记忆搜索：跨会话语义与关键字检索、按权限控制可见范围、支持对单层记忆直接覆盖修改（CHANGELOG.md:114-115）。
- **F-017**: 2.0.1 启动脚本支持交互式配置，自动预检 LLM 通路与端口占用；客户端接入地址一键复制，单机部署下自动解析宿主机地址（CHANGELOG.md:118-121）。
- **F-018**: ⚠️ 口径：CHANGELOG 的克隆命令写的是 `https://github.com/Tencent/TencentDB-Agent-Memory.git`（CHANGELOG.md:245、339），实际 remote 为 `TencentCloud/TencentDB-Agent-Memory`；两处组织名不同，学习截面以实际 remote 为准。

## 二、产品定位、四件架构与部署形态

- **F-019**: README_CN 标语为「让 Agent 沉淀经验，让人专注创造」；技术三问题表述为「什么值得留下、谁可以使用、下一次怎样少拿但拿对」（信源：s-readme）。
- **F-020**: README 声明运行环境 Node.js ≥ 22.16，npm 包名为 `@tencentdb-agent-memory/memory-tencentdb`（信源：s-readme）。
- **F-021**: ⚠️ 口径：README 宣传产品版本为 v2.0.0；MemoryCore/package.json 的实际包名为 `@tencentdb-agent-memory/memory-tencentdb-v2`、版本 `1.0.2-beta.1`；git 最新 tag 为 v2.0.2-beta.3——产品版本、npm 版本、git tag 三套口径并存（信源：s-readme、s-core-pkg、s-repo）。
- **F-022**: 系统由四个组件构成：MemoryCore（记忆核心，端口 8420）、MemoryKnowledge（知识引擎）、MemoryPanel/Hub（团队记忆操作台）、MemoryProxy（LLM 代理，端口 8096）（信源：s-readme）。
- **F-023**: MemoryKnowledge 的 config 默认端口为 8421（MemoryKnowledge/src/config.ts:147-180），docker 部署映射宿主端口 8424→容器 8421（deploy/global-images/.env.example:47-71；MemoryKnowledge/Dockerfile:77-89）。⚠️ 口径：README 中存在 8421/8424 两种端口说法，分别对应容器内监听与宿主映射。
- **F-024**: MemoryPanel 容器内监听 8125（start-memory-hub.sh:86-118），MemoryPanel/.env.example 默认端口写 8123。⚠️ 口径：8123 为本地裸跑默认值，8125 为容器内端口/部署映射口径。
- **F-025**: README 给出的 Benchmark 为 PersonaMem：不挂载记忆时 48%、启用记忆后 76%，相对提升 +59%（信源：s-readme）。
- **F-026**: Proxy 的接入方式被描述为「协议不变，把 Agent 的 base URL 指向 Proxy，不需要插件、Hook 或 MCP」（信源：s-readme）。
- **F-027**: README 列出 Proxy 支持 7 个客户端：DeepSeek Harness（dsh）、Claude Code、Codex、CodeBuddy、WorkBuddy、Hermes、OpenClaw（信源：s-readme）。
- **F-028**: INSTALL_CN 的 Proxy 客户端列表为 8 类：Claude Code、CodeBuddy、WorkBuddy、Codex、DeepSeek Harness、OpenCode、Hermes、OpenClaw（INSTALL_CN.md:334-349）。⚠️ 口径：README 7 个（不含 OpenCode），INSTALL_CN 8 个；OpenCode 为 2.0.1 起新增（F-013）。
- **F-029**: Claude Code 接入配置为设置 `ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default` 与 `ANTHROPIC_AUTH_TOKEN`，并配置 `--model`（INSTALL_CN.md:211-226）。
- **F-030**: 部署形态分 Standalone 与 Service：Standalone 使用 SQLite/本地文件/进程内状态；Service 使用 TCVDB/COS/Redis，面向 K8s 多副本与多租户（README.deployment.md:6-20）。
- **F-031**: Service 形态的 K8s 要点：ConfigMap/Secret 注入环境变量、Deployment 设置 `TDAI_DEPLOY_MODE=service`、Service 暴露 3100 端口（README.deployment.md:234-278）。
- **F-032**: Standalone Docker 示例：`docker run` 注入 LLM 参数、映射 8420:8420、挂载 tdai-data 卷，镜像名为 `agentmemory/hermes-memory:latest`（README.deployment.md:117-129）。
- **F-033**: 三个发布镜像为 `agentmemory/memory-core:latest`、`agentmemory/memory-hub:latest`、`agentmemory/memory-proxy:latest`，多架构 linux/amd64 + linux/arm64，发布在 Docker Hub 公开可拉（deploy/global-images/.env.example:15-25；CHANGELOG.md:240-242）。
- **F-034**: 部署脚本存在腾讯内网镜像源 `mirrors.tencent.com/memory-team-control/*`（信源：s-deploy）。
- **F-035**: 一键部署流程为 `cp .env.example .env`、填入两组 LLM 参数、执行 `./start-all.sh`；start-all 首次启动自动 init-admin、生成 `sk-mem-...` 并落盘 `.admin-key`，自检 `/v3/meta/auth/verify` 后打印可复制的 claude 启动命令（CHANGELOG.md:244-253）。
- **F-036**: `stop-all.sh --purge` 会清除 volume 与 admin key 用于重置（CHANGELOG.md:253）。

## 三、四层记忆模型与四类资产

- **F-037**: Chat Memory 分四个层级：L0 Conversation 原始对话 → L1 Atom 原子记忆 → L2 Scenario 场景 → L3 Core/Persona 长期认知（CHANGELOG.md:203-204；s-readme）。
- **F-038**: L0 原始对话以 JSONL 按天存储，路径形态 `conversations/YYYY-MM-DD.jsonl`（信源：s-core-readme）。
- **F-039**: L1 Atom 分为事实、偏好、约束、事件等类型，并归为 persona / episodic / instruction 三大类（信源：s-readme、s-core-code）。
- **F-040**: L2 Scenario 以 Markdown 文件存储在 `scene_blocks/*.md`，文件内含 META 分隔符与 heat（热度）数值（信源：s-core-code scene/）。
- **F-041**: 四类记忆资产为 Chat Memory、Skill、Wiki、CodeGraph（CHANGELOG.md:199-210）。
- **F-042**: Skill 资产从跑通的任务里提炼可复用 SOP，附带版本、资源文件、触发边界、执行步骤、验证规则；2.0.0 新增 Skill 强制归档功能（CHANGELOG.md:205-206）。
- **F-043**: Wiki 资产把文档变成结构化页面 + 链接图谱，README 注明灵感来自 Karpathy 的 LLM 知识库实践（CHANGELOG.md:207-208）。
- **F-044**: CodeGraph 资产索引仓库的符号/文件/调用关系/影响路径，供 Agent 改代码前做 impact analysis；2.0.0 新增定时自动同步代码库（CHANGELOG.md:209-210）。
- **F-045**: README 致谢声明确认 CodeGraph 复用了 github.com/colbymchenry/codegraph 的代码，Hermes Agent skill 代码亦为复用（信源：s-readme）。
- **F-046**: 可见性包含四个取值：private（Owner 只读，团队管理员不可见）、team、restricted（User/Role/Agent ACL）、agent（同团队 Agent 定向装配）（CHANGELOG.md:217-218；s-readme）。
- **F-047**: 角色分两层：全局 System Admin；团队内 Admin/Member；Owner 自动获得管理权（信源：s-readme）。
- **F-048**: Agent Loadout 机制支持给不同 Agent 绑定不同资产、调整优先级与使用方式（CHANGELOG.md:219）。
- **F-049**: CodeGraph 当前仅支持公开 HTTPS 仓库；Wiki/CodeGraph 为异步构建，需等待 ready 状态（信源：s-readme）。
- **F-050**: 数据格式存在 v2→v3 迁移脚本目录 `MemoryCore/scripts/migrate-v2-to-v3/`（含 README）；v2.0.0 起为数据格式 v3（信源：s-core-code、s-readme）。
- **F-051**: 检索采用 RRF 融合 BM25 与向量的混合检索，并受条数、字符预算与超时限制约束（信源：s-readme）。
- **F-052**: README 标注当前版本为 v2.0.0，ROADMAP 列出 v2.0.1 方向：零配置冷启动、Wiki 加速、自定义 Prompt、Skill 导出、Codex IDE Plan（信源：s-readme、s-roadmap）。
- **F-053**: ROADMAP_CN「下个版本 · v2.0.1」清单包含 Agent 模版、`mem:` 指令增强、记忆可编辑、L0/L1 记忆搜索、Cursor 支持等项（ROADMAP_CN.md:13-71）。
- **F-054**: 默认数据目录为 `~/.memory-tencentdb/memory-tdai`（信源：s-readme）。
- **F-055**: ⚠️ 口径：l0-recorder.ts 注释中出现路径 `~/.openclaw/memory-tdai/conversations/`，与 README 的 `~/.memory-tencentdb/memory-tdai` 为两套历史口径，并列登记（MemoryCore/src/core/conversation/l0-recorder.ts 注释）。
- **F-056**: README_CN 描述的 API 面包含 `/capture`、`/recall`、`/search/*`（兼容接口）与 `/v2/conversation|atomic|scenario|core` 分层接口（信源：s-readme）。

## 四、MemoryCore：L0/L1 抽取-去重-写入管线

- **F-057**: MemoryCore/package.json 声明包名 `@tencentdb-agent-memory/memory-tencentdb-v2`、版本 `1.0.2-beta.1`（信源：s-core-pkg）。
- **F-058**: 主要依赖包括 ai@^6、@ai-sdk/openai、sqlite-vec@0.1.7-alpha.2、@node-rs/jieba、mongodb@^6.21、js-tiktoken、zod@4、undici@8（信源：s-core-pkg）。
- **F-059**: optionalDependencies 包含 @clickhouse/client、cos-nodejs-sdk-v5、ioredis、kafkajs、opik；peerDependencies 包含 node-llama-cpp（本地 LLM）、openclaw>=2026.3.7（信源：s-core-pkg）。
- **F-060**: package.json bin 声明四个命令：migrate-sqlite-to-tcvdb、export-tencent-vdb、read-local-memory、seed-v2（信源：s-core-pkg；bin/*.mjs）。
- **F-061**: L1 抽取默认参数：maxMessagesPerExtraction=10、maxBackgroundMessages=5、enableDedup=true、maxMemoriesPerSession=10（l1-extractor.ts:147-153）。
- **F-062**: L1 去重召回参数 conflictRecallTopK=5（l1-dedup.ts）。
- **F-063**: 去重候选召回走 hybrid/FTS/vector + RRF 融合；检索能力缺失时降级为全量保存（l1-dedup.ts）。
- **F-064**: 去重 LLM 判定超时或失败时降级为全量 store；判定结果为四个决策值：store / skip / update / merge（l1-dedup.ts）。
- **F-065**: L1 写入采用 JSONL 主存 + 向量双写：嵌入失败时仅写 metadata/FTS，向量失败不阻塞 JSONL 主存（l1-writer.ts:257-351）。
- **F-066**: L0 记录器实现于 l0-recorder.ts；L0 表/文件含 team_id、user_id、agent_id、session_key、session_id、task_id 隔离字段（sqlite/memory-store.ts）。
- **F-067**: hooks/auto-capture.ts 在捕获时写 L0 记录并打 checkpoint；可选 L0 向量，supportsDeferredEmbedding 时后台延迟嵌入（hooks/auto-capture.ts）。
- **F-068**: hooks/auto-recall.ts 的召回用 Promise.race 做超时控制，超时返回 RecallResult.error，hook 层不向上抛错；支持 keyword/embedding/hybrid 三种模式（hooks/auto-recall.ts）。
- **F-069**: L1 抽取 prompt 位于 core/prompts/l1-extraction.ts，去重 prompt 位于 l1-dedup.ts，场景抽取 prompt 位于 scene-extraction.ts（信源：s-core-code prompts/）。
- **F-070**: L1 reader 实现于 record/l1-reader.ts，负责读取与隔离过滤（record/l1-reader.ts）。
- **F-071**: 隔离过滤结构 IsolationFilter 含 teamId、userId、agentId、sessionId、taskId、sessionKey 六字段（store/isolation.ts）。
- **F-072**: 状态后端 local-backend.ts 维护 sessionStates、buffers、timers、taskQueue、pendingTasks、locks 等内存结构（state/local-backend.ts）。
- **F-073**: capture 达到阈值即入队，否则由定时器冲刷；timer-member 映射覆盖 L1/L2/L3/flush 四类成员（state/local-backend.ts、state/timer-member.ts）。
- **F-074**: 后台服务包含 pipeline-worker、timer-scanner、worker-permit-pool 三个（services/）。
- **F-075**: 存储抽象层 storage/adapter.ts 配 factory.ts，本地实现 local-backend.ts、Mongo 实现 mongo-fs-backend.ts（core/storage/）。
- **F-076**: 工具层含 memory-search.ts 与 read-cos.ts 两个内部工具（core/tools/）。
- **F-077**: 报告层支持 console、file、noop、obs、otlp 多种 backend，由 report/factory.ts 选择（core/report/）。
- **F-078**: API 追踪子系统 api-trace 含策略、脱敏、stdout、OTel 上下文传播与 traced-proxy（api-trace/）。
- **F-079**: OpenClaw 适配位于 adapters/openclaw/（index.ts、llm-runner.ts），standalone 适配位于 adapters/standalone/index.ts（adapters/）。
- **F-080**: 内存清理与备份工具位于 utils/memory-cleaner.ts、utils/backup.ts、utils/checkpoint.ts（utils/）。

## 五、MemoryCore：L2 场景、L3 Persona、自定义 Prompt 与配额

- **F-081**: SceneExtractor 参数包含 timeoutMs=300000（5 分钟）、sceneBackupCount、maxScenes（scene-extractor.ts:112-133）。
- **F-082**: 场景文件使用 META_START/META_END 分隔符包裹元数据，元数据含 heat 数值（scene/scene-format.ts）。
- **F-083**: syncSceneIndex 通过扫描 scene_blocks/*.md 重建场景索引（scene/scene-index.ts）。
- **F-084**: 场景导航与派生分别实现于 scene-navigation.ts、scene-derive.ts（core/scene/）。
- **F-085**: Persona 触发分 5 类：显式请求、冷启动、恢复、首个 scene block、阈值触发（persona-trigger.ts:35-96）。
- **F-086**: profile-scope.ts 定义 scope 串形态 `team:...|agent:...`，提供 profileScopeFilter 与 profileRowInScope 行级校验（profile/profile-scope.ts）。
- **F-087**: profile-sync.ts 负责 profile 在作用域间同步（profile/profile-sync.ts）。
- **F-088**: memory-prompt 解析优先级为 agent → team → instance → 内置默认（memory-prompt/resolver.ts）。
- **F-089**: 每个 instance 最多 500 条 prompt，单条 prompt ≤ 10000 Unicode 字符；版本递增但 memory_prompt_id 保持不变（memory-prompt/*.ts 与 gateway/memory-prompt-schemas.ts）。
- **F-090**: composer 注入占位符 `<CUSTOM_MEMORY_STRATEGY>` 与 `<SYSTEM_CUSTOM_STRATEGY_GUARD>`（memory-prompt/composer.ts）。
- **F-091**: L1 输出固定为 JSON、L2 固定为 Scene Markdown、L3 固定为 Persona+Doctrine 的输出协议不可通过自定义 prompt 修改（memory-prompt/composer.ts）。
- **F-092**: 生成日志记录 Prompt ID、版本、来源、SHA-256，不存储 prompt 正文（memory-prompt 与 memory-generation-log 相关实现）。
- **F-093**: API 面含 `/v3/memory-prompt/*`（create/get/update/delete/set/log）与 `/v3/memory-generation-log/list|get`（信源：s-readme、s-core-api）。
- **F-094**: credit-calculator.ts 定义 DEFAULT_RATES（input/cache/output 三费率）与 DEFAULT_MODEL_MULTIPLIERS（模型倍率）（quota/credit-calculator.ts）。
- **F-095**: quota-manager.ts 实现配额管理；gateway 侧配额策略在 quota-credit-policy.ts（quota/、gateway/）。
- **F-096**: instance-config-provider.ts 提供每实例配置；tdai-core.ts 为核心装配入口（core/ 根）。
- **F-097**: 元数据面独立实现于 metadata/：router（auth/instance/pagination）、store（sqlite-adapter、db-name、factory、interface）、utils（crypto、id-generator、user-key）（metadata/）。
- **F-098**: 元数据库命名为 tdai_metadata_<instance>，数据面库命名为 tdai_memory（metadata/store/db-name.ts；部署文档）。
- **F-099**: 元数据面内置 system-user.ts 系统用户与 constants.ts 常量（metadata/）。
- **F-100**: seed 子系统含 input.ts、seed-runtime.ts、types.ts，对应 bin seed-v2（core/seed/、cli/commands/seed.ts）。
- **F-101**: CLI 入口 src/cli/index.ts 含命令注册与 README 说明（cli/）。
- **F-102**: 网关 LLM 解析逻辑在 llm-resolver.ts，支持 openai|anthropic 协议（gateway/llm-resolver.ts）。
- **F-103**: 环境配置工具有 env.ts、env-config.ts；部署模式相关常量在 gateway/metadata-env.ts（utils/、gateway/）。
- **F-104**: 网关内置 chat-memory-handlers.ts（/capture /recall 兼容面）、knowledge-handlers.ts（知识代理调用）（gateway/）。
- **F-105**: 网关上 generated/schemas.ts 与 types.ts 由 kubb.config.ts 配置生成（gateway/generated/、kubb.config.ts）。
- **F-106**: 根 index.ts 与 openclaw.plugin.json 声明包入口与 OpenClaw 插件元数据；postinstall 会对 openclaw 打 patch，兼容 pluginApi>=2026.3.13（信源：s-core-pkg、s-core-code）。

## 六、MemoryCore：存储后端与混合检索

- **F-107**: 后端选择逻辑：存在 mongoConfig → mongodb；service/tcvdb 模式且有 VDB 配置 → tcvdb；否则 sqlite（默认）（store/factory.ts:57-168、store/store-pool.ts:171-218）。
- **F-108**: TCVDB 连接需 url、apiKey、database 三项（store/tcvdb/client.ts）。
- **F-109**: TCVDB 向量索引优先 DISK_FLAT，回退 HNSW（带 M/efConstruction 参数）（store/tcvdb/memory-store.ts）。
- **F-110**: 无 embedding 能力时建 dim=1 占位向量索引；sparse vector 承载 BM25（tcvdb/memory-store.ts）。
- **F-111**: SQLite 实现于 store/sqlite/memory-store.ts，主表包括 l1_records、l0_conversations，隔离字段 team_id/user_id/agent_id/session_key/session_id/task_id 直接落列（sqlite/memory-store.ts、scripts/db/sqlite-init.sql）。
- **F-112**: 向量表 l1_vec、l0_vec 使用 sqlite-vec vec0 虚表、cosine 距离；FTS5 全文表同样包含隔离字段（sqlite/memory-store.ts）。
- **F-113**: SQLite 数据库文件名为 vectors.db（信源：s-core-code）。
- **F-114**: RRF 融合参数 RRF_K=60，融合公式为 1/(k+rank+1) 求和（store/search-utils.ts）。
- **F-115**: bm25-local.ts 以 `@tencentdb-agent-memory/tcvdb-text` 的 TS 实现替代 Python sidecar（store/bm25-local.ts）。
- **F-116**: bm25-client.ts 在 BM25 服务不可达时返回空向量并标记不健康（store/bm25-client.ts）。
- **F-117**: 分词使用 @node-rs/jieba，封装于 store/tokenize.ts（store/tokenize.ts）。
- **F-118**: embedding 封装于 store/embedding.ts（store/embedding.ts）。
- **F-119**: profile 行级存取独立实现于 store/profile-row-store.ts（store/profile-row-store.ts）。
- **F-120**: 列表分页抽象在 store/list-page.ts（store/list-page.ts）。
- **F-121**: TCVDB Skill 存储独立实现于 store/tcvdb/skill-store.ts，SQLite Skill 存储在 store/sqlite/skill-store.ts（store/）。
- **F-122**: MongoDB 初始化脚本为 scripts/db/mongodb-init.js（要求 Mongo 7.0+ mongot，见 INSTALL_CN 与 docker-compose.local-mongo.yaml）（scripts/db/、docker-compose.local-mongo.yaml）。
- **F-123**: SQLite 初始化 DDL 脚本为 scripts/db/sqlite-init.sql（scripts/db/）。
- **F-124**: tdai-gateway.yaml、tdai-gateway.standalone.yaml、tdai-gateway.local-mongo.yaml 三套网关配置分别对应默认/standalone/本地 Mongo（MemoryCore/ 根）。
- **F-125**: 存储后端类型与适配器接口定义在 store/types.ts、store/adapter.ts、store/index.ts（store/）。
- **F-126**: backend-selection 模块（index.ts、types.ts）集中后端决策（core/backend-selection/）。
- **F-127**: 抽象类型层 abstractions/types.ts 定义核心接口（core/abstractions/）。
- **F-128**: 工具调用面含 `/v3/tools/list`、`/v3/tools/call`（信源：s-readme、s-core-api）。
- **F-129**: read-cos.ts 提供从 COS 读取资源的内部工具（core/tools/read-cos.ts）。
- **F-130**: 导出/迁移工具：bin/export-tencent-vdb.mjs、bin/migrate-sqlite-to-tcvdb.mjs（bin/）。

## 七、MemoryCore：Skill 子系统

- **F-131**: Skill 数据层 v2 重构含三张物理对象：skills 主表、skill_fts（fts5）、skill_vec（vec0，仅 dimensions>0 创建）；注释明确不建 skill_bindings/task_skill_drafts/skill_resources/assets 等表（绑定下沉管控面、manifest 收敛主表）（skill/skill-store-ddl.ts:1-15）。
- **F-132**: skills 主表字段含 row_id、skill_id、version、is_head、user_id、owner_agent_id、team_id、task_id、name、description、content、content_hash、manifest_json、storage_dir、status、metadata_json、created_at_ms、updated_at_ms，UNIQUE(skill_id, version)（skill-store-ddl.ts:21-46）。
- **F-133**: 主表唯一索引 `uniq_skills_team_agent_name_head` 作用于 (team_id, owner_agent_id, name) 且仅 is_head=1 AND status='active'；另有 team/owner/user/version/task 五个辅助索引（skill-store-ddl.ts:48-64）。
- **F-134**: skill_fts 为 fts5 虚表，索引 name/description/content 与四个 UNINDEXED 隔离列，分词器 `unicode61 remove_diacritics 1`（skill-store-ddl.ts:71-83）。
- **F-135**: skill_vec 为 vec0 虚表，embedding float[__DIM__]、distance_metric=cosine，__DIM__ 在 init 时替换为实际维度（如 1536）（skill-store-ddl.ts:89-97）。
- **F-136**: FTS 索引 content 最大字符数常量 FTS_CONTENT_MAX=4000（skill-store-ddl.ts:103-104）。
- **F-137**: SkillCore 的 create/update 写路径解析校验 SKILL.md、生成或校验 skill_id、调用 SkillVersioning 创建/追加版本，校验失败抛 SkillCoreError（skill/skill-core.ts:251-313）。
- **F-138**: delete 物理删除所有版本并触发归档回调；writeFiles 经 requireHead、owner 校验与乐观锁后追加新版本（skill-core.ts:373-401）。
- **F-139**: get 读路径支持指定版本或默认 head；指定版本先确认 head 存在，再按 (skill_id, version, team_id) 查询并触发访问后处理（skill-core.ts:452-475）。
- **F-140**: 权限校验为纯函数，包含 owner 校验、team 匹配、expected_version 与 head version 一致的乐观锁校验，错误码对齐 403/404/409（skill/skill-permission.ts:33-68）。
- **F-141**: 版本追加逻辑计算新 version、检测内容/资源是否变化、拷贝旧版本目录、应用资源变更、写 DB 并同步 VDB delta（skill/skill-versioning.ts:212-301）。
- **F-142**: 抽取入口校验 ExtractMessage[]、格式化/截断 transcript，按 prefixSkillsLimit 做 full/relevant/recent 三档预检索后组装 LLM prompt（skill/skill-extractor.ts:128-196）。
- **F-143**: skill-fast-path.ts 实现快速通道；skill-config.ts 为配置；skill-format.ts 负责 SKILL.md 格式化；skill-tools.ts 定义供 Agent 调用的工具（skill/）。
- **F-144**: skill 队列模块 queue/（index.ts、types.ts）承载异步提取排队（skill/queue/）。
- **F-145**: `/v3/skill/*` 共注册 17 个端点：create、update、patch、delete、get、get-by-name、list、search、versions、files/write、files/remove、files/read、export、listing、extract、conversation/add、conversation/force-archive（gateway/skill-handlers.ts:1155-1171）。
- **F-146**: skill handler 前置校验在 service 模式优先 `resolveSkillCore(auth.serviceId)` 获取 per-instance core，回退到 standalone `getSkillCore()`，再校验请求参数（gateway/skill-handlers.ts:188-213）。
- **F-147**: skill-schemas.ts 使用 Zod 定义请求 schema；手动触发抽取的契约照搬 `/v3/skill/conversation/add`（gateway/skill-schemas.ts:215）。
- **F-148**: TCVDB Skill 存储与 SQLite Skill 存储分别实现于 store/tcvdb/skill-store.ts 与 store/sqlite/skill-store.ts（store/）。
- **F-149**: openclaw-plugin 子包含独立 package.json、openclaw.plugin.json 与 hooks/capture.ts、hooks/recall.ts、format.ts、sanitize.ts（MemoryCore/openclaw-plugin/）。
- **F-150**: pi-plugin 子包为 pi 平台插件（index.ts、package.json、vitest.config.ts）（MemoryCore/pi-plugin/）。

## 八、MemoryCore：网关、隔离与 API 契约

- **F-151**: v2-router 的统一响应信封为 `{code, message, request_id, data}`（gateway/v2-router.ts）。
- **F-152**: 请求体使用 Zod v4 safeParse 校验，失败返回 400（gateway/v2-router.ts、v2-schemas.ts）。
- **F-153**: v3 接口 collectV3Missing 强制要求 team_id + agent_id + user_id 三项，缺失返回 422；三项可从 body 或 `x-tdai-team-id`/`x-tdai-agent-id`/`x-tdai-user-id` 请求头获取；session_id 可选（gateway/v2-router.ts）。
- **F-154**: V3_ALLOWED_SUBPATHS 共 18 个：conversation 5、atomic 5、scenario 5、core 3（gateway/v2-router.ts）。
- **F-155**: 部署模式配置 deployMode 取值 standalone / service；FILE_STORE_MODE 在 service 模式为 cos、standalone 为 local（gateway/config.ts）。
- **F-156**: 鉴权采用 Bearer 令牌 + `x-tdai-service-id` 头；`/health` 与 CORS 预检豁免鉴权；CORS 使用白名单（gateway/config.ts）。
- **F-157**: `/v3/skill/*` 路径在鉴权豁免判断中单独列出（v2-router.ts:305、512、534；server.ts:705）。
- **F-158**: server.ts 同时承载 /v2 记忆接口与 /v3/skill/conversation/add 的 per-instance 路由（gateway/server.ts:2559）。
- **F-159**: v3 API 面包含 `/v3/skill/*`、`/v3/meta/*`、`/v3/knowledge/*`、`/v3/memory-prompt/*`、`/v3/memory-generation-log/*`、`/v3/tools/*`（信源：s-core-api）。
- **F-160**: 元数据面端点包括 `/v3/meta/auth/verify`、`/v3/internal/meta/user/init-admin`（部署脚本调用）（信源：s-deploy、s-core-api）。
- **F-161**: knowledge-handlers.ts 代理 Core 对 Knowledge 的调用；analytics/index.ts 提供 ClickHouse 查询接口（gateway/）。
- **F-162**: error-handler.ts 统一错误处理（gateway/error-handler.ts）。
- **F-163**: 网关配置文件 tdai-gateway.yaml 声明监听 8420（信源：s-core-code tdai-gateway*.yaml）。
- **F-164**: Dockerfile 运行时基础镜像 node:22-slim，EXPOSE 8420，定义 healthcheck，ENTRYPOINT 为 tini，CMD 启动 gateway（MemoryCore/Dockerfile:126-165）。
- **F-165**: 生产部署要求 STORE_MODE 等环境变量经容器注入；配置文件只读挂载（start-memory-core.sh:203-219）。
- **F-166**: 管理员初始化：默认用户名 admin，随机生成 `sk-mem-*` key 写入 ${MEMORY_CORE_ADMIN_KEY_FILE}，经 init-admin 与 auth/verify 双接口校验（start-memory-core.sh:256-309）。
- **F-167**: MEMORY_CORE_GATEWAY_API_KEY 留空等于关闭 Bearer 鉴权（本地零配置）（信源：s-deploy .env.example）。
- **F-168**: MEMORY_CORE_STORE_MODE 取值 sqlite（默认）/mongodb（试验，需 Mongo 7.0+ mongot，不静默降级）；MEMORY_CORE_METADATA_BACKEND 取值 auto/sqlite（信源：s-deploy .env.example）。
- **F-169**: MEMORY_PROMPT_MODE 取值 code（默认）/chat（信源：s-deploy .env.example）。
- **F-170**: 两组 LLM 配置分离：MEMORY_LLM_*（core/hub 内部使用，含 MEMORY_LLM_PROTOCOL=openai|anthropic）与 PROXY_UPSTREAM_*（代理上游）（信源：s-deploy）。
- **F-171**: v3-api-memorycore-doc.md 为 v3 接口权威文档（随仓 Markdown）（s-core-api）。
- **F-172**: 观测相关脚本含 e2e-memory-prompt-vdb-cos.ts、start-e2e-gateway.ts、bench-l0-mongo/ 性能基准 7 文件（scripts/）。

## 九、MemoryCore：offload 卸载与上下文压缩管线

- **F-173**: offload 以 OpenClaw 插件形态实现，入口 registerOffload（offload/index.ts）。
- **F-174**: offload 模式分 backend / collect / local 三种（offload/index.ts）。
- **F-175**: L1 批量参数 L1_BATCH_SIZE=5；失败重试 MAX_L1_CHUNK_RETRIES=3，重试后降级写 `[L1 degraded]` 条目（offload/index.ts）。
- **F-176**: L1.5 任务边界判定（l15Judge）有 1 次重试、间隔 3000ms，fail-safe 时推 short boundary（offload/index.ts）。
- **F-177**: L2 批量 30 条、每 5 秒轮询；含 null 阈值 l2NullThreshold 与 l2TimeoutSeconds；L1.5 60 秒超时强制 settle（offload/index.ts）。
- **F-178**: L2 产出 MMD（.mmd 任务节点文件），节点 ID 正则为 `\d{3}-N\d+`（offload/pipelines/l2-mermaid.ts、mmd-meta.ts）。
- **F-179**: L4 对应 create-skill 斜杠命令生成 SKILL.md（offload/index.ts）。
- **F-180**: L3 为 token 溢出压缩，实现 llm-input-l3.ts：compressByScoreCascade、aggressiveCompressUntilBelowThreshold、emergencyCompress，含 EMERGENCY_MIN_MESSAGES_TO_KEEP（offload/hooks/llm-input-l3.ts、l3-helpers.ts）。
- **F-181**: token 计数使用 tiktoken o200k_base 编码（l3-token-counter.ts、fast-token-estimate.ts、context-token-tracker.ts）。
- **F-182**: 内部会话正则 `/memory-.*-session-\d+/`；心跳 HEARTBEAT 消息被过滤（offload/index.ts、utils/session-filter.ts）。
- **F-183**: after_tool_call hook 攒工具调用 pair，forceTriggerThreshold 默认 4（offload/hooks/after-tool-call.ts）。
- **F-184**: offload 配套文件含 backend-client.ts、reclaimer.ts、session-registry.ts、state-manager.ts、mmd-injector.ts、storage.ts、opik-tracer.ts（offload/）。
- **F-185**: 独立 offload_server/ 提供 ingest-handler、mmd-handler、router、schemas、session-utils（offload_server/）；offload-client/context-engine.ts 为客户端（offload-client/）。
- **F-186**: 本地 LLM 路径 offload/local-llm/（index.ts、llm-caller.ts），对应 peer 依赖 node-llama-cpp（offload/local-llm/）。
- **F-187**: hooks/llm-output.ts 处理 LLM 输出侧卸载（offload/hooks/llm-output.ts）。
- **F-188**: 工具脚本 install-openclaw-plugin.sh、install-hermes-plugin.sh 负责插件安装（scripts/）。
- **F-189**: openclaw-plugin 文档 docs/architecture.md 描述插件架构（openclaw-plugin/docs/）。
- **F-190**: MemoryCore/SKILL.md、SKILL-MIGRATION.md、SKILL-DIAGNOSTIC-EXPORT.md 为随仓 Skill 使用/迁移/诊断文档（MemoryCore/ 根）。

## 十、MemoryKnowledge：知识引擎

- **F-191**: package.json 声明两个 bin：knowledge-server（bin/server.mjs）与 knowledge-mcp（bin/mcp.mjs）（MemoryKnowledge/package.json）。
- **F-192**: config 默认端口 8421、SQLite DB 路径 `./data/knowledge.db`、LLM 默认经 proxy/openai（src/config.ts:147-180）。
- **F-193**: server.ts 基于 Hono，在 /v3 下挂载 wiki、code-graph、tools、internal、llm-binding、auto-sync、analytics 路由，并暴露 /openapi.json 与 /docs；只读白名单免 service key（src/server.ts、middleware/auth.ts）。
- **F-194**: SQLite 经 better-sqlite3 以 WAL 模式与 busy timeout 打开（src/db/client.ts）。
- **F-195**: DDL 共 5 张表：knowledge_code_graph、knowledge_wiki、knowledge_wiki_audit、knowledge_code_graph_audit、llm_binding（src/db/schema.ts）。
- **F-196**: code_graph 表字段含 code_graph_id、repo_url、branch、status、internal_status、sync_error、stats_json；wiki 表含 wiki_id、source_type、source_url、status、internal_status、page_count、service_url、summary；llm_binding 含 mode、proxy_base_url、api_key、base_url、enabled（src/db/schema.ts）。
- **F-197**: 状态枚举 SyncStatus = pending | processing | ready | failed；WikiStatus 额外含 draft；codegraph 创建默认 pending，wiki 创建默认 draft（store/types.ts）。
- **F-198**: 幂等规则：codegraph 按 (service_id, team_id, repo_url, branch) 查重；wiki 按 (service_id, team_id, name) 查重（store/code-graph-service.ts、wiki-service.ts）。
- **F-199**: 构建状态机为 pending→processing→ready/failed；busy/not_found 有独立返回；全程写审计并通过 TMC callback 回调（store/build-queue.ts、callback.ts）。
- **F-200**: 自动同步由环境变量 KNOWLEDGE_AUTO_SYNC_ENABLED、SCAN_INTERVAL_MIN、MAX_CONCURRENT 控制；仅扫描 status=ready 的 codegraph，inFlight 去重 FIFO（store/auto-sync-scheduler.ts、routes/auto-sync.ts）。
- **F-201**: auto-sync 端点为 GET /auto-sync/status 与 POST /auto-sync/trigger（routes/auto-sync.ts）。
- **F-202**: MCP 暴露 12 个只读工具：code 侧 8 个 code_search/code_explore/code_callers/code_callees/code_impact/code_node/code_status/code_files；wiki 侧 4 个 wiki_search/wiki_read/wiki_list/wiki_graph；管理操作不暴露给 MCP（src/mcp/tools.ts）。
- **F-203**: MCP 服务端与 HTTP 客户端分别在 mcp/server.ts、mcp/http-client.ts（src/mcp/）。
- **F-204**: 每个 Wiki 有独立 SQLite 索引库 index.db，含 wiki_fts（BM25 虚表）、page_meta、graph_edge、source 表（engines/wiki/index-db.ts）。
- **F-205**: Wiki 索引写用独立连接、读用 LRU 连接池（engines/wiki/index-db.ts）。
- **F-206**: wikilink 正则为 `/\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]/g`（engines/wiki/manager.ts:89）；仅取 visible 页面，滤除 hidden/自环/不可解析目标，(source,target) 去重后写 graph_edge；读时从 graph_edge 临时构建 graphology 实例做多跳 BFS（engines/wiki/manager.ts:7-9）。
- **F-207**: Wiki ingest-v2 流水线含 14 个模块：chunker、cascade、prompts、llm、overview、merge、frontmatter、slug、safe-path、template、index-builder、log-writer、file-protocol、index（engines/wiki/ingest-v2/）。
- **F-208**: llm-binding 模式为 proxy | byo；proxy 模式生成 `/proxy/{service_id}/v1` 形态 URL（routes/llm-binding.ts、store/llm-binding-store.ts）。
- **F-209**: llm-binding 端点 POST /v3/internal/llm-binding/set|status|list（需 x-tdai-service-id）；status/list 不返回明文 key，只回 has_api_key 布尔（routes/llm-binding.ts）。
- **F-210**: 代码引擎 engines/code/ 含 bridge.ts、index.ts、normalize.ts；source-fetcher 含 git-fetcher 与注册表（engines/code/、source-fetcher/）。
- **F-211**: 遥测点击穿至 ClickHouse（clickhouse-telemetry.ts、analytics-routes.ts、telemetry.ts）。
- **F-212**: 响应信封与错误处理中间件在 middleware/response-envelope.ts、error-handler.ts（src/middleware/）。
- **F-213**: Dockerfile 设置 PORT=8421、EXPOSE 8421、healthcheck 调用 /health、ENTRYPOINT 为 docker-entrypoint.sh（MemoryKnowledge/Dockerfile:77-89）。
- **F-214**: docker/entrypoint.sh 要求 --public-url；LLM routing 支持 proxy/custom；环境变量映射 KNOWLEDGE_PUBLIC_BASE_URL、LLM_API_KEY、LLM_BASE_URL（docker/entrypoint.sh:17-48）。
- **F-215**: 部署侧 KNOWLEDGE_PUBLIC_BASE_URL 默认 `http://host.docker.internal:8424/v3`；KNOWLEDGE_SERVICE_KEY 留空自动生成 ks-svc-*（deploy .env.example）。
- **F-216**: v3-api-memoryknowledge-doc.md 与 openapi.yaml 随仓提供；仓库含 drizzle.config.ts（ORM 配置）与 docker-compose.yml（s-know-doc、s-know-code）。

## 十一、MemoryProxy：LLM 代理

- **F-217**: 包名为 context-proxy、版本 0.1.0；依赖 hono@^4.7.10；启动命令 `node --import tsx/esm src/index.ts`（MemoryProxy/package.json）。
- **F-218**: 默认监听 0.0.0.0:8096，配置文件形态 config.example.yaml（src/config.ts、config.example.yaml）。
- **F-219**: 双协议：OpenAI 兼容 `/v1/chat/completions` 与 Anthropic 兼容 `/v1/messages`；支持 SSE 流式（src/handler.ts、anthropicHandler.ts、directHandler.ts）。
- **F-220**: agent-adapters 工厂注册 8 个适配器：claude-code、codebuddy、codex、workbuddy、dsh、opencode、pi、default；AgentAdapter 接口含 classifyRequest、extractUserText（src/agent-adapters/，含 index.ts 共 10 文件）。
- **F-221**: 路由包括 /health、/whoami、/direct/*、/skill-bridge/*、/memory-bridge/*（src/server.ts）。
- **F-222**: memory-bridge 白名单 ALLOWED_SUBPATHS = {atomic/search, atomic/query, conversation/search, conversation/query, scenario/ls, scenario/read}（src/memory/memory-bridge.ts）。
- **F-223**: 与 Core 交互端点：/v3/skill/conversation/add（写回）、/v3/meta/auth/verify、/v3/atomic/search、/v3/conversation/search、/v3/scenario/ls、/v3/scenario/read（src/tdai/client.ts、skill/core-client.ts）。
- **F-224**: 注入边界标记包括 `<tdai_recalled_l1_memories>`、`<tdai_profile_memory>`、`<l3_core_memory>`、`<l2_scene_index>`、`<tdai_memory_tools>`、`<memory-tools-guide>`（src/injection/injectors/）。
- **F-225**: 注入器共 8 个：tdai-tools、tdai-profile-memory、tdai-l1-recall、tdai-fixed-asset、skill-tools、skill、knowledge-tools、asset-reflection（src/injection/injectors/）。
- **F-226**: 注入管线含 registry、provider、pipeline、observer、context、prewarm 六模块（src/injection/）。
- **F-227**: 注入适配分 openai.ts 与 anthropic.ts 两套序列化；agent 画像含 codebuddy、workbuddy、pi、claude-code 四套（src/injection/adapters/、agents/）。
- **F-228**: 环境变量含 TDAI_MEMORY_SYSTEM_USER_ID、TDAI_MEMORY_SYSTEM_USER_KEY、TDAI_PROXY_ADMIN_API_KEY、PROXY_DB_PATH（Docker 默认 /data/tdai-memory-proxy/proxy.db）（src/config.ts、信源：s-deploy）。
- **F-229**: v3-api-memoryproxy-doc.md 登记 6 个管理接口：/v3/instance/proxy-destroy、/v3/admin/rate-limits（GET/PUT/DELETE）、/v3/session/refresh-cache、/v3/session/force-archive-skill；章节为公共约定/接口目录/实例销毁/频控/Session（s-proxy-doc；src/routes/）。
- **F-230**: 频控实现于 rate-limit/（guard.ts、usage.ts、redis-store.ts）（src/rate-limit/）。
- **F-231**: 会话体系 src/session/ 含 store、registrar、session-key、preset、context-injector、client-capabilities、restore-space-id 等 13 个文件，并按客户端分子目录 claude-code/codebuddy/codex/workbuddy/dsh/opencode（src/session/）。
- **F-232**: sessionInit 首轮引导通过 AskUserQuestion 让用户选 team/agent/task，proxy 持久化绑定（CHANGELOG.md:230-231；src/session/）。
- **F-233**: 鉴权链路：x-tdai-user-key → 内核 /v3/meta/auth/verify 换 user_id，按用户维度控制资产可见性（CHANGELOG.md:234-235；src/auth.ts、src/meta/client.ts）。
- **F-234**: 会话内 mem 指令实现于 mem-command/：parser、pre-intercept、pending-store、task-draft-generator、response-builder；commands 含 create-task、update-task、sync、session-reset、help、create-skill 六个（src/mem-command/）。
- **F-235**: Skill 桥接模块 skill/ 含 skill-bridge、handler-glue、core-client、normalize-conversation、version-pin-repo、kv-version-pin-repo（src/skill/）。
- **F-236**: 存储抽象 storage/ 含 sqlite-storage、fs-storage、cos-storage、memory-storage、factory、per-key-mutex、key-utils 与 cos-types（src/storage/）。
- **F-237**: db/ 含 sessionRepo、binding-repo、hookCacheRepo 及 redis/kv 双实现与 schema（src/db/，11 文件）。
- **F-238**: tdai 子模块含 recorder、pending-writes、identity、capabilities、client、types（src/tdai/）。
- **F-239**: 特有处理器 workbuddyHandler.ts、codexHandler.ts、auxiliaryHandler.ts；extraction-gate.ts、guard-adapter.ts 做请求门控（src/ 根）。
- **F-240**: 可观测/计费集成含 pricing.ts、credit-reporter.ts、clickhouse.ts、langfuse.ts、opik.ts、judge-client.ts、requestLog.ts（src/ 根、src/report/）。
- **F-241**: dsh 接入支持 aux 请求短路（compaction / title-gen）与 CLI headless bypass（CHANGELOG.md:171-173）。
- **F-242**: turnSeq.ts、trace-archive.ts、instance-upstream-cache.ts 处理轮次序号、追踪归档与上游缓存（src/ 根）。
- **F-243**: systemUser.ts 与 systemUserPassthrough.ts 处理系统用户身份透传（src/ 根）。
- **F-244**: Dockerfile EXPOSE 8096，使用 tini entrypoint（信源：s-proxy-code）。
- **F-245**: README 原文要求把 coding agent 的 upstream 指向 proxy 并在 path 中带 spaceId；强调「无需插件/hook/MCP」（MemoryProxy/README.md）。
- **F-246**: scripts 含 setup-claude-code.sh、proxy.sh 与 qa/task-e2e.sh、qa/codex-init.sh（MemoryProxy/scripts/）。

## 十二、MemoryPanel/Hub：团队操作台

- **F-247**: 包名 team-memory-control、版本 0.1.0；依赖 hono、@hono/node-server、dotenv、jose、ulid、zod；脚本含 dev/build/start/test/openapi 生成（MemoryPanel/package.json:1-35）。
- **F-248**: 入口 src/panel/index.ts 加载配置、构建依赖与 Hono app；日志声明 API 前缀为 `/api/v1/meta/*`（src/panel/index.ts:7-24）。
- **F-249**: API 为 POST RPC 风格；analytics-actions.ts 对接内核 Analytics，列出 config、spaces、session-init/*、tool-calls/*、usage/*、usage-raw/list 等 16 个 action，区分 GET/POST；ClickHouse 未配置时返回 503（src/panel/api/analytics-actions.ts:18-55）。
- **F-250**: meta-api 为无状态透明代理（stateless）（信源：s-panel-code）。
- **F-251**: .env.example 含 KNOWLEDGE_SERVICE_URL、KNOWLEDGE_AUTH_TOKEN、KNOWLEDGE_TIMEOUT_MS 及 LLM binding 同步变量（MemoryPanel/.env.example:33-46）。
- **F-252**: OpenAPI 描述文件 docs/api/meta-api.openapi.yaml 由 scripts/generate-meta-openapi.ts 生成（docs/api/、scripts/）。
- **F-253**: 脚本含 e2e-knowledge-authz.sh、e2e-skill-authz.sh（授权端到端）、secret-scan.sh、install-git-hooks.sh、mock-memory-server.ts（scripts/）。
- **F-254**: Hub 镜像 agentmemory/memory-hub 同时包含 Panel 与 Knowledge Service（CHANGELOG.md:214）。
- **F-255**: memory-hub 容器名 tdai-memory-hub，端口映射 PANEL_PORT:8125、KNOWLEDGE_PORT:8424，卷 PANEL_VOLUME:/data/knowledge（start-memory-hub.sh:86-118）。
- **F-256**: start-memory-hub.sh 注入 REMOTE_INSTANCE_URL=http://memory-core:8420（start-memory-hub.sh:19-23）。
- **F-257**: hub 启动要求变量 MEMORY_HUB_IMAGE、PANEL_PORT、KNOWLEDGE_PORT、PANEL_VOLUME、LLM 参数、KNOWLEDGE_PUBLIC_BASE_URL（start-memory-hub.sh:19-23）。
- **F-258**: Panel 提供团队/Agent/资产（Owner/版本/状态/可见性）统一管理、Agent Loadout 配置、Wiki+CodeGraph 工坊、中英文切换（CHANGELOG.md:212-222）。
- **F-259**: 2.0.1 面板新增登录页点阵波纹动效、团队编辑/删除入口整合进团队切换器、管理员创建账号可自定义 User_Key、资产 ID 展示与一键复制（CHANGELOG.md:109-116）。
- **F-260**: docker/local/Dockerfile.local 为本地构建镜像（MemoryPanel/docker/）。
- **F-261**: panel-api-doc.md 为面板 API 说明文档（MemoryPanel/ 根）。
- **F-262**: 2.0.2-beta.1 起 Panel 兼容 OAuth2 登录，登录身份与 user_key 自动打通（CHANGELOG.md:40-46）。

## 十三、部署拓扑与脚本

- **F-263**: start-all.sh 启动顺序为 memory-core → memory-hub → proxy，各组件等待 healthy 后继续（deploy/global-images/start-all.sh:1-55）。
- **F-264**: start-all.sh 调用 require_vars 校验必填环境变量；proxy 默认以 PROXY_FULL_STACK=1 启动（start-all.sh:1-55）。
- **F-265**: start-all.sh 结束读取 `.admin-key` 并打印 Claude Code 接入命令（start-all.sh:61-76）。
- **F-266**: _lib.sh 的 require_vars 检查变量缺失或仍为 REPLACE_ME，缺失则列出并退出（_lib.sh:33-49）。
- **F-267**: wait_healthy 根据 Docker inspect 的 State.Health.Status 判断 healthy/unhealthy/none，支持超时与日志输出（_lib.sh:99-135）。
- **F-268**: memory-core 容器启动要求 MEMORY_CORE_IMAGE、MEMORY_CORE_PORT、MEMORY_CORE_VOLUME（start-memory-core.sh:16-18）。
- **F-269**: memory-core 容器名 tdai-memory-core（推断同名规则，容器名见 start-memory-core.sh），端口 ${MEMORY_CORE_PORT}:8420、卷 ${MEMORY_CORE_VOLUME}:/data/tdai-memory、配置只读挂载（start-memory-core.sh:203-219）。
- **F-270**: start-proxy.sh 中 PROXY_FULL_STACK=1 同时启用 auth、tdai、sessionInit 三个开关，否则各自默认关闭（start-proxy.sh:53-66）。
- **F-271**: proxy 容器名 tdai-proxy，端口 ${PROXY_PORT}:8096，配置只读挂载（start-proxy.sh:152-163）。
- **F-272**: .env.example 默认端口：MEMORY_CORE_PORT=8420、PANEL_PORT=8125、KNOWLEDGE_PORT=8424、PROXY_PORT=8096（.env.example:47-71）。
- **F-273**: .env.example 默认卷：MEMORY_CORE_VOLUME=tdai-memory-core-data、PANEL_VOLUME=tdai-panel-data（.env.example:47-71）。
- **F-274**: 部署结束打印的接入地址为 `ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default` 与 ANTHROPIC_AUTH_TOKEN（admin key）（start-all.sh:61-76）。
- **F-275**: admin key 存于 .admin-key 文件，sk-mem- 前缀自动生成（start-memory-core.sh:256-309）。
- **F-276**: KNOWLEDGE_SERVICE_KEY 留空时自动生成 ks-svc-*（deploy .env.example）。
- **F-277**: MEMORY_CORE_ADMIN_USERNAME 默认 admin（deploy .env.example）。
- **F-278**: 核心必填变量为两组 LLM 参数：MEMORY_LLM_* 与 PROXY_UPSTREAM_*（CHANGELOG.md:247；.env.example）。
- **F-279**: MEMORY_LLM_PROTOCOL 取值 openai|anthropic（.env.example）。
- **F-280**: hub 单独启动脚本 start-memory-hub.sh、core 单独启动 start-memory-core.sh、proxy 单独启动 start-proxy.sh（deploy/global-images/）。
- **F-281**: Docker 镜像为多架构（amd64/arm64），公开无需登录（CHANGELOG.md:240-242）。
- **F-282**: check_ports 在启动前做端口占用检查（信源：s-deploy，CHANGELOG.md:120）。
- **F-283**: MongoDB 一键入口 start-all-mongo.sh 位于部署目录（CHANGELOG.md:19）。
- **F-284**: docker-compose.local-mongo.yaml 与 tdai-gateway.local-mongo.yaml 支撑本地 Mongo 试验形态（MemoryCore/ 根）。
- **F-285**: MemoryKnowledge/docker/ 含 run.sh、smoke-test.sh、env.example（MemoryKnowledge/docker/）。
- **F-286**: README.docker.md 提供镜像使用说明（仓库根）。

## 十四、SDK、CI 与工程配套

- **F-287**: TypeScript SDK 包名 `@tencentdb-agent-memory/memory-sdk-ts-v2`（CHANGELOG.md:259；sdk/memory-core/typescript/package.json）。
- **F-288**: TS SDK v3 模块含 12 个文件：client、http、types、skill-client、skill-types、metadata-client、metadata-types、memory-prompt-client/types、memory-generation-log-client/types、index（sdk/memory-core/typescript/src/v3/）。
- **F-289**: TS SDK 顶级导出为 v3 严格 isolation 版本，`.../v2/v3` 子路径保留为向后兼容别名（CHANGELOG.md:262-271）。
- **F-290**: v3 客户端构造要求 endpoint、apiKey、serviceId、teamId、agentId、userId（后三项即 v3 严格 isolation 必填三元组）（CHANGELOG.md:264-267）。
- **F-291**: TS SDK 随附 README/README_CN、CHANGELOG、AGENT_GUIDE.typescript.zh-CN.md（sdk/memory-core/typescript/）。
- **F-292**: Python SDK 安装名 `tencentdb-agent-memory-sdk-python`（CHANGELOG.md:273；sdk/memory-core/python/pyproject.toml）。
- **F-293**: Python 包 tencentdb_agent_memory 顶层默认导出 v2 兼容 MemoryClient；v3 子包导出 MemoryClient、MetadataClient、SkillClient（CHANGELOG.md:276-278；sdk/memory-core/python/tencentdb_agent_memory/v3/）。
- **F-294**: Python v3 子包含 skill_client、metadata_client、memory_prompt、memory_generation_log、client 五个模块（sdk/memory-core/python/tencentdb_agent_memory/v3/）。
- **F-295**: Python SDK 通用层含 errors、cos、_v3_http、_http 四个基础模块（sdk/memory-core/python/tencentdb_agent_memory/）。
- **F-296**: Python SDK 随附 AGENT_GUIDE.python.zh-CN.md 与双语 README/CHANGELOG（sdk/memory-core/python/）。
- **F-297**: CI 工作流 .github/workflows/pr-ci.yml 在 PR 时触发（信源：s-ci）。
- **F-298**: 仓库 issue 模板分 bug_report、feature_request、question 三类，PR 模板为 PULL_REQUEST_TEMPLATE.md（.github/）。
- **F-299**: MemoryCore 测试使用 vitest（vitest.config.ts）；MemoryProxy 含 opencode 相关测试 2 个（__tests__/）；MemoryCore scripts 含 verify-clear-vs-archive.ts、verify-tcvdb-clear.ts、probe-vdb-capacity.ts、probe-vdb-reclaimable.ts、cleanup-vdb-test-dbs.ts 等运维验证脚本（信源：s-core-code、s-proxy-code）。
- **F-300**: 根目录含 .github/ISSUE_TEMPLATE、CONTRIBUTING(_CN).md、LICENSE；MemoryCore 含 tsdown.config.ts（打包）、vitest.config.ts；MemoryKnowledge 含 tsdown.config.ts、drizzle.config.ts（信源：s-repo 目录树）。

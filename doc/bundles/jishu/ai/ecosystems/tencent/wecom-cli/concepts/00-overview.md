---
type: concept
title: wecom-cli 总览：CLI 运行时与企业微信业务版图
description: 说明 wecom-cli 的交付形态、三层生态定位、安装方式与 13 个业务服务的覆盖范围。
tags: [wecom, wecom-cli, overview]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# wecom-cli 总览：CLI 运行时与企业微信业务版图

wecom-cli 是企业微信官方开源的命令行工具，覆盖消息、邮件、文档、在线表格、智能表格、智能文档、待办、日程、会议、微盘、通讯录等业务。它的特别之处不在于"命令多"，而在于**命令面并不固化在二进制里**：每个服务下有哪些方法、每个方法接受哪些参数，都由服务端下发的 schema 在运行时装配（见 F-072、F-073）。因此理解 wecom-cli，首先要理解它作为"Agent 可调用的业务运行时"这一定位，而不是一套静态的手册型 CLI。

## 一、交付形态：Rust 工作区 + npm 分发

源码是一个包含 5 个 crate 的 Rust workspace（见 F-001、F-002）：`wecom`（库）、`wecom-cli`（二进制）、`wecom-transport`（HTTP/协议层）、`wecom-fs`（文件与沙箱）、`wecom-error`（统一错误）。对外发布则走 npm：包名 `@wecom/cli`，版本 1.3.4（见 F-009），`bin` 指向 `./bin/wecom.js`（见 F-017），并配套 5 个平台子包分别携带 macOS x64/arm64、Linux x64/arm64、Windows x64 的二进制（见 F-015、F-010）。许可证为 MIT（见 F-032）。

这种"Rust 二进制 + npm 壳"的组合带来两个直接后果：

- 安装端只需要 Node.js ≥ 18（见 F-162），运行时并不依赖 Node 业务代码，Node 只负责定位并拉起对应平台的二进制；
- 升级以 npm 包版本为准，CLI 自身版本与 npm 包版本同源，`wecom-cli --version` 可作为现场核对手段（见 F-042）。

## 二、三层定位：CLI、Skill 与 SDK

在企业微信的 Agent 生态里，wecom-cli 位于"能力执行层"。它与上下两层的关系可以用下表概括：

| 层次 | 载体 | 与本仓库的关系 | 依据 |
|---|---|---|---|
| CLI 运行时 | `@wecom/cli` 1.3.4 + 5 个平台二进制包 | 本仓库的主体产物，负责鉴权、协议、沙箱与业务调用 | F-009、F-015 |
| Skill 层 | `skills/wecomcli-*` 共 15 个 `SKILL.md` | 以 Markdown 契约描述"何时调用、如何调用"，并通过 `metadata.requires.bins: ["wecom-cli"]` 声明对二进制的依赖；Skill 不内嵌 CLI | F-137、F-139 |
| SDK 层 | 同生态的 `wecom-aibot-python-sdk`（跨仓库） | 面向同一企业微信开放能力的另一种客户端形态，**不是**本仓库的依赖；本仓库没有 Python 构建入口，Python 只出现在 6 个技能辅助脚本中 | F-144、F-145、F-148 |

需要区分两个容易混淆的"Skill 层"：本仓库自带 15 个 `wecomcli-*` 技能，是"按业务域拆分"的官方技能包；同生态的 `wecom-unified` 则是另一套以 Markdown 契约加脚本、经 Bash 调用 `wecom-cli` 的统一技能包（属跨仓库观察，不在本包事实登记范围内）。两者的共同点是**都把 wecom-cli 当作能力后端**，差别只在技能的组织粒度。

至于"Claude Code 的 CLI 运行时"这一说法，更准确的理解是：wecom-cli 面向任何能执行 shell 的 Agent 宿主，Claude Code 只是其中一种典型宿主。本仓库自身只承诺 Agent Skills 形态，安装指引为 `npx skills add WeComTeam/wecom-cli -y -g`（见 F-162），并未在文档中枚举宿主兼容矩阵。

## 三、安装与首次配置

标准路径是三步（见 F-162）：

1. `npm install -g @wecom/cli` 安装 CLI；
2. `npx skills add WeComTeam/wecom-cli -y -g` 安装配套技能（README 标注为必需）；
3. `wecom-cli auth init` 完成一次性授权，默认扫码，也可用 `--manual` 手动录入（见 F-096）。

授权态可用 `wecom-cli auth show` 查看，加 `--status` 进入脚本模式并只输出 JSON（见 F-049）。平台支持范围为 macOS（x64/arm64）、Linux（x64/arm64）、Windows（x64）（见 F-162）；企业微信账号是硬前置，智能机器人的 Bot ID 与 Secret 则是可选项（见 F-162）。

## 四、13 个业务服务速览

根命令下挂 13 个服务（见 F-047）。它们的命令形态统一为 `wecom-cli <service> [resource...] <method> [flags]`（见 F-046），差异主要体现在业务语义上：

| 服务 | 业务品类 | 能力摘要 |
|---|---|---|
| `message` | 消息 | 向机器人最近对话过的单聊/群聊推送 Markdown、图片、文件、语音、视频消息 |
| `mail` | 邮件 | 邮件搜索与内容读取 |
| `doc` | 文档 | 在线文档新建、导入、读取、追加与覆盖写入 |
| `sheet` | 在线表格 | 新建、CSV/Excel 导入、内容读改、追加行与子表管理 |
| `smartsheet` | 智能表格 | 子表、字段、记录、视图、图表与行列样式管理 |
| `smartpage` | 智能文档 | 创建、读取页面内容、编辑内容与数据表信息 |
| `calendar` | 日程 | 日程增删改查、参与人管理、闲忙查询、会议室查询与预订 |
| `meeting` | 会议 | 预约与取消会议、更新参会人、列表与详情、纪要与转写原文 |
| `todo` | 待办 | 创建、读取、更新、删除待办，分派参与人与完成待办 |
| `disk` | 微盘 | 文件搜索、基础信息读取、上传与下载 |
| `contact` | 通讯录 | 按姓名、拼音、别名搜索成员并获取基本信息 |
| `media` | 媒体 | 媒体文件上传与下载 |
| `identity` | 身份 | 身份相关信息查询（技能层未展开说明） |

表中服务名来自根命令注册清单（见 F-047），能力摘要对应 README 的功能范围与技能说明。`media` 与 `identity` 没有独立技能文档展开，使用前建议先以 `wecom-cli <service> --help` 查看运行时 schema。

## 五、运行时必须知道的三个约束

第一，**帮助与调用都依赖在线 schema**。文档明确说明 `--help` 与 `--doc` 需要网络与凭证（唯一的例外是构建时启用 `--no-default-features` 后 `--doc`/`--schema` 可离线，见 F-136），因此"断网看手册"并不可靠。第二，**输出与日志分流**：正常结果写 stdout，日志与诊断写 stderr，便于 Agent 直接解析。第三，**schema 缓存以磁盘文件为准、新鲜期为 60 秒**（见 F-068、F-069），缓存位于 `<config_dir>/cache`（见 F-064），因此同一台机器上的不同进程可以共享，但服务端 schema 变更最多需要 60 秒才被感知。

## 六、延伸阅读

- 命令如何被解析与装配：[/concepts/01-command-model.md](/concepts/01-command-model.md)
- 5 个 crate 的职责与依赖方向：[/concepts/02-crate-architecture.md](/concepts/02-crate-architecture.md)
- 授权与凭据生命周期：[/concepts/03-auth-session.md](/concepts/03-auth-session.md)
- 传输、轮询与断点续传：[/concepts/04-transport-resilience.md](/concepts/04-transport-resilience.md)
- 文件沙箱与安全边界：[/concepts/05-sandbox-security.md](/concepts/05-sandbox-security.md)
- 15 个技能的组织方式：[/concepts/06-skills-layer.md](/concepts/06-skills-layer.md)
- 文档、测试与发布流程：[/concepts/07-development-release.md](/concepts/07-development-release.md)
---
type: concept
title: 团队 Skill+CLI 集成：AK/SK 签发成员 token 与 CI 直发
description: 接入方团队把 Meoo 能力接入自有 Agent/CI 的完整六步——两种接入方式选型、接入资源与三个权限点、HMAC 签发成员短期 token 的接口报文、tgz 安装与 meoo skill install 目录检测、MEOO_TOKEN/MEOO_API_URL 注入、项目操作与 CI 直发命令，以及 token 生命周期四阶段管理
tags: [meoo, miaowu, cli, open-api, hmac, token, ci, skill, integration]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: cli-open-guide
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入
  - id: open
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台
---

# 团队 Skill+CLI 集成：AK/SK 签发成员 token 与 CI 直发

> 本篇面向**接入方团队**（把秒悟能力集成进自己 Agent/CI 的一方），不是个人用户。个人安装与浏览器登录见 [02](02-cli-install-login.md)。开放平台身份模式的全景见 [00](00-open-platform-overview.md)。

## 1. 先选型：Skill+CLI 还是 OpenAPI 自行封装

| 对比项 | 用 Meoo Skill + CLI（本篇） | 基于 OpenAPI 自行封装 |
|---|---|---|
| Meoo 提供什么 | 配套 Skill、CLI、项目模板和操作命令 | 云服务 OpenAPI 和项目导入 API |
| 接入方做什么 | 装 Skill 和 CLI，签发临时 token，经 MEOO_TOKEN 注入 | 封装 Agent 工具，定义参数与结果处理，自生成项目结构并组织调用 |
| Agent 如何使用 | 读官方 Skill，按指引选 CLI 命令执行 | 读接入方自建的工具说明，调自建工具 |
| 项目如何组织 | 用 CLI 项目模板，按 Skill 指引组织代码、用云服务、同步发布 | 自行生成符合运行要求的项目结构，经 OpenAPI 配能力、经导入 API 接入 |
| 适合诉求 | 快速让已有 Agent 复用官方工具与指引 | 自行设计 Agent 工具、项目结构和开发流程 |

表格五行逐字来源 F-043。本篇只覆盖左列路径。

**接入主流程四步**（F-042，源页加粗）：

```text
安装 Meoo Skill + CLI → 用团队 AK/SK 签发临时 token → 注入 MEOO_TOKEN → Agent 执行任务
```

## 2. 准备五类接入资源

| 准备项 | 配置要点 |
|---|---|
| 开放团队与 AK/SK | 在开放版管理后台创建团队 API 凭证；**由接入方服务端保存 AK/SK 并完成请求签名**（F-044） |
| 成员身份 | 联调可用团队 Owner；面向业务用户时，建立业务用户与虚拟成员 `member_id` 的映射（F-044） |
| 凭证权限 | AK/SK 配 `team.member.token.issue`；查询成员配 `team.member.read`；可委托权限包含 `cli.compat`（F-045，三个权限点逐字） |
| 运行环境 | **Node.js 18 或以上**，安装支持 MEOO_TOKEN 的 CLI 接入版本；Agent 具备终端执行能力及 Skill 加载能力（F-046） |
| 服务地址 | 生产 `https://meoo.com`；联调用对应环境地址及**该环境签发的凭证**（F-047） |

> Node 版本第三处口径：这里的 18+ 是**集成运行环境**要求，区别于本机个人安装的 Node 20+（F-005）与云端构建镜像的 24.15.0（F-024），见 [verification.md](../references/verification.md) 核验项二。

**红线提醒（2026-10 时点）**：团队 AK/SK 暂未开放自助创建入口，现阶段需联系秒悟团队人工创建并提供团队账号，Secret 仅创建时交付一次（F-037）⚠️ dated；集成权益仅建议开发预发联调（F-036）。

## 3. 第一步：用 AK/SK 签发成员 token

在**接入方服务端**，按团队 AK/SK 的 HMAC 签名协议调用成员 token 接口（F-048，报文逐字）：

```http
POST /open/v1/team/members/{member_id}/tokens
Content-Type: application/json

{
  "scopes": ["cli.compat"],
  "expires_in": 900
}
```

要点（F-048、F-049）：

- `member_id` 选本次任务对应的团队成员（Owner 或虚拟成员）；
- `expires_in` 是有效期**秒数**，示例为 900（15 分钟）；按任务时长设置，并满足团队凭证允许的有效期范围；
- 签发请求用团队 AK/SK 做 HMAC 签名（具体签名算法在未抓取的「团队系统集成」页，见台账放弃核验清单，本篇不补造）；
- 从响应取 `access_token` 和 `expires_in`，接入方记录到期时间；
- CLI 以该成员身份执行操作，项目访问范围由成员所属团队、角色和资源权限共同确定。

> 架构洞察：AK/SK（长期、服务端、只签发）与成员 token（短期、任务环境、可业务操作）构成双层凭证。`scopes: ["cli.compat"]` 把 token 能力收窄到 CLI 兼容面，即使任务环境泄露，爆炸半径也受 scope 与 900 秒有效期双重限制（呼应 F-033：AK/SK 不能直调业务 API）。

## 4. 第二步：安装 CLI 接入版与配套 Skill

在 Agent 或 CI 运行环境中，用平台提供的 tgz 安装包安装（路径替换为实际路径，F-050，逐字）：

```bash
npm install -g "/path/to/meoo-cli.tgz"
meoo --version
meoo skill install
```

Skill 随 CLI 安装包提供。`meoo skill install` 会自动检测五款 Agent 的已有配置目录：**Claude Code、Cursor、Trae、CodeBuddy、Qoder**（F-051）。

自有/未列入的 Agent，用 `--target` 装到它实际加载的目录（F-051，逐字）：

```bash
meoo skill install --target /path/to/agent/skills/meoo-cli
```

目标目录是 meoo-cli Skill 文件夹本身，内含 `SKILL.md` 和 `references/`；需把该目录配置进 Agent 的 Skill 加载路径。**升级 CLI 后要再次执行安装命令**以同步配套指引（F-052）。

## 5. 第三步：注入 token，让 Agent 执行命令

把 `access_token` 设为 `MEOO_TOKEN`，目标环境地址设为 `MEOO_API_URL`（F-053，逐字）：

```bash
export MEOO_TOKEN="<access_token>"
export MEOO_API_URL="https://meoo.com"
```

实际接入时由接入方服务端、Secret 管理或任务调度器把变量注入 Agent 的命令执行进程——Agent 启动的 CLI 子进程继承这些变量（F-053）。**多业务用户并发时，按任务分别传入各自成员的 token**（F-058）。

先做身份与项目核验（F-054，逐字）：

```bash
meoo --json whoami
meoo --json projects list
```

随后在本地应用目录中，以实际项目 urlId 执行项目操作（F-055，逐字）：

```bash
meoo projects use "<项目 urlId>"
meoo cloud status
meoo sandbox push
meoo deploy
```

四条依次为：选择项目 → 查看云服务状态 → 同步本地源码 → 构建发布。`--json` 可获取结构化结果，便于 Agent 把操作状态、错误信息及产出反馈给用户（F-054、F-055）。

### CI 场景：已有构建产物时直发

CI 已完成静态构建时，跳过构建与推送直接发布（F-056，逐字）：

```bash
meoo --json deploy --project "<项目 urlId>" --skip-build --skip-push --force
```

使用前提源页写得很硬：**执行前完成构建并核对项目**；`--force` 用于自动化任务中的确认步骤（F-056）。不要在交互场景养成加 `--force` 的习惯——它的存在就是替人确认，人不在场才需要它。

## 6. 第四步：token 生命周期四阶段

| 任务阶段 | 接入方处理（F-057） |
|---|---|
| 任务启动 | 按业务用户确定 member_id，签发或复用有效 token，注入执行进程 |
| token 临近到期 | 用团队 AK/SK 为同一成员重新签发；运行中的 Agent 通过执行器更新**后续子进程**的环境 |
| 身份或权限错误 | 依次检查：目标环境、token 到期时间、`cli.compat` 权限、成员状态、目标项目权限；修正后重新调用 |
| 任务完成 | 回收任务环境中的 token，保留任务结果及**经过脱敏**的操作记录 |

凭证三层落点（F-058）：**AK/SK 只在接入方服务端或密钥管理系统；成员 token 只经任务环境传递；Skill 只描述操作流程、不持有凭证。**

## 7. 安全红线汇总（接入前自查）

1. 长期凭证只能存可信服务端——**不入浏览器、移动端、代码仓库、构建产物**（F-038）；
2. 测试与生产的账号、凭证、项目不得混用（F-041）；地址与凭证要同环境成对（F-047）；
3. token 按任务、按成员签发，不跨用户复用（F-058）；
4. 任务结束回收 token、脱敏日志（F-057）；
5. OAuth 应用不能自行注册，需联系 Meoo 取 `client_id`/Client Secret（F-040）。

## 8. 坑点与边界

- **把 AK/SK 当 API Key 用**：它不能直接调项目/Agent/Release（F-033），必须先换 token。
- **token 过期后只改全局环境变量**：运行中的 Agent 要靠执行器更新后续子进程环境（F-057），已启动的旧进程不会自动获得新值。
- **权限点配齐三缺一**：签发要 `team.member.token.issue`、查成员要 `team.member.read`、委托面要含 `cli.compat`（F-045）。
- **把 Skill 装到 Agent 不加载的目录**：五款之外的 Agent 必须用 `--target` 并自行配置加载路径（F-051、F-052）。
- **CI 未构建先发布**：`--skip-build` 依赖已有产物，顺序不能反（F-056）。
- 采集稿中 `team.member.read`、`SKILL.md` 曾被转换器渲染成占位外链，均非真实 URL（见台账「转写噪声登记」）。

## 9. 延伸阅读

- [00 开放平台总览](00-open-platform-overview.md)
- [02 个人安装与浏览器登录](02-cli-install-login.md)（对照两种身份）
- 完整报文与 CI 命令流：[examples/03 团队 token 与 CI 发布](../examples/03-team-token-ci-publish.md)

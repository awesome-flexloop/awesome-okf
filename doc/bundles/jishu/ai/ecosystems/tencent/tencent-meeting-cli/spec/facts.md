---
type: spec-facts
title: 腾讯会议 CLI（tmeet）事实清单
status: stable
generated: { by: reference_agent/trae-solo, at: 2026-10-03T00:00:00Z }
sources:
  - id: s-page
    resource: https://meeting.tencent.com/meeting-cli/index.html
    title: 腾讯会议 CLI 产品首页
  - id: s-install
    resource: https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web
    title: 腾讯会议 CLI 安装指南（面向 AI Agent）
  - id: s-readme
    resource: https://github.com/TencentCloud/tencentmeeting-cli
    title: tencentmeeting-cli GitHub README（main 分支）
  - id: s-cloud
    resource: https://cloud.tencent.com/document/product/1095/133827
    title: 腾讯云文档中心《腾讯会议 CLI 说明》（页面更新时间 2026-07-08）
  - id: s-command
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/docs/command.md
    title: 官方完整命令参考 docs/command.md（1594 行）
  - id: s-skill
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/skills/tmeet-skill/SKILL.md
    title: CLI-SKILL 清单 tmeet-skill/SKILL.md（version 1.0.18，约 34KB）
  - id: s-pkg
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/package.json
    title: npm 包清单 package.json
  - id: s-changelog
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/CHANGELOG.md
    title: 项目变更日志 CHANGELOG.md（Keep a Changelog 约定）
---

# 腾讯会议 CLI（tmeet）Facts

> 本文件登记从 8 个官方公开信源提取的 72 条编号事实，抓取日期 2026-10-03。每条事实标注信源编号，作为本知识包唯一事实来源；信源间口径差异以「⚠️ 口径」条目并列登记，不做裁决式删改。

## 一、产品定位与分发

- **F-001**: 产品名称为「腾讯会议 CLI」，命令行入口为 `tmeet`，npm 包名为 `@tencentcloud/tmeet`（信源：s-readme、s-pkg）。
- **F-002**: 产品首页标语为「一行指令，让 AI 为你管理腾讯会议」，定位为让 AI 直接管理会议、覆盖会议核心业务域的命令行工具（信源：s-page）。
- **F-003**: 仓库地址为 https://github.com/TencentCloud/tencentmeeting-cli ，基于 MIT License 开源，README 徽章标注 Go 1.22+（信源：s-readme）。
- **F-004**: 腾讯云文档将其定义为「腾讯会议官方推出的命令行工具」，核心作用是充当 AI Agent 的执行抓手：AI Agent 依托配套 CLI-Skill 完成命令调用，用户输入自然语言指令，由 AI 代为完成腾讯会议操作（信源：s-cloud）。
- **F-005**: 首页列出的兼容 AI Agent 工具包括 WorkBuddy、DeepSeek Harness、Claude Code、Codex、Cursor、GitHub Copilot（信源：s-page）。
- **F-006**: 首页 FAQ 称 CLI-Skill 可与 Claude Code、Cursor、Codex、OpenClaw 等 AI 工具集成（信源：s-page）。
- **F-007**: 首页面向真实业务场景列出三类：教育培训（批量排课、课程整理、错题溯源）、销售面客（会前对齐要点、会后复盘）、办公协作（会议冲突检查、会议章程管理、纪要待办整理）（信源：s-page）。
- **F-008**: npm 包 `package.json` 声明 `version: v1.0.18`、`bin.tmeet` 指向 `./scripts/tmeet.js`、含 `postinstall` 钩子 `node scripts/cleanup.js`、发布文件仅含 `scripts/` 与 `dist/`（信源：s-pkg）。
- **F-009**: 2026-09-11 发布的 v1.0.18 是 CHANGELOG 中最新版本；其上一版本 v1.0.17 发布于 2026-09-09（信源：s-changelog）。
- **F-010**: CHANGELOG 遵循 Keep a Changelog 约定，按 Added/Changed/Fixed 分段记录变更（信源：s-changelog）。

## 二、安装与环境要求

- **F-011**: 推荐安装命令为 `npm install -g @tencentcloud/tmeet`（信源：s-readme、s-cloud、s-page）。
- **F-012**: 安装指南要求在安装 CLI 后再安装配套 Skill：`npx skills add TencentCloud/tencentmeeting-cli -y -g`，并标注该 Skill 为「必需」（信源：s-install）。
- **F-013**: 安装指南给出的环境要求为 Node.js >= 14（信源：s-install）。
- **F-014**: `package.json` 的 `engines` 字段声明 `"node": ">=14"`（信源：s-pkg）。
- **F-015**: ⚠️ 口径：腾讯云文档「功能说明」节写「本地依赖：Node.js ≥ 16」，与安装指南及 package.json 的 `>=14` 不一致（信源：s-cloud vs s-install/s-pkg）。
- **F-016**: 首页 FAQ 对 `npm: command not found` 的解答为前往 Node.js 官网安装 LTS 版本（已含 npm），并检查 npm 全局 bin 目录在 PATH 中、安装后重启终端（信源：s-page）。
- **F-017**: 支持从源码构建：`git clone` 后执行 `go build -ldflags "-X tmeet/cmd.Version=v1.0.0" -o tmeet .` 或 `make build VERSION=v1.0.0`（信源：s-readme、s-cloud）。
- **F-018**: 跨平台支持 macOS、Linux、Windows（信源：s-readme、s-page）。
- **F-019**: 安装指南第 3 步要求「配置完成后重启 AI 工具，以确保 SKILL 完整加载」，再运行 `tmeet auth status` 验证（信源：s-install）。
- **F-020**: 安装指南提供了可直接复制给 AI 助手的一句话提示词：「帮我安装腾讯会议CLI，链接地址：https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web 」（信源：s-page、s-install）。

## 三、OAuth2 授权与凭证安全

- **F-021**: 授权命令为 `tmeet auth login`，采用设备码 OAuth2 授权流程，无密码；CLI 自动打开系统默认浏览器跳转授权 URL 并轮询结果，轮询超时时间为 5 分钟（信源：s-readme、s-cloud）。
- **F-022**: `tmeet auth login --no-browser` 可禁用自动打开浏览器，仅输出授权 URL 由用户手动打开（信源：s-readme、s-cloud）。
- **F-023**: SKILL.md 声明 `auth login` 是阻塞命令，会阻塞等待最多 300s，要求必须前台运行，不要用后台方式（`&`）运行，否则凭证可能写入失败（信源：s-skill）。
- **F-024**: 凭证使用 AES-256-GCM 加密保存到本地，明文不落盘（信源：s-readme、s-page）。
- **F-025**: 腾讯云文档描述凭证「存入系统 Keychain，与设备绑定，无法在另一台机器上解密」（信源：s-cloud）。
- **F-026**: `tmeet auth status` 可查看登录状态，输出包括 OpenId、AccessToken/RefreshToken 的过期状态与剩余有效时间；未登录时提示 `Not logged in`（信源：s-command）。
- **F-027**: `tmeet auth logout` 登出并清除本地认证凭证，无参数（信源：s-command）。
- **F-028**: 配置文件默认存储在 `~/.tmeet/` 目录；可用环境变量 `TMEET_CLI_CONFIG_DIR`（配置目录，默认 `~/.tmeet/`）与 `TMEET_CLI_DATA_DIR`（加密数据目录，平台相关默认路径）覆盖（信源：s-readme）。
- **F-029**: SKILL.md 规定除 `auth login`、`auth status` 与 `event list`/`event schema`/`event status`/`event stop` 外，所有命令都需要先登录；未登录时提示 `user config is empty`（信源：s-skill、s-cloud）。
- **F-030**: 安全建议包括：不要把 `~/.tmeet/` 目录或系统 Keychain 数据作为构建产物传递/归档/上传到代码仓库；不要在命令行参数或脚本注释中硬编码账号信息；不要截图或复制凭证文件到 AI 对话框（信源：s-cloud）。
- **F-031**: 怀疑凭证泄露时的处置为立即执行 `tmeet auth logout` 清除本地凭证，并在腾讯会议账号安全中心吊销授权（信源：s-cloud、s-readme）。
- **F-032**: v1.0.18 将凭证清理改为「先释放资源再清凭证」两阶段流程：`ClearUserConfig` 先按注册顺序 fail-fast 执行全部 ResourceReleaseHook，全部成功后才删 Keychain 与 active_open_id；任一 hook 失败则保留凭证供重试（信源：s-changelog）。

## 四、命令体系总览

- **F-033**: README 命令树包含 10 个一级命令域：`auth`、`meeting`、`contact`、`record`、`report`、`control`、`minutes`、`tshoot`、`app`、`event`（另有根命令级全局标志）；按 command.md 登记的子命令数为：auth 3、meeting 11、contact 3、record 9、report 4、control 3、minutes 2、tshoot 2、app 2、event 5，合计 44 个子命令（信源：s-readme、s-command）。
- **F-034**: ⚠️ 口径：腾讯云文档（页面更新时间 2026-07-08）「工具清单」节称「腾讯会议 CLI 暴露了 19 个命令」，并按授权管理 3、会议管理 7、录制管理 6、参会报告 2、问题排查 1 列示；该清单不含 contact/control/minutes/app/event 等命令域（信源：s-cloud）。
- **F-035**: 全局标志有三个：`--format`（`json` 紧凑默认 / `json-pretty` 缩进）、`--compact`（精简输出，仅保留关键字段，默认 false）、`--version`/`-V`（查看版本号）（信源：s-readme、s-command）。
- **F-036**: 除 event 子命令族外，响应统一为 `{trace_id, message, data}` 信封结构（信源：s-skill）。
- **F-037**: event 子命令族输出 bare JSON，不带 `{trace_id, message, data}` 信封，也不经过 compact 中间件，`--compact` 对其无效（信源：s-skill、s-changelog）。
- **F-038**: 所有时间参数使用 ISO 8601 格式（如 `2026-04-10T14:00+08:00`），不支持仅日期格式；响应中的时间戳字段自动转换为 ISO 8601 展示（信源：s-readme、s-skill）。
- **F-039**: 自 v1.0.5 起，所有支持分页的命令统一采用 `--page-token` + `--page-size` 游标方案；原 `--page`/`--pos`/`--size` 标记为 deprecated，仍可使用（信源：s-readme、s-command）。
- **F-040**: 常见报错表登记 4 条：`user config is empty`（未登录）、`--start format error`（时间格式不合法缺时区）、`--meeting-id is required`（缺必填参数）、`user has been initialized`（重复 login）（信源：s-cloud）。

## 五、会议管理域（meeting）

- **F-041**: `meeting create` 必填参数为 `--subject`、`--start`、`--end`；可选参数包括 `--password`（4~6 位数字）、`--timezone`（Oracle-TimeZone 标准如 `Asia/Shanghai`）、`--meeting-type`（0 普通/1 周期性，默认 0）、`--join-type`（1 所有人/2 仅受邀/3 仅企业内部，默认 0）、`--waiting-room`（默认 false）（信源：s-command）。
- **F-042**: 周期性会议参数：`--recurring-type`（0 每天/1 周一至周五/2 每周/3 每两周/4 每月）、`--until-type`（0 按日期/1 按次数结束）、`--until-count`（默认 7；每天/工作日/每周最大 500，每两周/每月最大 50）、`--until-date`（信源：s-command）。
- **F-043**: `meeting create --invitees` 接收 openid 列表，逗号分隔或重复传参，最多 100 人（信源：s-command）。
- **F-044**: 高级会议参数含 `--water-mark-type`（文字水印 0 单排/1 双排/2 关闭，个人账号默认 2）、`--audio-watermark`（默认 false）、`--auto-record-type`（none/local/cloud，默认 none）、`--auto-asr`（默认 false）；企业账号场景下企业强制态设置优先于入参（信源：s-command）。
- **F-045**: bool 参数显式传 false 必须使用等号形式（如 `--audio-watermark=false`），不能用空格形式（信源：s-command）。
- **F-046**: `meeting get` 的 `--meeting-id` 与 `--meeting-code` 二选一，meeting-id 优先级更高（信源：s-command）。
- **F-047**: `meeting update` 仅传入需要修改的字段，未传字段保持不变；`--sub-meeting-id` 仅修改周期会议中单场子会议时间，且不可与 `--recurring-type`/`--until-type`/`--until-count`/`--until-date` 同时使用（信源：s-command）。
- **F-048**: `meeting update` 可通过 `--invitees` + `--invitees-type`（replace/add/remove）变更邀请列表；指定 `--invitees` 时 `--invitees-type` 必填（信源：s-command）。
- **F-049**: `meeting cancel` 取消普通会议传 `--meeting-id`；取消周期会议某一子会议加 `--sub-meeting-id`；取消整场周期会议传 `--meeting-type 1`（信源：s-command）。
- **F-050**: `meeting list` 查询进行中/即将开始的会议，`--page-size` 默认与最大均为 20；支持 `--show-all-sub 1` 展示全部子会议；`--start`/`--end` 为分页查询时间值（信源：s-command）。
- **F-051**: `meeting list-ended` 按时间范围查询已结束会议，`--page-size` 默认与最大均为 30（信源：s-command）。
- **F-052**: `meeting search` 支持 `--query` 关键词、`--query-field`（subject/creator/note/all，默认 all）、`--meeting-code`（仅数字无短横线精确匹配）、`--start`/`--end` 时间窗组合过滤（信源：s-command）。
- **F-053**: 受邀成员管理有 4 个独立子命令：`invitees-list`、`invitees-add`、`invitees-remove`、`invitees-replace`；后三者 `--invitees` 为必填，最多 100 个 openid（信源：s-command）。

## 六、录制、转写与纪要域（record / minutes）

- **F-054**: `record list` 的过滤参数三选一：`--start`+`--end` 时间范围、`--meeting-id`、`--meeting-code`；均不传则报错（信源：s-command）。
- **F-055**: `record address` 用 `--meeting-record-id` 获取录制文件下载地址与 record_file_id（信源：s-command）。
- **F-056**: `record search` 的 `--query-field` 支持 subject、creator、transcript_content（原始转写）、smart_minutes（智能纪要内容）、timeline（时间轴）、all；`--file-type` 支持 video/audio/transcript/upload/external/all（信源：s-command）。
- **F-057**: `record smart-minutes` 用 `--record-file-id` 获取智能纪要，`--lang` 支持 default（原文）/zh/en/ja，`--pwd` 为录制文件访问密码（信源：s-command）。
- **F-058**: 转写三命令：`transcript-get`（转写详情，`--pid` 起始段落 ID + `--limit` 段落数为独立定位参数，非通用分页）、`transcript-paragraphs`（段落列表）、`transcript-search`（按 `--text` 搜关键词）（信源：s-command、s-readme）。
- **F-059**: 录制权限申请为两阶段命令：`permission-apply-prepare` 预览审批文案/会议主题/录制所有者/申请人等信息（响应含 `expires_in` 过期秒数），用户确认后再执行 `permission-apply-commit` 提交，返回 `unique_id`/`status`/`approval_url` 等（信源：s-command）。
- **F-060**: 元宝纪要（minutes）有两个子命令：`minutes search`（关键词最多 50 字 + 时间范围，page-size 默认 20 最大 50）与 `minutes get`（`--minute-id` 与 `--meeting-id` 二选一，周期会议加 `--sub-meeting-id`）（信源：s-command）。
- **F-061**: `minutes get` 可选内容开关：`--overview`（默认 true）、`--summary-points`（默认 true）、`--todos`（默认 true）、`--short-summary`（滚动总结历史序列，默认 false）；page-size 默认 10 最大 30（信源：s-command）。
- **F-062**: SKILL.md 定义一场会议存在两类独立纪要：元宝纪要（基于会中 ASR、参会者人人可取无需权限、无逐字稿）与录制纪要（基于录制文件、创建者所有、需权限、有逐字稿）（信源：s-skill）。
- **F-063**: SKILL.md 规定已知会议取纪要先 `meeting get` 拿 `permission_status`：`can_view` 走 `record smart-minutes`；`can_apply`/`closed`/无录制走 `minutes get`；录制侧取不到时降级 `minutes get` 并告知用户（信源：s-skill）。
- **F-064**: 跨会议检索纪要内容时要求 `minutes search --query` 与 `record search --query-field transcript_content` 两条都执行，按会议去重并每条标注来源（信源：s-skill）。

## 七、通讯录、参会报告与会中控制

- **F-065**: `contact search` 按 `--username` 搜索企业通讯录成员，可用 `--job-title`、`--department-name` 过滤；另有 `lookup-by-email`（最多 50 个邮箱）与 `lookup-by-phone`（最多 50 个手机号）批量反查（信源：s-command）。
- **F-066**: SKILL.md 对通讯录命令设场景白名单：仅可用于「会议邀请」（invitees-add/replace）与「呼叫成员入会」（control call）两类前置解析；严禁单独用于查询任何人的姓名/部门/职位/联系方式/是否存在，无下游会议动作时一律拒绝（信源：s-skill）。
- **F-067**: `report participants` 查参会人列表（含入会/离会时间），page-size 默认/最大 100；`report waiting-room-log` 查等候室成员记录，page-size 默认/最大 100（信源：s-command、s-cloud）。
- **F-068**: `report participants-export` 为异步导出（xlsx 默认或 json），仅返回 `job_id`；需每 5 秒调用 `report job-result --job-id` 轮询，status 为「成功」时获取下载链接（有效期 2 小时），「处理中」继续等待，「失败」返回 error_msg（信源：s-command）。
- **F-069**: `control call` 会中呼叫成员入会，`--users` 最多 20 个 openid（信源：s-command）。
- **F-070**: `control waiting-room` 支持三种 `--operate-type`：enter-meeting（移入会议）、back-to-waiting（移回等候室）、expel（移出）；成员参数 `--users`/`--sip-users`/`--pstn-users` 三选一至少一种，合计最多 20 个；expel 时可用 `--allow-rejoin` 控制是否允许重新加入（信源：s-command）。
- **F-071**: `control kick` 踢出成员，三类成员参数合计最多 20 个；`--allow-rejoin` 默认 true；SKILL.md 硬约束踢人来源必须取自 `report participants` 返回的会中参会人，严禁使用 `contact search` 结果（信源：s-command、s-skill）。

## 八、Agent 行为契约（CLI-SKILL）

- **F-072**: 二次确认命令清单含 9 个：`meeting cancel`、`meeting update`、`meeting invitees-add`、`meeting invitees-remove`、`meeting invitees-replace`、`control call`、`control kick`、`auth logout`、`record permission-apply-commit`（信源：s-skill）。
- **F-073**: 确认流程为：先展示操作详情（用 meeting_code 标识会议）→ 结束本轮回复等待用户下一条真实输入 → 收到「确认/是/yes」后执行；自问自答、虚构用户指令、默认代选三种做法被明确列为违规（信源：s-skill）。
- **F-074**: 隐私字段规则：严禁向用户暴露 `meeting_id`，所有面向用户的展示统一使用 `meeting_code`（会议号）；meeting_id 仅用于命令行参数传递（信源：s-skill）。
- **F-075**: 成员回显硬约束：每名成员按 `姓名（<标识>）` 格式输出，姓名优先级为显示名字段 → 用户输入的搜索关键词 → 「未知成员」；括号标识按 部门 > 职位 > open_id 取一项（信源：s-skill）。
- **F-076**: 多候选结果必须由用户确认，禁止模型基于职位/部门/匹配度自行选择；必填参数缺失必须向用户询问，禁止自行填充默认值（信源：s-skill）。
- **F-077**: 查询类命令默认追加 `--compact` 降低上下文 token；`--compact` 中间件按命令的 API 注解从远端拉取精简字段列表，未声明注解或拉取失败时透明放行（信源：s-skill）。
- **F-078**: 翻页准则要求不得自行拼接/递增 page-token；非穷尽式诉求下每页后先询问用户是否继续；连续翻页超 5 页或累计超 200 条须主动征询（信源：s-skill）。

## 九、事件订阅与应用信息（v1.0.17 / v1.0.18 新增）

- **F-079**: v1.0.18 新增 `event` 命令组，基于 per-host bus 守护进程：所有 `event consume` 消费者复用同一条 WSS 长连接，由 bus 统一管理握手/心跳/自动重连，事件以 NDJSON 写 stdout、诊断信息写 stderr（信源：s-changelog、s-command）。
- **F-080**: `event consume` 支持批处理（`--max-events` N 条后退出 / `--timeout` 如 30s、5m）与常驻（两者不传，SIGINT/SIGTERM 或 `event stop` 退出）两种模式；支持 `--param key=value` 过滤、`--jq` gojq 投影、`--output-dir` 事件落盘（仅相对路径、拒绝 `..`）、`--quiet`（信源：s-command）。
- **F-081**: ready 标记为 stderr 输出 `[event] ready event_key=<key>`，`--quiet` 也不屏蔽；退出标记含 reason（limit/timeout/signal/shutdown）；退出码约定 0 正常、1 致命错误、2 仅 status --fail-on-orphan 与 stop 在 refused/errored 时返回（信源：s-command）。
- **F-082**: bus 状态有 running / stale_owner（绑定其他用户或未登录）/ orphan（进程已死残留 pid/meta 文件）；`event status --fail-on-orphan` 在异常态返回退出码 2；`event stop --force` 可清理残留，且被 SKILL 列为需二次确认的写操作（信源：s-command、s-skill）。
- **F-083**: `event list` 列内置注册表中全部 EventKey（按 domain, key 排序），`event schema <EventKey>` 输出 params_schema、resolved_output_schema 与 jq_root_path；两者均为本地查询、不依赖登录（信源：s-command）。
- **F-084**: `event consume` 不回放历史事件，仅投递订阅后新产生的事件；不读取 stdin，`< /dev/null`、nohup、setsid 均不会导致退出（信源：s-changelog）。
- **F-085**: jq_root_path 错误不会报错而会静默丢弃事件；meeting.started/meeting.end 的 jq_root_path 为 `.payload`，且 payload 为长度恒 1 的数组，jq 需先 `.[0]` 再下钻（信源：s-command、s-changelog）。
- **F-086**: 隐藏子命令 `event _bus` 由 consume 自动拉起，SKILL 明确 Agent 不得直接调用（信源：s-changelog、s-command）。
- **F-087**: v1.0.17 新增 `app get`/`app set`，管理当前登录用户自己的 CLI 应用在会中的展示：`--homepage`（http/https、≤200 字符；空字符串=不下发不在会中展示）、`--layout-style`（sidebar 375px / wide_sidebar 735px / popout 960×540）、`--sdk-name`（显示宽度 ≤20，ASCII 计 1、中文计 2）（信源：s-command、s-changelog）。
- **F-088**: 腾讯会议客户端 3.45.10 之前版本不支持会中打开 http:// 页面，仅支持 https；3.45.10 及以后两者均支持（信源：s-command）。
- **F-089**: `app set` 变更不影响当前已在进行的会议，需重新入会才能看到变化（信源：s-changelog）。

## 十、问题排查与账号条件

- **F-090**: `tshoot log` 导出本地日志打包为 zip，输出到 `~/tmeet_ts_{datetime}.zip`；`--start` 与 `--end` 必须同时传或同时不传；`--upload` 可上传服务器（需登录）（信源：s-command）。
- **F-091**: `tshoot feedback` 上报问题，`--category` 五个枚举：tool_not_found、tool_error、tool_inadequate、unexpected_result、suggestion；必填 `--intent`（≤200 字符），可选 `--actions-tried`/`--result`（各 ≤500 字符）、`--tool-name`、`--error-code`；需登录（信源：s-command）。
- **F-092**: SKILL.md 自动反馈规则要求上报前二次确认；反馈内容严禁透露姓名/电话/会议号/会议链接/会议主题/参会人，须打星脱敏；同一会话同一问题只报一次（信源：s-skill）。
- **F-093**: 使用条件：个人版、专业版已开放；商业版/企业版需填写「腾讯会议 Skills 企业账号灰度申请」表单，申请后专人联系（信源：s-cloud）。
- **F-094**: CLI 以 OAuth 授权账号身份操作，只能访问该账号下的数据，无法跨账号或访问企业级数据；当前只支持单账号登录，切换账号需先 logout 再 login（信源：s-cloud）。
- **F-095**: 错误码 500284（该功能暂不可使用）处理规则为严禁重试，如实告知功能不可用、解释权归腾讯会议；错误码 500294 返回含升级链接的套餐提示时须原样输出为可点击 Markdown 链接（信源：s-skill、s-changelog）。
- **F-096**: 云文档给出的调用链路为：Agent 加载 CLI-Skill（触发词+调用范例+安全约束）→ 拼出 tmeet 命令在终端执行 → CLI 自动注入 OAuth Token → 调腾讯会议开放平台 REST API → JSON 响应返回（信源：s-cloud）。
- **F-097**: README「安全与风险提示」声明：AI 可能因模型幻觉、提示词注入、投毒攻击、执行偏差等导致数据泄露、越权操作；安装使用 CLI 即视为自愿承担相关责任（信源：s-readme）。
- **F-098**: v1.0.18 新增事件相关客户端错误码 4000（EventInternal）、4001（EventBus）、4002（EventBusNotRunning）与 WSS token 过期服务端码 200010203、10006（信源：s-changelog）。

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
  - id: s-qqdoc
    resource: https://docs.qq.com/doc/DVUNDV0trdUdqeW5X
    title: 腾讯文档官方用户手册《腾讯会议 CLI使用说明》（页面最后保存 2026-06-25）
  - id: s-code
    resource: https://github.com/TencentCloud/tencentmeeting-cli/tree/v1.0.18
    title: tencentmeeting-cli 源码主体（tag v1.0.18，commit e631b355da2b001d24b82f453b65d96f39c59865，2026-09-11）
---

# 腾讯会议 CLI（tmeet）Facts

> 本文件登记从 10 个官方公开信源提取的 199 条编号事实：F-001 ~ F-098 基于首批 8 信源（2026-10-03），F-099 ~ F-112 基于腾讯文档官方用户手册（s-qqdoc，2026-10-03），F-113 ~ F-199 基于第三轮源码主体学习（s-code：tag v1.0.18 @ commit e631b35，2026-10-04 采集，事实均带文件/行号锚点，关键计数经 Glob/Grep 机械复核）。每条事实标注信源编号，作为本知识包唯一事实来源；信源间口径差异以「⚠️ 口径」条目并列登记，不做裁决式删改。

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

## 十一、官方用户手册（腾讯文档，最后保存 2026-06-25）补充事实与跨源比对

- **F-099**: 腾讯文档平台存在官方用户手册《腾讯会议 CLI使用说明》（https://docs.qq.com/doc/DVUNDV0trdUdqeW5X ），页面元数据 lastSaveTimestamp 为「2026年06月25日 16:00」，面向最终用户、以「对 AI 说话」叙事组织，正文含安装与操作截图（截图以图片对象存在，文本接口未返回其 URL）；公开可读、无需登录。手册开篇「风险提示」原文：「接入腾讯会议CLI后，AI Agent 将获得你预约会议、查询日程、读取录制和纪要等能力」「AI 系统可能因模型幻觉、提示词注入等原因产生非预期操作」（与 F-097 README 风险提示同源表述）（信源：s-qqdoc）。
- **F-100**: 手册用户面定位话术为「腾讯会议 CLI 就是给 AI Agent 的那双手」「你不需要自己敲命令」，与首页标语（F-002）的表述不同但定位一致（信源：s-qqdoc）。
- **F-101**: 手册点名的兼容 AI 工具为 Workbuddy、Qclaw、Cursor、Claude Code、Codex；与首页名单（F-005，含 DeepSeek Harness、GitHub Copilot）不一致，其中写作「Qclaw」（首页 FAQ 另作 OpenClaw，F-006）（信源：s-qqdoc）。
- **F-102**: 手册「本地依赖」写「Node.js ≥ 16，以及一个支持执行 Shell 命令的 AI Agent」，构成 ≥16 口径的第二信源（与 F-015 腾讯云文档一致；并列于 F-013/F-014 的 `>=14` 口径）（信源：s-qqdoc）。
- **F-103**: 商业版/企业版开通路径为填写「腾讯会议Skills企业账号灰度申请」在线表单（腾讯文档智能表格），URL 为 https://doc.weixin.qq.com/smartsheet/form/1_wpyz5ICgAAWDugasO-Q2tZhXBbuwRBgQ_d25881 ，表单说明为填写后由官方同学联系（细化 F-093）（信源：s-qqdoc）。
- **F-104**: 手册「工具清单」按五类登记 19 个命令并逐条给出一句话职责：授权 3——`auth login`（OAuth2 授权登录，可选 --no-browser）、`auth status`（查看登录状态与凭证有效期）、`auth logout`（登出清除本地凭证）；会议 7——`meeting create`（创建会议，支持普通/周期性）、`meeting update`（修改会议，需 Agent 二次确认）、`meeting cancel`（取消会议或某一场子会议，需确认）、`meeting get`（按 --meeting-id 或 --meeting-code 查详情）、`meeting list`（查待开始/进行中会议）、`meeting list-ended`（按时间范围查已结束）、`meeting invitees-list`（查受邀者名单）；录制 6——`record list`（按 ID/会议号/时间范围三选一）、`record address`（拿录制文件下载链接和 record_file_id）、`record smart-minutes`（拿 AI 纪要）、`record transcript-get`（拿转写全文）、`record transcript-paragraphs`（分页浏览转写段落）、`record transcript-search`（在转写中搜关键词）；参会报告 2——`report participants`（参会人明细含入会/离会时间）、`report waiting-room-log`（等候室成员记录）；排查 1——`tshoot log`（导出本地日志，可选 --upload 上传服务器）（信源：s-qqdoc；分组计数与 F-034 一致，本条补全逐命令名与职责原文）。
- **F-105**: 对照 v1.0.18 command.md 子命令清单（F-033）逐一核对，F-104 中 19 个旧命令名在 v1.0.18 中全部保留（含 `record address`、`record smart-minutes`、`transcript-*` 三命令、`meeting invitees-list`、`report waiting-room-log`、`tshoot log`）；44 = 19 + 25，25 个新增命令均为新命令名或新域（contact/control/minutes/app/event），未见旧命令被重命名或移除（信源：s-qqdoc × s-command 跨版本比对）。
- **F-106**: 手册安全建议写「CLI-Skill 内置了 create / update / cancel 的二次确认行为约束」，即该版本（v1.0.0 时期，2026-06-25 保存）二次确认范围为 3 个写命令；v1.0.18 SKILL.md 的确认清单已扩展至 9 个命令（F-072），新增项全部来自新域能力（受邀者变更、会中控制、权限申请）（信源：s-qqdoc × s-skill 跨版本比对）。
- **F-107**: 手册同一句表述为「腾讯会议CLI 凭证使用 AES-256-GCM 加密，存入系统 Keychain，与设备绑定，无法在另一台机器上解密」，在同一官方文本内同时包含 F-024（AES-256-GCM 本地加密）与 F-025（系统 Keychain、设备绑定）两种措辞（信源：s-qqdoc）。
- **F-108**: 手册「使用须知」给出腾讯用户规则中心链接 https://rule.tencent.com/rule/202603130003 （信源：s-qqdoc）。
- **F-109**: 手册「反馈与支持」登记三个入口：体验问题走 GitHub Issues（https://github.com/TencentCloud/tencentmeeting-cli/issues ）、安全漏洞走仓库 SECURITY.md（https://github.com/TencentCloud/tencentmeeting-cli/blob/main/SECURITY.md ）、另有「内测体验互助群」（以二维码图片给出，文本载荷中不含群号或链接）（信源：s-qqdoc）。
- **F-110**: 手册「AI 工具本身的风险」节提示：CLI 只负责把数据传给 AI Agent，数据如何使用取决于接入的 AI 工具；使用第三方 AI 客户端（点名 Cursor、Claude Code、ChatGPT）时会议内容可能被该平台模型处理，应参考对应平台隐私政策（信源：s-qqdoc）。
- **F-111**: 手册给出四个高频用户场景的对话式样例：①快速预约会议（产出会议号 123456789 与加入链接）；②会后获取纪要（产出含会议总结、关键决策、待办事项的结构化纪要）；③查看谁参加了会议（完整参会清单并与受邀名单对比谁缺席）；④修改会议时间带二次确认（AI 先 `tmeet meeting get --meeting-code 123456789` 查详情 → 告知「原定 14:00-15:00，是否改到 16:00-17:00」→ 等用户确认后才执行 `tmeet meeting update`）（信源：s-qqdoc）。
- **F-112**: 手册安装节提供「用 agent 安装（对 agent 说）」路径，示例一句话 prompt 为「按照文档帮我装一下所有的东西：https://github.com/TencentCloud/tencentmeeting-cli 」；命令行路径按序串联 npm 全局安装或 go/make 源码构建（F-011、F-017）、`npx skills add` 安装 Skill（F-012）、`tmeet auth login` 授权（F-021），并附 meeting create/list/list-ended/logout 的最小示例（时间参数示例精确到秒：`2026-03-12T14:00:00+08:00`）（信源：s-qqdoc）。

## 十二、源码主体事实（tag v1.0.18 @ e631b35，2026-10-04 采集；信源 s-code）

> 本节为第三轮增量：对 tencentmeeting-cli 源码主体（Go module `tmeet`）的结构化学习结果。锚点格式为 `文件:行号`，计数类事实均经 Glob/Grep/PowerShell 机械复核；与前 9 个文档信源的口径差异以「⚠️ 口径深化/纠正」并列，不覆盖旧条目。

### 十二-1 工程骨架、构建与分发

- **F-113**: Go module 名为 `tmeet`、`go 1.22.0`（go.mod:1-3）；直接依赖仅 8 个：spf13/cobra v1.10.2、spf13/pflag v1.0.10、gorilla/websocket v1.5.3、itchyny/gojq v0.12.17、zalando/go-keyring v0.2.8、golang.org/x/sys v0.30.0、google.golang.org/protobuf v1.34.2、Microsoft/go-winio v0.6.2（go.mod:5-14）。
- **F-114**: 程序入口 main.go 仅一行 `os.Exit(cmd.Execute())`，全部命令装配位于 cmd 包；Execute 使用具名返回值以便根 defer 的 crash recover 改写退出码（cmd/root.go）。
- **F-115**: 版本变量仅 `var Version = "dev"`（cmd/root.go:31），发布版本由 `-ldflags "-X tmeet/cmd.Version=..."` 注入；⚠️ Go 源码中**不存在** `BuildTime` 变量声明，而 Makefile/build.sh 同时传入 `-X tmeet/cmd.BuildTime=...`——该 -X 指向不存在的符号（Go 链接器静默忽略），不会进入二进制。
- **F-116**: 四个后端主机常量定义于 internal/core/endpoints.go:14-17：Open=`api.meeting.qq.com`（REST 开放平台）、CGI=`work.medialab.qq.com`（OAuth/代理）、Auth=`meeting.tencent.com`（授权页）、WSS=`meeting.tencent.com`（事件长连）。
- **F-117**: `Tmeet` 容器结构含 7 个字段（internal/core/tmeet.go:17-25）；NewTmeet 同时构造 RestClient（Open 主机）与 CGIClient（CGI 主机），配置目录以 MkdirAll(0700) 创建。
- **F-118**: 全仓（排除 vendor）实测 252 个 `.go` 文件，其中 64 个 `_test.go`、188 个非测试文件；测试分布于 21 个包。
- **F-119**: Makefile 提供 5 个交叉构建目标：darwin amd64/arm64、linux amd64/arm64、windows amd64；统一 `CGO_ENABLED=0 -trimpath -ldflags "-s -w -X ..."`，产出纯静态二进制。
- **F-120**: build.sh 的构建顺序为：先 `go test -count=1 ./...` 全量测试，再交叉编译，并执行产物 0755 权限自检、用 sed 把版本号同步进 package.json。
- **F-121**: npm 包的可执行入口 scripts/tmeet.js（实测 125 行）是 Node 包装器：Node 主版本 <14 直接拒绝；PLATFORM_MAP 维护 5 项平台→dist 二进制名映射；ensureExecutable 三层兜底（access X_OK 探测 → chmod +x → 拷贝到 tmpdir 下 tmeet-cache）；以 execFileSync 启动、stdio inherit、透传子进程退出码。
- **F-122**: ⚠️ 反直觉：postinstall 钩子 scripts/cleanup.js **不删除其他平台二进制**，其实际行为是对当前平台二进制执行一次 `tmeet auth logout` 清理登录态；任何失败均 exit 0，不阻断 npm 安装。
- **F-123**: .gitignore 忽略 tmeet 本机构建产物、.idea/、`/log` 与 `/logs` 两目录及全局 `*.log`、dist/、*.enc、master.key、*.out、node_modules、package-lock.json。
- **F-124**: Skill 安装脚本 skills/tmeet-skill/scripts/agent_init.py（实测 122 行）负责写入 agent.json（TMEET_AGENT/TMEET_MODEL 的落盘来源之一）。

### 十二-2 命令装配、中间件与精简输出

- **F-125**: cmd/root.go 启动顺序固定：registerResourceReleaseHook（类型名 ResourceReleaseHook；首个注册的是 event-bus 的 cleanup.OnUserCleared，root.go:172-178）→ NewTmeet → log.Init → crash recover defer → 10 个 AddCommand（auth/meeting/contact/record/report/control/minutes/tshoot/app/event）。
- **F-126**: 全局持久标志为 `--format`（默认 `json`）与 `--compact`（默认 false）；`-V/--version` 是根命令本地标志；root 设置 SilenceUsage: true，错误时不打印整段 Usage。
- **F-127**: 登录前置检查 preCheck 由 cobra annotation 驱动：`skipPreCheck=="true"` 跳过整条命令，`skipPreCheckFlag` 按 flag 名豁免（供 `--help` 等场景）；event 查询类与 auth 命令据此免登录，与 F-029 的用户面规则一致。
- **F-128**: 各业务域在 internal/<domain> 或 cmd/<domain> 的 base.go 导出 NewBaseCmd；叶子命令采用「opts 结构 + 洋葱中间件」装配：`middleWare.Chain(opts.Run, WithApiCmd(StaticApiCmd(...)), ...)`，业务 Run 在内层。
- **F-129**: internal/cmdutil/api_schema.go:17-100 定义**实测 38 个** ApiCmd* 字符串常量，分布：meeting 12、record 9、report 4、contact 3、control 3、tshoot 2、minutes 3、app 2。
- **F-130**: ⚠️ 关键架构事实：ApiCmd 常量**不生成任何 cobra 命令或 flag**，仅用于①请求头 `Tmeet-Cli-Name`；②compact 精简字段拉取的 cmd 参数。各叶子命令的 REST 路径硬编码在各自 Run 中；全部 flag 也是手工 StringVar/IntVar/StringSliceVar/StringArrayVar 声明。
- **F-131**: 自研 EnumValue 实现 pflag.Value 做枚举校验，全仓**仅 2 处使用**：`control waiting-room --operate-type` 与 `app set --layout-style`（cmd/app/set.go、cmd/control/waiting_room.go）。
- **F-132**: FlagSwitch/FlagSwitchWithDefault 支持一个叶子命令按 flag 出现情况切换多个 ApiCmd，例如 `meeting get` 按 `--meeting-id`/`--meeting-code` 在 ApiCmdMeetingGetById 与 ApiCmdMeetingGetByCode 间切换（与 F-046 的优先级规则互为实现侧）。
- **F-133**: `--compact` 的完整链路：远程 `GET /v1/api/compact-schema`（query: operator_id、operator_id_type=2、cmd=<apiCmd>、source=CLI）取 CompactFields → filecache 磁盘缓存（cache/schema，TTL 由服务端下发，per-apiCmd 互斥锁 + double-check）→ 输出层 `KeepFields(data, depth=10, fields)` 裁剪；远程失败透明放行（实现侧印证 F-077）。
- **F-134**: 新旧分页兼容位于 internal/cmdutil/pagination.go：PageTypeOld=0/PageTypeToken=1；page-size 上限 meeting/record 为 30、report 为 100；ChoosePageOrToken/ChoosePosOrToken 自动识别调用方传入的是旧页码还是新 token；`--page/--pos/--size` 经 MarkDeprecated 标记（实测 7 个调用点：report 3、meeting 2、record 2）。
- **F-135**: internal/cmdutil/hints 包定义的 `HintProvider` 接口（Hints(string) []string）所在包**零 import**——接口类型本身无引用；但 meeting create/update 以同签名方法（cmd/meeting/create.go:80、update.go:117）直接作为函数值传给 `output.WithHints`（internal/output/options.go:80），属结构化（鸭子类型）使用；提示内容由 GenerateMeetingSettingsHints 解析响应 corp_lock_mask 位掩码生成。
- **F-136**: 两个隐藏命令：`event _bus`（Hidden:true + skipPreCheck，其 `--interval`(5s)/`--idle-timeout` 也 MarkHidden）与 `tshoot commands`（DFS 遍历命令树列出叶子命令，供 Agent 自举获取机器可读命令清单）。
- **F-137**: annotation 键常量共 3 个：`apiCmd`、`skipPreCheck`、`skipPreCheckFlag`，均挂在 cobra.Command.Annotations 上。

### 十二-3 OAuth 设备码流与配置存储

- **F-138**: 设备码授权三 endpoint 均在 CGI 主机：`POST /v2/oauth2/oauth/cli-oauth-init`（internal/auth/auth_code.go:18，请求体含 device_id=MachineID）→ 浏览器打开 `https://meeting.tencent.com/marketplace/tencentmeeting-cli-auth.html?code=<auth_code>` → 轮询 `/v2/oauth2/oauth/cli-oauth-poll`（auth_token.go:22）。
- **F-139**: 轮询参数：间隔 loopPollTime=5s、总超时 authorizationTimeout=5 分钟（实现侧印证 F-021/F-023 的 300s）；刷新 endpoint 为 `/v2/oauth2/oauth/cli-refresh-token`（auth_token.go:40），过期判断预留 60s leeway 提前刷新。
- **F-140**: AuthTokenData 含 6 个字段：access_token、refresh_token、access_token_expire_time、refresh_token_expire_time、open_id、sdk_id。
- **F-141**: login 包整个写盘过程包在 filelock.WithLock(token.lock) 中；已登录再次登录返回 UserHasBeenInitializedError（用户面文案 `user has been initialized`，与 F-040 对应）。
- **F-142**: 代码中**不存在统一 Config 类型**，而是三份分离结构：UserConfig（sdk_id/open_id/access_token/refresh_token + int64 过期时间，加密落盘——macOS/Linux 为 `.enc` 文件，Windows 为注册表值，见 F-149）、AppMeta{active_open_id}（明文 config.json，仅用于定位当前账号的密文；源码注释沿用历史 `.enc` 泛化措辞）、AgentConfig（明文 agent.json）。
- **F-143**: 目录解析：`TMEET_CLI_CONFIG_DIR` 默认 `~/.tmeet`；`TMEET_CLI_DATA_DIR` 平台默认值为 darwin `~/Library/Application Support/tmeet`、windows `%LOCALAPPDATA%\tmeet`、unix `~/.local/share/tmeet`。
- **F-144**: 所有敏感配置写入均为原子写：同目录临时文件 + Sync + Rename；配置目录权限 0700。
- **F-145**: ResourceReleaseHook 按注册顺序执行、fail-fast；单个 hook 的 panic 被 recover 转为 error；任一 hook 失败则保留凭证与 active_open_id 供重试（实现侧印证 F-032）；事件总线在 OnAuthFailed 场景走 ClearUserConfigUnResource，不执行 hook。
- **F-146**: 唤起浏览器三平台分叉：darwin `open`、windows `rundll32 url.dll,FileProtocolHandler`、unix `xdg-open`（需 DISPLAY）；`--no-browser` 退化为仅打印授权 URL。
- **F-147**: 设备指纹 SystemInfo.MachineID 持久化在配置目录 `.machine_id`：48 字符随机串，以 O_EXCL 方式首写者胜；设备唯一 ID 构造为 `<openId>*<machineId>`（即 Tmeet-Unique-ID 头）。

### 十二-4 三平台 Keychain、加密与文件安全原语

- **F-148**: keychain 常量 ServiceName=`"tmeet"`、MasterKeyAccount=`"master.key"`（internal/core/keychain/keychain.go:31-35）。
- **F-149**: ⚠️ 口径深化（对 F-025/F-107 的实现侧修正）：凭证存储三平台并不相同——**darwin**：仅主密钥存入系统 Keychain（go-keyring），业务数据经 AES-256-GCM 加密后写 `<dataDir>/<open_id>.enc`（keychain_darwin.go:7-10）；**unix/linux**：主密钥就是权限 0600 的 `master.key` 文件（进程 umask 0077），**不使用任何系统 keyring**，业务数据同样写 `.enc`；**windows**：主密钥存注册表 `HKCU\Software\TmeetCli\keychain` 并经 DPAPI 保护，**业务数据（AES-256-GCM 密文 base64 后）也写在同一注册表键下以 open_id 命名的值中（keychain_windows.go:338-361 SetStringValue，全程无文件操作），不落 `.enc` 文件，且业务值不经过 DPAPI**。官方文档「存入系统 Keychain」仅在 macOS 字面上成立。注意 keychain.go:3-5 泛化头注释与 config.go/user.go 沿用的 ".enc" 措辞为历史注释，平台注释与平台 Get/Set 实现才是权威。
- **F-150**: 加密原语（crypto.go）：AES-256-GCM；主密钥为 32 字节随机数，无 KDF/无口令派生；nonce 12 字节；密文字节布局为 `nonce || ciphertext || tag`（macOS/Linux 即 `.enc` 文件布局，Windows 为注册表值经 base64 解码后的字节布局）。
- **F-151**: GCM 的 AAD（附加认证数据）绑定 account（open_id 字节），防止跨账号替换密文（macOS/Linux 为替换 `.enc` 文件，Windows 为改写他人注册表值）（代码注释 SEC-009，keychain_darwin.go:89、keychain_windows.go:317/344）；decryptWithAADFallback 先以 account 作 AAD 解密、失败再以 nil AAD 重试一次，用于自动迁移历史密文。
- **F-152**: windows DPAPI 的 entropy 为 `service + "\x00" + account`；仅当主密钥解密命中 NTE_BAD_KEY_STATE(0x8009000B)/ERROR_INVALID_DATA(0xD)/NTE_BAD_DATA(0x80090005) 三个错误码、且新旧 entropy 两次尝试均失败时，才 purge 整个注册表键并重新生成（keychain_windows.go:152-170,240-241,409-420），非任意读取失败都自愈。
- **F-153**: filelock 跨平台互斥：unix flock(LOCK_EX|LOCK_NB)，windows LockFileEx；获取不到时 50ms 轮询、5s 超时。
- **F-154**: filecheck（unix）在读取 .enc 等敏感文件前拒绝符号链接、非常规文件与非属主文件；windows 因走注册表存储而为 no-op（filecheck_windows.go:5 注释 SEC-010）。
- **F-155**: 配置层注释明确「plaintext is never persisted to disk」：明文 token 只存在于内存，config.json 仅含非敏感的 active_open_id（internal/config/config.go:14,28-29）。

### 十二-5 HTTP 传输、代理头、错误码与重试

- **F-156**: thttp DefaultHttpClient 整体 Timeout=3s、MaxIdleConns=200；业务响应统一信封 `{trace_id, message, data, hints}`。
- **F-157**: cgi-proxy 使用泛型 ProxyRsp{code,message,nonce,data}；网络失败时以 DefaultNoProxyHttpClient（绕过代理配置）新建 Request 重试 1 次。
- **F-158**: rest-proxy 每次请求前先 RefreshToken；请求最多 retry 3 次；TokenExpired/NotRetry 分类不重试；服务端码 200190303 被判定为 token 过期。
- **F-159**: REST 请求注入的诊断/安全头包括：Tmeet-Unique-ID（openId*machineId）、Tmeet-Device-Info（os;agent;model）、Tmeet-Open-Source: CLI、Tmeet-Cli-Ver、Tmeet-Trace（cmdPath;traceID）、Tmeet-Cli-Name（apiCmd）；链路 trace 优先取响应头 X-TC-Trace。
- **F-160**: 客户端错误码分段：1000-1007、2000-2008、3000-3002、4000-4002（事件域，与 F-098 对应）、9000（Panic）；错误判定走 exception 包的包级函数 `exception.Is(err, target)`——两个参数均为 `*TmeetError` 时只比较 Code 字段（errors.go:31-39）；TmeetError 本身没有 Is 方法。
- **F-161**: 通用退避重试参数：MaxAttempts=3（即最多执行 4 次）、初始间隔 100ms、倍率 2.0、单步封顶 3s、±25% jitter。
- **F-162**: OAuth2Authenticator 为请求附加 X-TC-Nonce 等鉴权头。

### 十二-6 事件总线（per-host bus）内核

- **F-163**: 事件子系统共七个组件：source（Source 接口 Name/Run，可选 Subscribable）→ bus（Bus.Run + Hub fan-out，每个 Conn 的 sendCh 容量实测 sendChCap=100，bus/conn.go:39）→ IPC transport → busctl（Ping/QueryStatus/SendShutdown）→ spawner → busdiscover 为守护进程侧六个组件，consume_runner 为 consume 客户端侧的第七个组件（消费适配/输出/退出码）。
- **F-164**: IPC 端点：unix 为 `<configDir>/event/bus.sock`；windows 为命名管道 `\\.\pipe\tmeet-event-bus`（go-winio），管道缓冲 pipeBufferSize=65536（transport_windows.go:30），代码中无显式 SDDL（默认 ACL）。
- **F-165**: bus 自举由 spawner 以 exec 再调用自身隐藏命令 `event _bus` 完成：unix  Setsid 脱离控制终端；windows 用 CREATE_NEW_PROCESS_GROUP(0x200)+HideWindow（注意不是 DETACHED_PROCESS）；子进程 stdio 全 nil；ready 等待 5s、就绪探测 ping 间隔 20ms；Release 时不 Wait 子进程。
- **F-166**: bus 存活判据是 `bus.alive.lock` 文件锁的非阻塞 TryLock（busdiscover），而非探测 PID；另有 bus.pid（pid + RFC3339 时间，tmp+rename 原子写）、bus.meta（meta_version=1/openid_hash/started_at/bus_version/pid）、bus.fork.lock（并发 fork 串行化）、ws.state（source 状态持久化）。
- **F-167**: WSS 入口 `wss://meeting.tencent.com/wemeet-socket/mercury-wss-cli/connection`；协议 wsspb 基于 protobuf，Head 字段含 frame_type/cmd_type/cmd/seq_no/msg_id/module/status。
- **F-168**: 鉴权帧 AuthBindReq/AuthRefreshReq 携带 biz_id/token_type/token/open_id/cli_uniq_id；常量 biz_id=`web_hook_cli`、token_type=`access-token`；cmd 常量包括 `/conn/ping`、`/conn/access-token-auth-bind`、WsCLISubscribeEvent、WsCLIPushEvent。
- **F-169**: 心跳是**应用层** `/conn/ping`（非 websocket control ping），默认间隔 defaultHeartbeatInterval=25s（source/wssource.go:102），服务端 HeartRsp.heart_interval 可下发覆盖；握手超时 10s、读超时 5min、重连退避 1-30s、连续失败 30 次放弃、稳态持续 >60s 后重置失败计数；关闭码 1006 触发重连，鉴权错误不重连；token 轮换时 AuthRefresh 优先于下一次 ping 发出。
- **F-170**: IPC 为 NDJSON 行协议，消息类型共 8 种：hello/hello_ack/event/control/bye/status_query/status_response/shutdown。
- **F-171**: source 状态机 6 态：connecting/reconnecting/steady/auth_failed/auth_expired/disconnected；状态写 ws.state 文件供重连/诊断读取。
- **F-172**: consumer 接入时的 Hello 校验链：owner hash = `sha256(openId)` 前 12 字节的 hex（24 字符），不匹配拒绝；必须恰好声明 1 个 EventKey 且该 key 已注册；错误分类 WrongOwner/UnknownEventKey/InvalidParams。
- **F-173**: 事件注册表实测**恰好 8 个 key**（internal/event/schemas.go 中 8 次 RegisterKey，行 106/196/294/378/462/563/675/768）：meeting.created、meeting.updated、meeting.canceled、meeting.started、meeting.end（domain=meeting，5 个）、recording.completed（recording）、smart.transcripts、smart.minutes（smart）；8 个 key 的 jq_root_path 全部为 `.payload`，params 均为可选 meeting_id，线上 payload 形态为 `array<object>`；**长度恒为 1 的服务端契约仅覆盖 meeting.started / meeting.end 两个 key**（schemas.go:32-39 注释：数组形态为未来批量推送预留、当前未启用），其余 6 key 无此保证。
- **F-174**: ⚠️ 纠正：schemas.go 头注释提到的 `recording.failed` **未注册**，`event list` 实际只暴露 F-173 的 8 个 key；注册表不是开放扩展点，新增事件类型必须改代码发版本。另：结束事件官方拼写为 **`meeting.end`**（非 `meeting.ended`；schemas.go:44-45、docs/command.md:1472 双重一致，后者示例形式为 `--event-id meeting.end`），写错返回 UnknownEventKey；v0.3.0 复核据此更正示例 04 的 4 处旧写法。
- **F-175**: 订阅引用计数 subRegistry：同一 EventKey 首个消费者 0→1 时向 WSS 发 SUBSCRIBE；**最后一个消费者 1→0 时不发 UNSUBSCRIBE**——Remove() 虽返回 1→0 布尔值但 bus 不据此动作（subreg.go:13-15,57-61；source.go:63-66 注释 "There is intentionally NO Unsubscribe"），契约为「消费者消失后由服务端按 TTL 自动取消」；重连后以 Snapshot() 全量 Replay 重订阅（subreg.go:84-90）；多消费者复用同一服务端订阅。
- **F-176**: 慢消费者背压：dropped 计数按订阅者每 1s 聚合；单 Conn 队列满时 PushDropOldest 丢最旧事件保新事件（bus/conn.go:220-254）。
- **F-177**: bus 空闲退出 IdleTimeout=30s（无消费者）；`_bus --interval 5s --idle-timeout` 两个参数对用户隐藏（与 F-136/F-086 对应）。
- **F-178**: 事件去重环 DefaultDedupCapacity=512（dedup.go:31），去重键为 RawEvent.TraceID，用于吸收重连窗口内的重复推送。
- **F-179**: consume 就绪标记 `[event] ready event_key=%s` 写 stderr 且 `--quiet` 不屏蔽（实现侧印证 F-081）；内部 frameCh 容量 8；事件输入全部来自 IPC netConn，**不读 stdin**（印证 F-084）；Hello 帧 trace_id 格式为 `consume-<pid>-<nanos>`。
- **F-180**: consume 退出 reason 是**字符串**而非数字枚举：limit/timeout/signal/shutdown；退出码 2 仅出现在 `status --fail-on-orphan` 与 `stop` 被拒绝/出错两处（印证 F-081/F-082）。
- **F-181**: `--output-dir` 安全约束：仅允许相对路径、拒绝绝对路径与包含 `..` 的路径段、对 traceID 做 sanitizeTraceID 清洗、文件权限 0o600；落盘内容为原始事件，**不受 `--jq` 投影影响**。
- **F-182**: `event stop` 优雅关闭等待 10s；仍有消费者且未带 `--force` 时拒绝（refused, exit 2）；`--force` 清理 bus.pid/bus.meta/bus.sock 三件，**不删除 alive lock**。
- **F-183**: 登出钩子 cleanup.OnUserCleared：仅 owner hash 匹配才动作 → 发 Shutdown 并等 3s → 进程仍存活则按 PID 在 unix 发 SIGKILL、windows 调 TerminateProcess → 清理 sock/meta/pid（F-032 两阶段清理在事件域的具体实现）。
- **F-184**: jq 过滤基于 gojq Parse/Compile；Apply 得到零结果时 dropped=true（静默丢弃，印证 F-085 的用户面现象）；消费端 jq_root_path 为 `.payload` 时喂给 jq 的输入是 ev.Payload。

### 十二-7 枚举、输出管道、日志与崩溃上报

- **F-185**: internal/utils/enumerate 实测 16 个非测试枚举文件；CorpLockMask 为 uint32 位掩码：0x1 文字水印、0x2 音频水印、0x4 自动录制、0x8 自动 ASR（hints 解析的依据）；ExportJobStatus=1/2/3 对应导出任务三态。
- **F-186**: InstanceType 实测 **23 个成员**（instanceid.go:7-29）：取值 0-10、12、20-22、30、32、33、81-84、86；其中 12=Vision Pro，81-84/86 为 HarmonyOS 手机/平板/PC/座舱/AR-VR；11、31、85 等缺号。
- **F-187**: 其他业务枚举：MeetingJoinType(1/2/3)、MeetingRecurringType(0-4)、MeetingRecurringUntilType(0/1)、MeetingType(0/1/2/4/5/6)、MeetingUserRole(0-7)、MeetingUserJoinRole(creator/hoster/invitee)、RecordState(1/2/3)、RecordType(0/2/3/4/5)、RecordAudioDetect(0/1)、ShowAllSubMeetings(0/1)、WaitingRoomOperateType(1/2/3，双向映射)。
- **F-188**: converter 包对 JSON 字节树做字段变换（点路径/同名双模式、maxDepth 限深）；TimestampConverter 以 1e11 为阈值自动判别秒/毫秒时间戳（支撑 F-038 的时间展示转换）。
- **F-189**: ⚠️ 代码与 CHANGELOG 不一致：Base64DecodeConverter 源码实际只处理 3 种编码标识，而 CHANGELOG v1.0.18 称支持 4 种；本知识包以源码 3 种为准，并列登记差异。
- **F-190**: 输出层：formatOutput 组装统一信封（F-156）；event 经 EventPrint 输出 bare JSON NDJSON（印证 F-037）；业务中间件包括 WithConvert、WithContactSearchLogic（users 恰好 1 条时仅保留 open_id）、WithMetaFieldFilter（按 filter_field 裁剪）、WithTotalCountLogic（total_count=0 时移除该字段）。
- **F-191**: 日志为自研实现（未用第三方日志库）：文件名 tmeet-YYYY-MM-DD.log，单文件 10MB 滚动、保留 7 天，写入经容量 4096 的异步 channel；bus 经 InitNamed 写 logs/bus-*.log；trace_id 为 32 字符 hex（8 字符秒级时间戳 + 4 字符 PID + 20 字符随机）。
- **F-192**: panic 恢复后 POST `/v1/cli/crash` 上报（1s 超时；body: operator_id、operator_id_type:2、crash_stack、error_code），栈截断 8192 字符，PanicExitCode=2；recover 必须由调用方 defer 触发；运行不产生 coredump 文件。
- **F-193**: 环境变量 TMEET_AGENT/TMEET_MODEL 优先于 agent.json 配置，最终进入 Tmeet-Device-Info 请求头。
- **F-194**: 工程纪律：CONTRIBUTING.md 要求 gofmt、go test 通过、中文注释、新功能必须附测试；SECURITY.md 承诺仅维护 latest 版本、漏洞私域上报、7 个工作日首次响应、30 天修复。

### 十二-8 版本沿革与仓库统计

- **F-195**: CHANGELOG.md 实测 **18 个**版本条目：v1.0.1（2026-04-07）至 v1.0.18（2026-09-11），**不存在 v1.0.0**；README/Makefile 中的 `v1.0.0` 仅为构建命令示例值。⚠️ 旧条目 F-106 中「v1.0.0 时期」系依据手册保存日期（2026-06-25）的推断措辞，源码版本序列自 v1.0.1 开始。
- **F-196**: tag v1.0.18 快照内 docs/command.md 与 docs/command_en.md 实测均为 1594 行，与 s-command 信源（main 分支 raw，1594 行）一致。
- **F-197**: skills/tmeet-skill/SKILL.md 实测 401 行、9 个 `##` 二级章节；frontmatter 为 name=tmeet-skill、version 1.0.18，metadata.requires 声明 bins 与 cliHelp；无 license 字段。
- **F-198**: skills/tmeet-skill/references/ 下实测 10 个分命令参考 Markdown，随 Skill 一起分发。
- **F-199**: 分发链路事实串联：Go 侧 5 目标静态二进制（F-119）→ package.json files 仅收 scripts/ 与 dist/、bin 指向 scripts/tmeet.js（F-008）→ tmeet.js 按 PLATFORM_MAP 5 项映射选二进制并做可执行位兜底（F-121）→ postinstall 执行 auth logout 清登录态（F-122）；版本号单一注入点为 tmeet/cmd.Version，BuildTime 注入为空操作（F-115）。

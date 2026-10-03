---
type: Reference
title: "CLI-SKILL 清单、CHANGELOG 与 package.json 信源"
description: "tmeet-skill/SKILL.md v1.0.18（Agent 行为契约）、CHANGELOG.md（版本演进）与 package.json（包元数据）的事实登记：二次确认、隐私规则、双纪要路由、event/app 版本变更。"
tags: [tencent-meeting, tmeet, reference, skill, changelog, package-json, agent-contract]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: skill-manifest
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/skills/tmeet-skill/SKILL.md
    title: CLI-SKILL 清单 tmeet-skill/SKILL.md
  - id: changelog
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/CHANGELOG.md
    title: 项目变更日志 CHANGELOG.md
  - id: package-json
    resource: https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/package.json
    title: npm 包清单 package.json
---

# CLI-SKILL 清单、CHANGELOG 与 package.json 信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| SKILL.md | https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/skills/tmeet-skill/SKILL.md（v1.0.18，约 34KB） |
| CHANGELOG | https://raw.githubusercontent.com/TencentCloud/tencentmeeting-cli/main/CHANGELOG.md（Keep a Changelog） |
| package.json | 同仓库 main 分支根目录 |
| 抓取日期 | 2026-10-03 |
| 对应事实 | F-008 ~ F-010、F-014、F-023、F-032、F-036、F-037、F-062 ~ F-064、F-066、F-072 ~ F-079、F-082、F-086、F-089、F-092、F-095、F-098 |

## SKILL.md：Agent 行为契约（v1.0.18）

登记的规则族：

1. **登录态**：auth login 阻塞 ≤300s、必须前台禁止后台（F-023）；除 auth 与 event 只读命令外均需登录；
2. **响应契约**：统一 {trace_id,message,data} 信封；event 族 bare JSON、compact 无效（F-036、F-037）；
3. **双纪要体系**：元宝纪要（ASR、人人可取、无逐字稿）vs 录制纪要（创建者所有、需权限、有逐字稿）；permission_status 分流、失败降级、跨会议双跑标注来源（F-062~F-064）；
4. **二次确认 9 命令 + 跨轮确认流程**，禁止自问自答/虚构指令/默认代选（F-072、F-073）；
5. **隐私字段**：禁止对用户暴露 meeting_id，只用 meeting_code（F-074）；成员回显 `姓名（部门>职位>open_id）`（F-075）；多候选用户定夺、必填缺失禁自填（F-076）；
6. **通讯录白名单**：仅限邀请/呼叫前置解析（F-066）；
7. **踢人来源**：必须取自 report participants（F-071）；
8. **token 节流**：查询默认 compact；翻页 5 页/200 条征询、游标禁自造（F-077、F-078）；
9. **反馈纪律**：tshoot feedback 二次确认、隐私脱敏、同问题只报一次（F-092）；
10. **错误码**：500284 禁重试、500294 升级链接原样渲染（F-095）。

## CHANGELOG：版本演进要点

- **v1.0.18（2026-09-11，最新）**：新增 event 命令组（per-host bus、共享 WSS、NDJSON、ready/exit 契约、状态机、错误码 4000~4002 等）（F-079~F-086、F-098）；logout 两阶段资源释放 hook（F-032）；build.sh 先 go test 再编译；stale 代理 env 自动直连重试；compact 白名单拉取失败透明放行（F-077）；
- **v1.0.17（2026-09-09）**：新增 app get/set 会中展示配置（F-087~F-089）；
- **v1.0.5**：分页统一为 page-token/page-size（F-039）。

迭代密度信号：v1.0.17 与 v1.0.18 间隔仅 2 天；腾讯云文档 2026-07-08 的 19 命令清单到 v1.0.18 的 44 子命令（F-033、F-034）。

## package.json：包元数据

- `version: v1.0.18`；`bin.tmeet = ./scripts/tmeet.js`；`engines.node >=14`（F-008、F-014）；
- `postinstall: node scripts/cleanup.js`；发布文件仅 `scripts/`、`dist/`（F-008）。

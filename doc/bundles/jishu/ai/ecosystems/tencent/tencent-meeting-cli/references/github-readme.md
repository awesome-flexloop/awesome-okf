---
type: Reference
title: "tencentmeeting-cli GitHub README 信源"
description: "官方开源仓库 README 的事实登记：包名与许可证、Go 源码构建、设备码授权、AES-256-GCM 凭证、配置目录、命令树、全局契约、分页迁移与安全风险提示。"
tags: [tencent-meeting, tmeet, reference, github, readme, open-source]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: github-readme
    resource: https://github.com/TencentCloud/tencentmeeting-cli
    title: tencentmeeting-cli GitHub README（main 分支）
---

# tencentmeeting-cli GitHub README 信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | github-readme |
| URL | https://github.com/TencentCloud/tencentmeeting-cli |
| 类型 | 官方开源仓库 README（main 分支） |
| 抓取日期 | 2026-10-03 |
| 对应事实 | F-001、F-003、F-011、F-017、F-018、F-021、F-022、F-024、F-028、F-031、F-033、F-035、F-038、F-039、F-097 |

## 仓库与包

- 命令入口 `tmeet`，npm 包 `@tencentcloud/tmeet`（F-001）；
- MIT License，README 徽章标注 Go 1.22+（F-003）；
- 跨平台 macOS/Linux/Windows（F-018）。

## 安装

```bash
npm install -g @tencentcloud/tmeet   # F-011
```

源码构建（F-017）：

```bash
go build -ldflags "-X tmeet/cmd.Version=v1.0.0" -o tmeet .
make build VERSION=v1.0.0
```

## 授权

- `tmeet auth login` 设备码 OAuth2 流程：自动打开浏览器 + 终端轮询，超时 5 分钟；`--no-browser` 只输出 URL（F-021、F-022）；
- 凭证 AES-256-GCM 加密保存到本地，明文不落盘（F-024）；
- 配置目录 `~/.tmeet/`，环境变量 `TMEET_CLI_CONFIG_DIR` / `TMEET_CLI_DATA_DIR`（F-028）；
- 怀疑泄露：`tmeet auth logout` 并到账号安全中心吊销（F-031）。

## 命令树与全局契约

- README 命令树列出 auth/meeting/contact/record/report/control/minutes/tshoot/app/event 共 10 个命令域（F-033）；
- 全局标志：`--format json|json-pretty`、`--compact`、`--version/-V`（F-035）；
- 时间一律 ISO 8601 带时区（F-038）；
- v1.0.5 起分页统一为 `--page-token` + `--page-size`，旧 `--page`/`--pos`/`--size` deprecated（F-039）。

## 安全与风险提示（原文要点）

README 明示：AI 可能因模型幻觉、提示词注入、投毒攻击、执行偏差等导致数据泄露、越权操作；安装使用 CLI 即视为自愿承担相关责任（F-097）。

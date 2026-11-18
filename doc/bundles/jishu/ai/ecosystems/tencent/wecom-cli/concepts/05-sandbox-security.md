---
type: concept
title: 沙箱与安全：双域文件系统及遥测边界
description: 说明 wecom-cli 的私有域、工作域、deny 规则、固定临时目录与调用链遥测。
tags: [wecom, wecom-cli, sandbox, security]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 沙箱与安全：双域文件系统及遥测边界

CLI 在构造期建立两个文件系统域：私有域 roots 为配置目录；工作域 roots 为当前工作目录和固定临时目录，并额外拒绝配置目录。roots 与 deny 没有环境变量、flag 或配置扩展口（F-116–F-119）。

## deny 规则

内建 deny glob 共 34 条，覆盖凭据目录、凭据与历史文件名、密钥证书扩展名和多段凭据库（F-120）。规则包括 `.ssh`、`.aws`、`.git` 等目录，`.env`、`id_rsa` 等文件，以及 `.pem`、`.key`、`.p12`、`.pfx`、`.jks` 等扩展名（F-121–F-124）。Unix 与 Windows 另有系统目录和 DPAPI 形状规则（F-125–F-127）。

deny 恒优先于 allow；默认 deny 为空，调用方必须显式挂载推荐规则。即使 roots 为 None，已挂载的 deny 仍然生效（F-128）。固定临时目录在 Unix 为 `/tmp`，Windows 为本地数据目录下的 `Temp`，不使用 `std::env::temp_dir()`（F-131）。

## 遥测与验证

调用链头使用 `x-wecom-trace`，值包含 chain 与 id 并限制为 512 字节；启用 `call-chain` 时由入口注入（F-132、F-133）。日志读取 `WECOM_CLI_LOG_LEVEL`、`WECOM_CLI_LOG_DIR` 与编译期默认目录，JSON 修复成功事件会向 stderr 给出提示（F-134、F-135）。安全 e2e 还覆盖符号链接逃逸、硬链接别名、`..` 逃逸和配置目录位于 cwd 等场景（F-169）。

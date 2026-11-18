---
type: concept
title: 传输与韧性：信封、轮询、续传与分页
description: 说明 wecom-cli transport 层如何承载协议封装、长任务轮询、断点续传和输出分页。
tags: [wecom, wecom-cli, transport, resilience]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 传输与韧性：信封、轮询、续传与分页

`wecom-transport` 集中管理网络与长任务语义。默认最小轮询间隔为 500 ms，默认轮询超时为 120 秒，连续网络错误上限为 3 次（F-101）。

## 信封与响应

响应协议由 `ApiResponse` 承载 `result`、错误、taskid、poll mode、长任务信息和额外字段；`ResponseEnvelope` 负责把响应解码为该结构，传输层提供 `PassthroughReq` 与 `GatewayRes`（F-106–F-109）。

## 长任务

长任务信息包含 `done`、`task_timeout` 与 `polling_interval_ms`。`TaskQuery` 使用 `POST /task/query` 并提交 method 与 payload；每轮按配置间隔休眠，首次取得超时参数时记录起点，超过时限返回超时错误（F-102–F-105）。`ApiResponse` 直接提供轮询信息给 transport 层（F-115）。

## 断点续传与 HTTP 超时

续传最多 4096 段，单段上限 64 MiB；已知总长度完成、返回零字节或收到 416 时终止，短读不终止（F-110、F-111）。HTTP 请求默认不设置全局 timeout，只有显式 timeout 才写入 reqwest builder（F-112–F-114）。

## 输出分页

设置 `--page-count` 后，执行器按页循环并在页间按 `page_delay_ms` 休眠；`write_page` 在有文件时追加写入，否则交给输出器打印（F-074、F-075）。

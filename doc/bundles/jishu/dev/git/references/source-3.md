---
type: Reference
title: 信源：《Git 下载代码加速，解除容量限制》（简书连载《开源的世界》）
description: 简书文章《Git 下载代码加速，解除容量限制》信源登记——http.postBuffer 增大缓存、lowSpeedLimit/lowSpeedTime 提速、浅层克隆与 fetch --unshallow（2020 年前后）
tags: [git, 下载加速, 信源登记, 简书, 开源的世界]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8a47a9e7353b
    url: https://www.jianshu.com/p/8a47a9e7353b
    title: 《Git 下载代码加速，解除容量限制》
---
# 信源：《Git 下载代码加速，解除容量限制》

本文是简书连载《开源的世界》（nb/40234132）中的一篇（Git 下载代码加速，解除容量限制），作者为"水之心"，内容时点为 2020 年前后。本 git 束的下载加速内容以其为事实依据（F-256~F-259）。

## 信源信息

| 项目 | 内容 |
|------|------|
| 标题 | Git 下载代码加速，解除容量限制 |
| 作者 | 水之心 |
| 所属连载 | 开源的世界（https://www.jianshu.com/nb/40234132） |
| 原文 URL | https://www.jianshu.com/p/8a47a9e7353b |
| 内容时点 | 2020 年前后 |
| 抓取时间 | 2026-09-02 |

## 内容要点

- 针对 `error: RPC failed; curl 18 transfer closed with outstanding read data remaining` 报错：增大缓存 `git config --global http.postBuffer 524288000`，用 `git config --list` 查看是否生效后重新克隆
- 针对网络下载速度缓慢：`git config --global http.lowSpeedLimit 0` 与 `git config --global http.lowSpeedTime 999999`
- 仍无法 clone 时的兜底：浅层克隆 `git clone --depth=1 http://xxx.git` 后 `git fetch --unshallow` 更新远程库到本地
- 参考资料：博客《使用Git pull文件时，出现"error: RPC failed; curl 18 transfer closed with outstanding read data remaining"》（cnblogs.com/p/12503650.html）

## 覆盖事实编号

F-256 ~ F-259

---
type: Concept
title: Git 下载代码加速与容量限制解除
description: 基于 2020 年前后《开源的世界》下载加速教程——http.postBuffer 增大缓存、http.lowSpeedLimit/lowSpeedTime 低速阈值调整、浅层克隆加 fetch --unshallow 解除 Git 克隆容量与速度问题
tags: [git, 下载加速, 网络配置]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8a47a9e7353b
    resource: /references/source-3.md
    title: 《Git 下载代码加速，解除容量限制》
---
# Git 下载代码加速与容量限制解除

> **时点说明**：本文基于 2020 年前后教程（简书连载《开源的世界》中的《Git 下载代码加速，解除容量限制》）整理。下述 `git config` 配置项与浅层克隆技巧均为 Git 原生能力，方法仍可参考；具体配置值可根据网络状况调整。

## 背景：克隆报错（F-256）

通过 HTTP 克隆大仓库时可能出现如下报错，通常是缓存区溢出（curl 的 `postBuffer` 默认值太小）导致：

```
error: RPC failed; curl 18 transfer closed with outstanding read data remaining
```

## 方法一：增大缓存（F-256）

使用 git 命令增大缓存（单位是 B，`524288000` 约 500MB）：

```bash
git config --global http.postBuffer 524288000
```

使用 `git config --list` 查看是否生效，此时重新克隆即可。

## 方法二：调整低速阈值（F-257）

针对网络下载速度缓慢，修改低速限制相关配置：

```bash
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

## 方法三：浅层克隆（F-258）

以上两种方式依旧无法 clone 时，可先以浅层克隆（只取最新历史）下载，再更新远程库到本地：

```bash
git clone --depth=1 http://xxx.git
git fetch --unshallow
```

## 现状

- 本文基于 2020 年前后教程，参考资料为博客《使用 Git pull 文件时，出现"error: RPC failed; curl 18 transfer closed with outstanding read data remaining"》（cnblogs.com/p/12503650.html，F-259）。
- `http.postBuffer`、`http.lowSpeedLimit`/`http.lowSpeedTime` 为 Git 官方配置项，长期可用；浅层克隆 `--depth` 与 `git fetch --unshallow` 也是 Git 原生能力。实际克隆慢/失败还可能与网络代理、防火墙、仓库体积等因素相关，可结合当前网络环境排查。
- 配置均为 `--global` 全局作用域，若只想作用于单个仓库可去掉 `--global`。

## 相关概念

- [Git 学习路线与 Git Flow 分支模型导论](00-learning-path.md)
- [Git Flow 分支模型与团队协作](01-branch-model.md)

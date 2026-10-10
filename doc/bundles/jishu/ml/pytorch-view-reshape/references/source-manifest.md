---
type: source-manifest
title: 信源登记——PyTorch view/reshape 公众号博文
description: 微信公开博文《（导师：PyTorch 的 view 和 reshape 你真会用？）》信源登记、公开性核验与采集记录
sources:
  - id: wechat-article
    url: https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w
    title: 导师："PyTorch的view和reshape你真会用？"我："Codex写的！"导师："一转置就报错，连内存拷贝都没搞懂，你敢说自己会训练模型？"
    author: cos大壮（公众号「深夜努力写Python」）
    date: "2026-10-09"
status: stable
generated:
  by: trae-solo-agent
  at: "2026-10-10T10:00:00+08:00"
okf_version: "0.2"
---

# 信源登记（Source Manifest）

## 1. 账号归属与公开性核验

| 项 | 值 |
|----|----|
| 公众号账号名 | **深夜努力写Python**（`nickname` 字段） |
| 文章署名作者 | cos大壮（全文自述"我是cos大壮"） |
| 发现渠道 | 用户直接提供 mp.weixin.qq.com 公开链接（`?from=industrynews`） |
| 公开性 | ✅ 公开可访问，无需登录/邀请码/CAPTCHA 绕过 |
| 账号归属信号 | 页面 nickname=「深夜努力写Python」；og:title 与正文标题逐字一致；appmsgid=2247503302 |
| 采集方式 | curl 带移动端 UA 直取 HTML，解析 `js_content` 正文（psi-wall 未见；正文全文取得） |
| 采集时间 | 2026-10-10 |

## 2. 文章元数据

| 项 | 值 |
|----|----|
| 标题 | 导师："PyTorch的view和reshape你真会用？"我："Codex写的！"导师："一转置就报错，连内存拷贝都没搞懂，你敢说自己会训练模型？" |
| 发布时间 | 2026-10-09 11:26（`createTime` / `createTimestamp=1791516360`） |
| URL | https://mp.weixin.qq.com/s/Cj-lGaB1EaSC0I1yeaRH0w |
| 正文字数 | ~7239 字符 / 259 行（采集提取后） |
| 内容主题 | PyTorch `view()` vs `reshape()`、张量内存布局/连续性（contiguity）、`transpose()`/`permute()` 后 `view()` 报错机理、完整时序分类案例 |
| 附带内容 | 结尾为「超硬核：学习圈子」推广文案（问题清单），属作者营销/引流部分，不作为技术事实处理 |

## 3. 停止规则与失败清单

| 项 | 结果 |
|----|------|
| `not-collected` | 无（正文全文取得） |
| `unverified` | 见 [facts.md](facts.md) 中 `author_claim` 类型条目（作者观点，非硬事实） |
| 全文镜像 | 未复制全文，仅登记结构性事实与作者声明（详见 facts.md） |

## 4. 采集通道

- **脚本方案**：`curl.exe -s -L -A "<iPhone UA>"` 直取 mp.weixin.qq.com HTML；`js_content` 提取正文。
- 该通道为一次性只读获取，未持久化登录态，未绕过任何访问控制。

## 5. 责任边界

本文技术内容为 PyTorch 框架公开 API 语义（`view`/`reshape`/`contiguous`/`transpose`/`permute`/`is_contiguous`/`stride`），以 PyTorch 官方文档为准；本束仅对博文所述口径作 P0 核验（详见 [verification.md](verification.md)），不把作者教学性措辞升级为普遍事实。
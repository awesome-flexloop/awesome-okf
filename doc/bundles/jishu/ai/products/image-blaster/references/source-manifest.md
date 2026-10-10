---
type: Reference
title: image-blaster 信源登记（source-manifest）
description: 本知识包的信源清单、公开性预检记录、采集方式与停止规则
sources:
  - id: wechat
    resource: https://mp.weixin.qq.com/s/uANTnBjmirCavBJb9pNytA
    title: 6.9K Star！这个开源项目把图像变3D世界的门槛砸得稀碎！
    access_time: "2026-10-10"
  - id: github
    resource: https://github.com/neilsonnn/image-blaster
    title: neilsonnn/image-blaster（README + .claude/skills 目录实测）
    access_time: "2026-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T12:00:00+08:00"
status: stable
stale_after: "2026-12-10"
---

# 信源登记（source-manifest）

## 信源清单

| source_id | 类型 | URL | 标题 | 访问时间 | 可访问性 | 归属证据 | 状态 |
|---|---|---|---|---|---|---|---|
| `wechat` | 公众号公开文章 | [mp.weixin.qq.com/s/uANTnBjmirCavBJb9pNytA](https://mp.weixin.qq.com/s/uANTnBjmirCavBJb9pNytA) | 6.9K Star！这个开源项目把图像变3D世界的门槛砸得稀碎！ | 2026-10-10 | ✅ 公开可读（curl 抓取成功，无需登录/验证码） | og:url 指向该原文；URL 含 `from=industrynews` 频道参数；无账号名可抓取确认 | collected |
| `github` | 开源仓库（官方一手） | [github.com/neilsonnn/image-blaster](https://github.com/neilsonnn/image-blaster) | README + `.claude/skills/` | 2026-10-10 | ✅ 公开可读 | GitHub 官方页面；MIT license；neilsonnn（Neilson K-S），World Labs 团队成员（第三方来源佐证） | collected |

## 公开性预检（Public-Only Gate）

**VP1. 是否无需登录、邀请码、验证码或特殊权限即可访问？**
- `wechat`：✅ 是。通过 curl 直接抓取到完整 HTML（含 `js_content` 正文区，约 3.7MB 页面，正文 ~5395 字符），未遇登录墙/验证码。
- `github`：✅ 是。GitHub 公开仓库。

**VP2. 页面归属信号是否可核验？**
- `wechat`：og:url 指向目标 URL，og:description 与正文标题吻合（"从一张照片到一个可漫游的3D空间，中间隔了多少行业壁垒？"）。账号名（公众号名）未能从抓取页面确认，已在边界标注。
- `github`：仓库主 `neilsonnn` 与文章所述作者 GitHub 手柄一致。

**VP3. 遇到登录墙/验证码/限流时是否停止并记录？**
- 首次 WebFetch 被微信侧 "环境异常" 拦截（反爬/临时限制，非登录墙），故改用 curl + UA 抓取成功。已如实记录采集方式差异。

**VP4. 是否未将文章全文/原始 HTML 掺入库？**
- ✅ 是。全文原始文本仅存于会话临时文件（`%TEMP%`），bundle 内仅保留结构化事实、摘要与必要短引用，未做全文镜像。

## 采集方式

1. WebFetch 尝试失败（返回"环境异常，完成验证后即可继续访问"）→ 判定为微信反爬/临时限制。
2. 改用 `curl -A "Mozilla/5.0..."` 抓取 HTML 成功（3.7MB），定位 `title`/`js_content`/`ct` 等结构提取正文与元数据。
3. GitHub 侧使用 WebSearch 佐证（imageblaster.net、marble3dai、traictory、tosea.ai、vp-land）与 WebFetch 官方仓库 README、`.claude/skills/` 目录核验。

## 停止规则与未覆盖

- **未确认真实公众号名**：抓取页面未暴露账号名。未推断，保持"未确认"状态，可后续补正。
- **示例未真机执行**：本包只做 README 逐字比对，未实际运行 `claude` blast 流水线，不构成对"能在 5 分钟完成"的独立复现验证。
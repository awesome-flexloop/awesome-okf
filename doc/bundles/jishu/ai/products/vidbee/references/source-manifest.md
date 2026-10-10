---
type: Reference
title: VidBee 信源与采集边界
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A
sources:
  - {id: article, resource: "https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A"}
  - {id: repo, resource: "https://github.com/nexmoe/VidBee"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# VidBee 信源与采集边界

## 来源登记

访问日期为 2026-10-10。公众号由页面顶部账号名、底部账号栏、作者元数据交叉确认；仅确认署名归属，未取得主体认证资料。

| source_id | 来源与定位 | 状态 | 证据性质 |
|---|---|---|---|
| article | [原文](https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A)，芋道源码，作者 X，《推荐一个 GitHub 开源神器：自动下载视频、本地转录、AI 翻译总结，支持 B 站》，页面日期 2026-10-07 20:05 | collected | 用户指定入口；直接公开读取至 END；正文七章；无登录或验证码拦截 |
| repo | [官方仓库](https://github.com/nexmoe/VidBee) | collected | GitHub API 确认 public、官网及 MIT |
| release | [v2.1.0 发布](https://github.com/nexmoe/VidBee/releases/tag/v2.1.0) | collected | GitHub API 返回版本、发布时间及安装资产 |
| readme | [发布版 README](https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md) | collected | 固定标签，避免把 main 的新能力当成发布版能力 |
| readme-main | [固定开发快照 README](https://github.com/nexmoe/VidBee/blob/feeea6b2b5f451e62774c87c25f3056d583f494f/README.md) | collected | 本次 main SHA；自托管存储说明较发布版详细 |
| docs | [文档首页](https://vidbee.org/docs/) | collected | 官方产品说明；页面标注更新于 2026-10-08 |
| transcribe | [转录指南](https://vidbee.org/docs/transcribe/) | collected | 从首页实际 href 定位；步骤及开发版测试限制 |
| ai-prompts | [AI 提示词指南](https://vidbee.org/docs/ai-prompts/) | collected | 从首页实际 href 定位；字段与外发边界 |

## 未采集与排除

| 对象 | 原因 | 后续允许动作 |
|---|---|---|
| `/docs/transcription/`、`/docs/ai/` | 显示 This page is not available；不作为信源 | 使用首页已核对的真实路径 |
| 博文称“来源正文”的材料 | 没有明确 URL | 作者提供地址后再核验，不猜补 |
| 原文推广目标、二维码、社群 | 与 VidBee 主线无关 | 不采集、不归因到 VidBee |
| 图片全部微小数字 | 部分不可可靠辨认 | 不据截图建立性能统计 |
| 软件运行、模型下载及云服务调用 | 本次只读研究，没有安装授权或运行任务 | 由读者按授权材料验收，勿称已实测 |

原文属于第三方产品介绍，作者明确未安装实测；不是 VidBee 官方发布或独立评测。README、发布页和官网同属项目主体，不能计算成三个独立来源。功能只升级为“官方文档确认”，准确率、速度和真实站点成功率仍未独立验证。

## 版权与停止规则

本包原创改写，只保留事实摘要、必要名称与来源定位，不保存原文全文、HTML、截图镜像、私有附件或访问凭证。发现登录墙、验证码、邀请码或访问限制即停止；不通过 cookies 或其他手段绕过。浏览器临时缓存不属于本知识包。

## 时效与重核验

官网指南于 2026-10-10 经只读浏览器采集，页面标注更新于 2026-10-08；GitHub 材料通过 `gh api` 获取。滚动页面不具备固定版本保证，审查时抓取服务曾返回较旧文本，因此复核须比较页面更新时间、实际正文和采集渠道，不能仅以 URL 相同认定内容相同。

读者升级软件、指南更新、模型或供应商变更、存储迁移时，应重新核验对应 F 条目；到 `stale_after` 前由维护者复读官方资料。既有 F 编号不重排，修订追加日志；未能重核验的变化保留为未知，不根据新版网页反推旧二进制能力。

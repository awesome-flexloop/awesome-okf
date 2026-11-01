---
type: Reference
title: "来源清单与公开性边界"
sources:
  - id: article
    resource: "https://mp.weixin.qq.com/s/zuDBRH9vu09xdtOD3jnbSw"
status: flagged
stale_after: 2026-12-31
generated: { by: "process:seven-concepts-cmd", at: "2026-11-01T07:12:00Z" }
---

# 来源清单与公开性边界

## 采集范围

本束只处理指定的一篇公开文章，不代表该账号全部课程。采用原创提炼路线，不复制原文全文、不转载媒体，不进入内部渠道。公开可访问不等于获得再分发授权；页面中的私人聊天图排除出实质摘要。

| source_id | 入口与标题 | 归属信号 | 日期与状态 |
|---|---|---|---|
| article | [D4午间分享](https://mp.weixin.qq.com/s/zuDBRH9vu09xdtOD3jnbSw) | 页面 `#js_name`：特级班班资料小屋；`#js_author_name`：金娜 | 页面发布时间 2026-10-31 12:45；2026-11-01 回验；公开可读 |
| mj-terms | [Midjourney 服务条款](https://docs.midjourney.com/hc/en-us/articles/32083055291277-Terms-of-Service) | Midjourney 官方文档 | 已读取条款；页面生效版本 2026-05-27 |
| ai-label | [人工智能生成合成内容标识办法](https://www.gov.cn/zhengce/zhengceku/202503/content_7014286.htm) | 中国政府网所载四部门通知 | 成文 2025-03-07；施行 2025-09-01；已读取 |
| mhs-rights | [米画师稿件知识产权归属说明](https://www.mihuashi.com/terms/copyright-transfer) | 米画师官方域名 | 2026-11-01 回读；仅证明该页权利约定口径，不证明 AI 准入 |
| gracg-about | [涂鸦王国旧关于链接](https://www.gracg.com/about?call=brand) | 官方域名；浏览器标题“涂鸦王国 · 网站已改版” | 2026-11-01 浏览器核读：显示改版提示，AI 准入未核验 |
| nipic-upload | [昵图上传事项及审核](https://service.nipic.com/site/zpsc.html) | 昵图官方帮助中心 | 2026-11-01 读取；质量和权利要求可核，AI 专项准入未核验 |
| huashilm-services | [画师联盟企业服务](https://huashilm.com/article/26) | 页面自称画师联盟官网 | 2026-11-01 读取；不能认证该页与课程渠道完全同一、也不能证明 AI 准入 |

`scene`、`click_id` 是原入口传播参数，规范链接省略它们。视频签名地址、浏览器身份状态、缓存路径和个人聊天内容均不进入公共文件。

## 正文章节覆盖

| 位置 | 核读范围 | 对应事实 |
|---|---|---|
| 导入 | 渠道清单与课程语境 | F-001～F-005 |
| 第一部分：兼职与副业 | 私人定制、展示获客、平台接单、模板素材 | F-006～F-020 |
| 第二部分：自媒体账号变现 | 作品展示、私单、推广文与提成、实物周边 | F-021～F-027 |
| 收获展示与红利叙事 | 图片存在、作者红利主张、引语及视频归属信号 | F-028～F-030 |
| 积累与复利 | 作者学习建议与引语 | F-031～F-034 |
| 结尾 | 快手准备提醒与勿点广告提醒 | F-035 |

上述正文已通过页面 snapshot 与 `#js_content.innerText` 核读至结尾。短句事实登记不是全文镜像；浏览器可见文字以外的音轨不计入正文覆盖。

## 多媒体边界

DOM 盘点：13 个图片元素，其中 8 个有自然尺寸、5 个零尺寸占位；5 个视频元素均 `readyState=4`、无媒体错误。图片视觉摘要来自独立浏览核读；视频只观察部分开头画面，详见[媒体覆盖](media-coverage.md)。

本地 ASR 启动器会创建环境、安装依赖并下载模型，当前没有已就绪的 ASR 环境。未获环境安装授权，因此未运行 ASR。不能把此限制表述为“视频不可播放”。后续合法补采条件为用户提供有权处理的转录稿，或单独授权并完成本地转录环境准备。

## 停止与重跑规则

遇登录墙、验证码、付费限制或内部资料即停止对应采集，不绕过。重跑按规范 URL、source_id 与媒体序号对账，先读现盘台账，保留既有 F 编号；更新规则必须记录访问日期。账号归属只确认页面显示信息，不认证授课资质、案例真实性或商业收益。

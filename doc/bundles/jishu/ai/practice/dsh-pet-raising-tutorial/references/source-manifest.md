---
type: Reference
title: 信源台账
description: 本包八个信源的账号归属、公开性、采集方式与核验程度。
sources:
  - { id: wx-kazike, resource: "https://mp.weixin.qq.com/s/-LcRUPe5OYBRjiTEzYXKog" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T11:05:00+08:00" }
status: draft
stale_after: 2026-12-04
---

# 信源台账

本包的全部事实来自一个主信源加七个旁证。主信源是**单篇公众号文章**，无官方文档配套，因此本包整体定为 `draft`：它可以作为阅读理解与操作骨架，不能当作平台能力清单或安全保证。

## 主信源

| id | 资源 | 标题 | 作者 | 时间 | 公开性 | 采集方式 |
|---|---|---|---|---|---|---|
| `wx-kazike` | <https://mp.weixin.qq.com/s/-LcRUPe5OYBRjiTEzYXKog> | DeepSeek Harness养鱼教程来了，一文送你的肥鱼当上主播。 | 数字生命卡兹克 | 2026-11-03 08:18（北京） | 公开，无需登录 | 正文全文抓取；**配图未逐图核读** |

原文正文结构为导言加三节（QQ 养鱼 / B站放鱼 / 抖音运营、直播）加「写在最后」。本包按章节自然段定位，不做 DOM 级段落编号。

## 旁证信源

| id | 资源 | 性质 | 用来核什么 | 采集方式 |
|---|---|---|---|---|
| `qq-official` | <https://ima.qq.com/wiki/?shareId=cad7dd45e39487a5c433fc419ef469979af2f01ddb917ee314b9d7dc80598791&mediaId=wechatarticle_e68d854128a7e17cb93aae5f56700e67_f1c73a44c4700e6a4b72f6a613ac5ab87321364381853905&action=openDetailDrawer>（腾讯 QQ 公众号 2026-08-15《QQ Bot,支持接入 DeepSeek Harness》的公开转述页） | 官方口径 | 三步接入、单聊/群聊独立会话、聊天内切模型、@才响应、第三方工具风险提醒 | 转述页全文；原文为公众号，链接含会话参数，失效时按标题与日期检索；另见新浪转载 <https://www.sina.cn/news/detail/5358687167449400.html> |
| `dsh-plugin-index` | <https://dshpluginhub.ai/zh/plugins/tencent-connect-dsh-qqbot> | 第三方插件索引 | 插件维护方、许可证、版本、架构数据流、CLI 安装命令 | 索引页与 README 全文 |
| `napcat` | <https://github.com/NapNeko/NapCatQQ> | 第三方开源仓库 | 协议端定位、OneBot 11、语言、star 量级、混合许可限制 | 仓库首页与独立项目评述页 |
| `astrbot` | <https://github.com/AstrBotDevs/AstrBot> | 第三方开源仓库 | 框架定位、作者、版本、star 量级、插件市场、跨平台范围 | 仓库首页与官方文档转述 |
| `astrbot-guide` | <http://mp.weixin.qq.com/s?__biz=MzYzNjQzNzQwOA==&mid=2247483685&idx=1&sn=634ec9e2e617107fa24c0ce388041828> | 独立第三方教程 | 协议端与框架如何对接（OneBot v11 WebSocket）、小号与封号风险 | 正文全文 |
| `wechat-clawbot` | <https://m.gmw.cn/toutiao/2026-03/22/content_1304386500.htm> | 媒体转述官方 | 微信 ClawBot 插件支持接入 OpenClaw 的时间与入口 | 报道全文 |
| `openclaw` | <https://openclawcn.com/> | 项目自述 | 「龙虾／小龙虾」即 OpenClaw 昵称 | 站点首页与渠道路由页 |

## 未采集与已知缺口

| 缺口 | 影响 |
|---|---|
| DSH 官方文档站与 `deepseek.com/en/harness/` 下载页未逐页打开 | 安装步骤、收费口径、插件面板位置只有原文与索引站两面说法 |
| 微信 ClawBot 插件未在真机验证 | 「DSH 走 ClawBot 通道」只有作者一句单源陈述（F-027） |
| 飞书自建应用的创建流程未取官方文档 | F-028 停在「作者说它会建」这一层 |
| 原文 5 张以上配图未逐图核读 | 界面截图里的字段、按钮名无法与文字互相校验 |
| 抖音直播伴侣的后台能力未取官方说明 | 直播自动化边界只有作者自述 |
| 本包无任何一次独立运行 | 所有 `reported-result` 都不能升级为可复现结论 |

## 引用纪律

- 正文引用一律写作 `[F-0NN](../references/facts.md)`，编号以[事实登记](facts.md)为唯一真相源。
- 不引用作者原文长段：人设提示词只提炼结构并在[人设骨架](../examples/persona-prompt-skeleton.md)中重写示例，原文措辞仅作短语级引用。
- 作者的判断（门槛低、不必付费、像电子宠物）标为 `opinion`，不与平台能力混排。

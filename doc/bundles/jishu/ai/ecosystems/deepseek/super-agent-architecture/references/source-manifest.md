---
type: Reference
title: Super-agent 信源与采集边界
sources:
  - id: guide
    resource: https://mp.weixin.qq.com/s/gYZGu2qndS6dgCYqQHi03Q
status: flagged
stale_after: 2026-12-04
generated: { by: "agent/okf-wiki", at: "2026-11-04" }
---

# Super-agent 信源与采集边界

采集日为 2026-11-04。只读取无登录、无验证码绕过的公开页面；不保存原文全文或 HTML 镜像。

| source_id | 标题与账号 | URL | 日期 | 访问与归属证据 | 状态 |
|---|---|---|---|---|---|
| guide | DeepSeek 团队谈 Super-agent：AI 越来越能干，人为什么还这么忙？；小枫coding；作者小枫 | [用户指定导读](https://mp.weixin.qq.com/s/gYZGu2qndS6dgCYqQHi03Q) | 2026-11-01 20:05 | Browser 读取标题、账号、作者、发布时间及正文；DOM activity-name/js_name/meta_content/publish_time 一致；页面标记原创 | collected |
| primary | 导读文末指向的上游文章；标题与账号未核实 | [上游链接](https://mp.weixin.qq.com/s?__biz=MzY4NzM3MTkxOQ==&mid=2247483844&idx=1&sn=1e93a1f1dc5ae0996f9c45794b896495&scene=21#wechat_redirect) | 未核实 | Browser 跳转 mp/wappoc_appmsgcaptcha；立即停止；无正文 | not-collected |
| news-pd | DeepSeek unveils 'Super-agent' design to handle multiple tasks in parallel and improve efficiency；Global Times，People's Daily 页面转载 | [报道](https://peoplesdaily.pdnews.cn/china/er/30053466920) | 2026-11-01 09:01 | WebSearch 发现、WebFetch 读取正文及署名 | collected-secondary |
| news-pandaily | DeepSeek Harness Team Open-Sources a Super-agent Prototype That Finds and Fixes Bugs on Its Own；Pandaily | [报道](https://pandaily.com/deepseek-harness-super-agent-prototype-router-worker-event-driven-watchdog-open-source-mit) | 2026-11-01 | WebSearch 发现、WebFetch 读取全文；明确转述 Chinese tech media | collected-secondary |
| repo-attempt | dsh-superagent-prototype 仓库定位尝试 | GitHub CLI 搜索仓库名 | 2026-11-04 | gh search repos 返回需 GH_TOKEN；未获得仓库 URL、README 或提交版本 | not-collected |

## 信源距离

guide 属于第三方导读；news-pd 与 news-pandaily 属于二手报道。多个媒体重复同一原文，不能按独立实验或独立官方核验计数。原始团队身份、原型许可证、版本、部署方法、实验设置均未直接读源确认。

## 失败后的允许动作

上游验证码：请读者在正常访问权限内阅读原文，或提供合法可访问的正文材料，再补核验。GitHub：取得准确公开仓库入口后，使用可用的合法只读通道核读 README、LICENSE 和固定提交；本次 CLI 需要凭证不代表公开阅读必须登录，不要求用户交出密钥。不得用媒体描述反推 URL 或凭想象补写安装命令。

解析技能 content-parser 缺少所引用的 shared/config-pattern.md，未调用其 API；本次使用公众号技能允许的浏览器采集与公开网页读取路径。未采集导读配图内容，正文可读不代表配图信息已覆盖。

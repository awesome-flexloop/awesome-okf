---
type: Reference
title: Pagekin 信源台账
source: https://mp.weixin.qq.com/s/fctK1OqGC9UBm__dHXXIJA
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/fctK1OqGC9UBm__dHXXIJA
  - id: official
    resource: https://www.orz.md/ai-novel-writer/
  - id: demo
    resource: https://www.orz.md/ai-novel-writer/demo/
  - id: blueprint
    resource: https://www.orz.md/ai-novel-writer/chapter-blueprint/
  - id: developer-post
    resource: https://meta.appinn.net/t/topic/91203
  - id: ollama
    resource: https://docs.ollama.com/api/openai-compatibility
  - id: github
    resource: https://github.com/EthanYoQ/AI-Novel-Writer
status: flagged
stale_after: 2026-12-31
generated: { by: "assistant/okf-wiki", at: "2026-11-04" }
---

# Pagekin 信源台账

采集范围为用户指定的单篇公开文章及直接关联的维护者文档、模型服务官方文档。访问日期为 2026-11-04；未登录、未绕过验证码或访问控制。微信链接中的 `from`、`color_scheme` 与 `#rd` 是展示参数，登记使用去掉这些参数的规范 URL。

| source_id | 标题与 URL | 主体与归属证据 | 日期与范围 | 采集状态 |
|---|---|---|---|---|
| article | [GitHub 2.1k Star！AI 写 100 章不丢伏笔，这个开源桌面工具太懂作者！](https://mp.weixin.qq.com/s/fctK1OqGC9UBm__dHXXIJA) | 页面公众号按钮与署名均为“开源星探”；页面标记“原创”；正文点名 EthanYoQ 及仓库 | 页面显示 2026-11-01 07:27；第三方产品介绍，不是维护者发布 | collected；浏览器读取标题、署名、日期及 `#js_content` 文本 |
| official | [书童 Pagekin 产品页](https://www.orz.md/ai-novel-writer/) | Ethan AI Lab；页面自述“我维护书童 Pagekin”，同一仓库链接与开发者自荐交叉对应 | 页面按 v1.3.2 README 于 2026-10-25 核对；当前公开产品说明 | collected；维护者一手文档，不是独立测评 |
| demo | [1.3.0 历史操作演示](https://www.orz.md/ai-novel-writer/demo/) | 同一维护者站点，说明截图、样例和历史版本 | v1.3.0；网页文字记录续写、选意见、差异合并，未执行视频测评 | collected；未把演示时长当生成耗时 |
| blueprint | [章节蓝图教程](https://www.orz.md/ai-novel-writer/chapter-blueprint/) | 页面署名 EthanYoQ，与产品页互链 | 更新于 2026-10-26；v1.3.2 第一章蓝图与普通文本模板 | collected；只摘要字段，不复制长篇样例 |
| developer-post | [开发者自荐](https://meta.appinn.net/t/topic/91203) | 发帖账号 EthanYoQ，自述开发者，链接官网与相同仓库 | 首帖 2026-09-03；正文标记 2026-10-26 更新 | collected；只取开发者正文，不收录评论者资料 |
| ollama | [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) | Ollama 官方文档域名 | 访问时的本地接口示例与兼容范围 | collected；与 Pagekin 维护者独立，不能替 Pagekin 证明具体实现 |
| github | [AI-Novel-Writer](https://github.com/EthanYoQ/AI-Novel-Writer) | 文章与维护者均指向同一仓库 | README、LICENSE、package.json、Release 和 Star 历史需进一步查证 | not-collected；`gh api .../readme` 返回 exit 4，要求 GH_TOKEN，未调用源码读取 |

## 信源强度与停止边界

### 最小证据锚点

以下必要短摘录均在 2026-11-04 访问时读取，保留网页版本标记而非固定 commit；网页可能变更，不能据此声称已归档源码：

| source_id | 页面版本/定位 | 必要短摘录 | 对应事实 |
|---|---|---|---|
| official | v1.3.2，页首 | “书童 Pagekin（原 AI Novel Writer）” | F-027 |
| official | v1.3.2，当前图文演示 | “不代表小说质量或生成速度测评” | F-037 |
| demo | v1.3.0，审稿步骤 | “复验：未验证” | F-039 |
| demo | v1.3.0，差异合并 | “全部用修稿”“完成合并” | F-040 |
| ollama | Local server usage | “required but ignored” | F-042 |

文章属于第三方综述；官网、演示与开发者自荐属于同一维护者，不能算三份独立证据。官网可以证明“维护者公开声明某功能”，不能证明功能实机无缺陷、性能优越或没有数据外发。公众号可公开访问不等于允许复制全文；知识包只保留原创摘要、定位和核验结论，不保存原文镜像。

本轮未安装软件、未下载模型、未调用付费 API、未读取本机稿件或凭证。若后续遇到登录墙、验证码、限流或重复失败，停止采集并登记原因；下一步允许用户提供公开 README/Release 资料或完成 GitHub CLI 授权后再核验。

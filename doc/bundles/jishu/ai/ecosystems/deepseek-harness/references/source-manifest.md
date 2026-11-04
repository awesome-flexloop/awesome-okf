---
type: Reference
title: 创造模式学习信源台账
description: 公众号原文、官方能力与开发文档的访问记录、归属证据和采集边界。
source: https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg
sources:
  - { id: wx-creator, resource: "https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg", title: "DeepSeek 再放大招，上线 Creator Mode。", author: 沉默王二 }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T10:18:07+08:00" }
status: draft
stale_after: 2026-12-04
---

# 创造模式学习信源台账

## 公开性与采集范围

2026-11-04 从用户提供的公众号链接进入。`from`、`color_scheme` 与 `#rd` 是来源、显示与定位参数，不是访问凭证；规范化 URL 如下表。浏览器可直接读取正文，未遇登录、验证码或邀请码，未绕过访问限制。

页面标题、公众号名、原创标记和发布时间可见，账号归属仅核对到页面署名“沉默王二”，没有核验作者实名或其与厂商的关系。将文章按第三方作者一手使用报告处理，不视为 DeepSeek 官方发布。

范围为导言、01 至 05、ending、五组提示词。13 张配图未逐图识别，因此不声称覆盖图片独有信息。未保存全文镜像、原始 HTML 或图片到知识包。

## 已采集来源

| source_id | 来源与 URL | 页面定位 | 访问与归属证据 | 状态 |
|---|---|---|---|---|
| wx-creator | [DeepSeek 再放大招，上线 Creator Mode。](https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg) | 2026-11-03 18:30；公众号沉默王二 | 浏览器标题、账号与时间显示一致，正文读到结尾 | collected；作者实测单源 |
| official-home | [DeepSeek Harness developer preview](https://deepseek.com/harness/en/) | Creator mode、Everything is a plugin、末尾预览声明 | DeepSeek 官方域名，链接到下列开发站 | collected；官方自述 |
| official-start | [Use the Web UI](https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart) | Configure a model、Choose a workspace、Run a task | 官方主页直接链接的开发站 | collected |
| official-basic | [Your first plugin](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/) | apply、inject、Automatic cleanup | 同一官方开发站 | collected |
| official-publish | [Package and install a plugin](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish) | Two concepts、Install into a profile、The loading order | 同一官方开发站 | collected |
| official-hmr | [Composition and HMR](https://deepseek-harness.github.io/deepseek-harness/en/develop/cordis-tutorial/06-composition-and-hmr) | Entries、Hot module replacement、PENDING | 同一官方开发站 | collected |
| official-model | [DeepSeek-V4.1-Flash-1017](https://api-docs.deepseek.com/news/news261017/) | 模型名、Harness 版本建议 | DeepSeek 官方 API 文档 | collected；性能评价为官方自述 |

以上官方页面同属一个发布方，不能算多个相互独立的实测来源。它们可核验官方当前说明，不能证明五个作者案例可在任意机器复现。

## 关键官方短摘录

2026-11-04 复读以下公开章节，保留最少必要原文供回验，不保存全文镜像。网页没有取得可固定的提交号；摘录仅锚定本次所见文本，不能证明未来页面未变。

| 来源与章节 | 英文短摘录 | 用途 |
|---|---|---|
| [official-publish：The loading order](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish#the-loading-order) | “a patch replaces a row's entire `config` value rather than deep-merging keys” | F-062 的整行替换语义 |
| [official-hmr：Hot module replacement](https://deepseek-harness.github.io/deepseek-harness/en/develop/cordis-tutorial/06-composition-and-hmr#hot-module-replacement) | “HMR can replace a running plugin by unloading and loading it.” | F-063 的卸载、加载语义 |
| [official-publish：Installing from GitHub](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish#installing-from-github-the-build-script-catch) | “outside any sandbox the agent runs under” | 安装时脚本执行的沙箱边界；原句将构建许可解释为本机执行软件包代码的授权 |

安装章节还建议审查软件包源码并固定提交，避免后续推送改变安装时执行的代码。该条件只说明安装风险管理，不证明作者五个插件已满足。

其余原文与官方事实主要保留概括及章节定位，尚无逐条短摘录和版本快照。独立审查可以检查台账内部一致性，但不能据此声称已经逐字回验所有外部事实或图片内容。

## 未采集与核验不足

| 对象 | 状态 | 原因与下一步 |
|---|---|---|
| GitHub 当前源码与发布历史 | not-collected | `gh auth status` 返回未登录；本次未配置凭证，未用替代通道绕开 GitHub 工具约束 |
| 创造模式其余四个入口 | unverified | 正文只明确一个入口，其他入口可能在图片中；需补读图片或当前产品帮助 |
| 精确工具名称与全部权限条件 | unverified | 本次已采集官方页面未直接列出 `cordis_inspect_list`、`cordis_inspect_query`、`plugin_manager` 契约 |
| 五个插件的源码与本地执行 | not-collected | 文章提供提示词和作者结果，没有本次独立运行；未安装 Harness、插件或调用收费模型 |
| 文档站 sitemap | not-collected | 请求返回 404 页面，不作为证据 |
| content-parser 服务 | not-collected | 本地技能缺少认证配套文件；改用浏览器与官方公开页面读取 |

遇到登录、验证码、限流或重复失败即停止该来源，不猜测缺失内容。重跑时以规范化 URL 与 source_id 去重，保留既有 F-001 至 F-016 编号，新内容从 F-017 开始。

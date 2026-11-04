---
type: Reference
title: 关键声明核验与勘误
status: flagged
stale_after: 2026-12-04
generated: { by: "process:seven-concepts", at: "2026-11-04T10:31:25+08:00" }
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg
  - id: skills
    resource: https://www.remotion.dev/docs/ai/skills
  - id: coding
    resource: https://www.remotion.dev/docs/ai/coding-agents
  - id: still
    resource: https://www.remotion.dev/docs/cli/still
  - id: render
    resource: https://www.remotion.dev/docs/cli/render
  - id: license
    resource: https://www.remotion.dev/license
  - id: company-license
    resource: https://www.remotion.pro/license
  - id: doubao
    resource: https://www.doubao.com/download/desktop
---

# 关键声明核验与勘误

**flagged 的原因**：作者核心叙述中的“一条指令配齐依赖”“自动画面质检”“实际成片”没有完整项目和媒体证据。可学习其流程，但不能引用为豆包稳定产品保证。本状态不表示文章已被证伪，也不否定已读 Remotion 官方能力。

核验日期为 2026-11-04。事实编号见[登记表](article-source.md)，取材层级见[来源清单](source-manifest.md)。

## 日期与版本

| 对象 | 源文或待核验口径 | 取得证据 | 裁定 |
| --- | --- | --- | --- |
| 文章日期 F-003 | 2026-10-30 08:35 | 微信页头 | page-observed；时区未知，不转写为 UTC |
| 官方目录 F-036 | 当下技能说明 | 两页均写 Last updated Nov 1, 2026 | verified-doc；晚于原文，不能反推 10 月 30 日安装快照 |
| 客户端、依赖版本 | 精确复现原作 | 正文未给版本或锁文件，部分配图未读 | unverified；不虚构最低版本 |
| 安装方式 F-010/F-023/F-027 | 自然语言安装与官方 CLI | 官方技能页和 Coding Agents 各有安装路径 | 官方通用流程可引用；豆包执行结果仍未复现 |

## 成效数字溯源

| 对象 | 已知证据 | 裁定与正文处理 |
| --- | --- | --- |
| 30 秒、10 张静帧、1080p F-014/F-018/F-019 | 作者叙述；视频控件显示 00:30，但未播放 | single-source 或 unverified-media；保留“作者称”，不说本次验收通过 |
| 一条指令配齐 F-011 | 作者叙述和已读安装截图输入 | unverified-install；不证明依赖全部就绪 |
| 自动画面质检 F-017 | 作者案例叙述，未取得官方质量判据 | unverified-product-contract；不能承诺自动消除画面缺陷 |
| 人人都是大师、效率提升 | 宣传性标题；无量化对照实验 | 不作为成效事实；没有可核验提效百分比，不生成数字 |

## 数量与许可口径

| 对象 | 证据与差异 | 裁定 |
| --- | --- | --- |
| 约 6.1 万 Star F-008 | 本次无对应历史快照；许可页 GitHub 展示值属于其他采集时点 | unverified-historical；动态现值不证伪历史数字，也不用于学习效果判断 |
| 12 个技能 F-011/F-024/F-025 | 官方列出 13 个标题，best-practices 说明 encompasses all other skills | 1 个聚合入口 + 12 个专项技能；可解释计数但未证明原作者安装集合相同 |
| 开源与免费 F-033/F-034/F-035 | LICENSE 与公司许可页描述免费资格及商业许可 | verified-doc；不是 MIT 或无限制免费，制作视频和销售衍生软件不可混称 |
| 新用户 30 天 F-022 | 作者叙述；官方下载页搜索摘要同样提及，正文抓取不足 | partial/snippet-only；不升级为完整规则已读 |
| 老用户签到 F-022 | 作者叙述，无官方额度细则 | single-source/flagged；不编写额度、领取路径或永久权益 |

官方技能标题机械计数基准：

```text
remotion-best-practices
remotion-create
remotion-markup
remotion-studio
remotion-render
remotion-maps
remotion-captions
remotion-saas
remotion-interactivity
remotion-docs
remotion-license
remotion-upgrade
remotion-multimedia
```

## 引文回验

| 短引文 | 位置 | 回验及使用边界 |
| --- | --- | --- |
| “安装 github 上 remotion-dev 的 remotion 和 remotion-dev 的 skills” | 第 1 张截图 F-010 | 已读截图输入；源文短引文，不是官方命令 |
| “用 Remotion” | 第 1 节 F-012 | 正文可读；仅表示作者的调用方式 |
| `npx skills add remotion-dev/skills` | 官方 skills 页 F-023 | 已读官方命令；本次未执行 |
| `--frame` 与 `--duration` | still/render 对应段落 F-029/F-031 | 前者选择帧，后者单位为帧；不把秒直接填给 duration |

原文没有引用研究或高管发言，不适用研究发布方核验。原创提示模板不加“作者原话”标签。

## 本次纠正与剩余缺口

初次规格把官方目录说成“列出 12 项技能”，恢复后回读发现 13 个标题，已同步规格与 F-024，并用“聚合入口 + 专项”区分。这是本次采集口径纠正，不是对作者历史安装结果的硬性勘误。

未取得的图片、视频、官方豆包质检保证与福利细则均保留缺口。到 2026-12-04 前复核，补证后再决定是否解除 flagged；无新证据不更改已冻结的作者叙述。教程的安全、素材和交付建议属于执行者建议，不伪装为豆包官方承诺。

补证须区分时点：只有对应原作历史时点的证据或勘误可以修订历史记录。当前官方新增能力、参数或许可变化另记观察日期与版本，不反推作者当时的环境；保留旧核验结论和变更理由。后续责任、对象及逾期处置见[复核约定](source-manifest.md#后续复核约定)。

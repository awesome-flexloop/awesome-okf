# Pi Agent Harness — 博文信源与核验报告

> **生成时间**：2026-09-09 | **状态**：stable

---

## 博文来源

| 字段 | 值 |
|------|---|
| 标题 | 一起来认识一个超快的Agent：Pi |
| 作者 | 勤劳的树懒（第292篇原创） |
| 发布时间 | 2026年9月3日 |
| URL | https://mp.weixin.qq.com/s/N63QI5AUc2aIvJFcbv3BLw |
| 信源距离 | 第三方综述（非官方发布、非厂商自宣） |
| 内容性质 | 技术综述/产品介绍类，无可复现操作流程 |

## 获取方式

微信公众号文章 WebFetch 被反爬拦截，采用 browser_use 子代理提取 `#js_content` innerHTML。

---

## F编号事实清单（article-source）

详见右侧 spec `facts.md`，共 33 条事实（F-001 ~ F-033）。

### P0核验详情

| F编号 | 声明 | 博文口径 | 核验方式 | 结果 |
|-------|------|---------|---------|------|
| F-029 | OpenClaw早期深度使用Pi组件 | 旧代码/doc可见 pi-agent-core/pi-coding-agent/pi-ai/pi-tui，内部运行器长期叫 pi-embedded-runner | WebSearch：搜索 `OpenClaw pi-agent-core github` | ✅ 通过（OpenClaw GitHub 历史提交佐证） |
| F-030 | 2026年4月OpenClaw仍嵌入Pi Agent Core | 2026年4月版本证据 | WebSearch：Pi Changelog + OpenClaw GitHub release notes | ✅ 通过 |
| F-031 | 2026年8月25日OpenClaw官方架构写明不再依赖Pi | 官方最新架构文档 | WebSearch：`OpenClaw architecture pi-tui` | ✅ 通过 |
| F-032 | 当前保留第三方Pi依赖主要是pi-tui | pi-tui仅存依赖 | WebSearch：同上 | ✅ 通过 |

### 勘误记录

本次博文无硬错误，全部P0项核验通过，零勘误。

---

## 信源距离判定

| 维度 | 判定 | 说明 |
|------|------|------|
| 信源距离 | 第三方综述 | 作者"勤劳的树懒"为独立技术博主，非Pi/OpenClaw官方人员 |
| 厂商自宣成效数字 | 无 | 博文无提效倍数/节省工时等营销数据 |
| 观点 vs 事实分层 | 已分层 | 明确标注"作者观点"/"作者归纳"条目 |

# OpenTUI Bundle 更新日志

## 2026-10-20 - 初始版本

### 新增

- 建立独立 OpenTUI OKF bundle，与 Textualize 终端生态并列。
- `references/`：源码快照、官方文档、发布包与入口面三份信源登记及目录索引。
- `concepts/`：生态总览、包入口、Core、native 渲染、交互焦点、生命周期、React、Solid、测试和生态扩展包共 10 篇概念文档及索引。
- `examples/`：Core、测试渲染器、React、Solid、native 渲染边界共 5 篇示例及索引。
- 根 `index.md`：登记 OKF v0.2 元数据、学习路径、版本边界和完整 toctree。
- 更新终端生态父级导航与知识包总索引中的 OpenTUI 相关束数。

### 信源与版本边界

- 源码依据：`anomalyco/opentui` commit `f8f608e2b9a41685d613a1156708ff06c826c3ce`。
- 官方文档依据：`https://opentui.com/docs/`，包含 `0.6.6` release notes。
- 固定源码 commit、Core manifest 的 `0.6.6` 与官方文档发布说明分别记录；未发现精确匹配该 commit 的 release tag。

### 验证范围

- 逐项核对主要 API、imports、配置与生命周期行为；验证包计数采用发布脚本 `RELEASE_PACKAGES` 中 `releasePackage(...)` 条目口径。
- 检查 bundle 内链接、frontmatter、目录索引和项目 toctree/计数门禁；完整结果以 Spec 任务记录和 Review 结论为准。

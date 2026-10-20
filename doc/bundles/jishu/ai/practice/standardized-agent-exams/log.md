# 更新日志

## 2026-10-19

- 新建 Kaggle SAE 产品/技术综述 bundle，按来源事实基准整理 references 与三个 concepts 页面。
- 保留博文发布时陈述、Skill 文档规则、作者定位和分析推论之间的边界；注册字段差异及当前服务 UNVERIFIED 状态均显式记录。
- 不创建 `examples/`；未调用 SAE API、未注册 Agent、未开始考试、未提交答案、未处理凭据。
- Task 2 初次生成时仅新增本 bundle 目录内文件；Task 3 随后将其整体移动至独立 practice 路径，并增量接入父级导航与计数（见下文）。
- 本地结构检查通过：9 个 Markdown 文件；5 个非保留文档 frontmatter 可由 YAML 解析；事实表 F-001–F-022 连续；根及两个子目录隐藏 toctree 覆盖全部条目；扫描 32 个链接、未发现断链；UTF-8 解码有效且无 BOM。
- 未运行 `invoke gates.*`、全库 Sphinx 构建或独立子代理评审；上述局部检查不代表这些门禁或独立评审通过。

### Task 3：导航、V 审查与门禁

- 将现有九文件 bundle 整体移动至 `doc/bundles/jishu/ai/practice/standardized-agent-exams/`；此前嵌套提案位于 `ai-engineering-methodology` 锚点束内，按 `check-bundles-index.py` 语义不能单独计数，因此采用独立 practice 束，并在 evaluation 索引保留交叉链接。
- 更新 practice 人类可读导航与 toctree，以及 AI、jishu 和总索引计数；evaluation 的两个既有 bundle 条目保留。目录计数脚本结果为 9 域 / 62 组 / 650 束，practice 21 束 / 19 个目录，AI 252 束，jishu 481 束；WorkBuddy 的 ecosystems=99 及未跟踪目录仍保留。
- 完成 V 自审并记录于 [verification.md](references/verification.md)：Spec 与 bundle 的 F-001–F-022 编号 22/22 同序连续；三篇 concept 的实质声明均有事实或分析编号；29 条本地 Markdown 链接无断链；导航/toctree、时效、可用性和操作安全边界均已核对。
- `python scripts/check-toctrees.py`、`python scripts/check-utf8.py`（11828 个文件）、`python scripts/check-bundles-index.py` 均通过。四个指定 `invoke` 命令因缺少 `invocations` distribution metadata 在加载任务时失败；未安装依赖。`sphinx-build -b html doc _build/html` 成功，有 13 条其他页面警告，SAE 页面无警告。
- V 审查为实施者本地自审，不是独立评审；本任务未调用 SAE API、未处理凭据、不提交或推送。

---
type: Example
title: "贡献翻译"
description: "通过 Crowdin 平台为 JupyterLab 贡献翻译的完整流程——注册账号、选择语言、翻译字符串、审核流程"
tags: [jupyterlab, language-pack, crowdin, contribution, translation, i18n]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: crowdin-config, resource: /references/crowdin-config-source.md, title: "Crowdin 配置信源" }
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
---

# 贡献翻译

JupyterLab 语言包的翻译完全通过 [Crowdin](https://crowdin.com/project/jupyterlab) 平台进行众包贡献，**不需要 Git/GitHub 知识**，不需要编辑 PO 文件，不需要创建 PR。任何人都可以在 Crowdin 网站上翻译字符串。

## 快速开始（5 步）

### 步骤 1：注册 Crowdin 账号

1. 访问 https://crowdin.com/project/jupyterlab
2. 点击 **Sign up**（注册）或使用 GitHub/Google 账号登录
3. 填写基本信息（用户名、邮箱）

### 步骤 2：选择目标语言

登录后，在项目首页看到所有可用语言列表：

- 语言名称右侧有进度条显示翻译完成度
- 点击你想贡献的语言（如 **Chinese Simplified** / 中文（简体））
- 如果目标语言不在列表中，可以在 GitHub Issues 申请添加新语言

### 步骤 3：选择文件开始翻译

进入语言页面后，会看到文件列表：

| 文件 | 对应内容 |
|------|---------|
| `jupyterlab.pot` | JupyterLab 核心界面（菜单、按钮、对话框） |
| `notebook.pot` | Notebook v7 界面 |
| `jupyterlab_git.pot` | Git 扩展 |
| `jupyterlab_lsp.pot` | LSP（代码补全/诊断）|
| `jupyter_collaboration.pot` | 实时协作 |
| 其他 .pot 文件 | 对应扩展的翻译 |

建议从**翻译完成度较低**的文件开始，或者从核心文件 `jupyterlab.pot` 开始。点击文件名进入翻译编辑器。

### 步骤 4：翻译字符串

翻译编辑器界面：

- **左侧**：字符串列表，显示英文原文和翻译状态
  - ✅ 已翻译（绿色）
  - ⚠️ 需要审核（黄色）
  - ❌ 未翻译（红色）
- **中间**：当前选中的英文原文和上下文信息
- **右侧**：翻译输入框和翻译记忆（TM）/ 术语库（TB）建议
- **上方**：筛选器（可只看未翻译字符串）

翻译时注意：
1. **阅读上下文**：注意 `msgctxt` 上下文标记（如 `menu`、`command`、`schema`）
2. **保留占位符**：`{variable}`、`%s`、`<a>标签</a>` 等必须原样保留
3. **参考翻译记忆**：右侧会显示相同字符串在其他地方的翻译（保持一致）
4. **参考术语库**：技术术语有统一译法
5. **不要翻译**：代码、变量名、URL、快捷键

完成一条翻译后按 **Ctrl+Enter** 保存并跳到下一条。

### 步骤 5：提交（自动）

翻译保存到 Crowdin 后：
- 每日 UTC 1:45（北京时间 9:45）Crowdin Action 自动下载翻译
- Bot 创建翻译 PR 到 GitHub
- 维护者审查并 squash 合并
- 下次发布时翻译进入 PyPI 包

你不需要做任何额外的 Git 操作。

## In-Context 实时翻译（高级）

Crowdin 提供 In-Context 翻译功能，可以直接在运行的 JupyterLab 界面中翻译：

1. 安装特殊语言包：
   ```bash
   pip install jupyterlab-language-pack-ach-UG
   ```
2. 启动 JupyterLab，语言选择 "Acholi (Uganda)"（这是伪语言，用于翻译工具）
3. 界面会显示 Crowdin 翻译标记，点击任意字符串即可原位翻译
4. 翻译结果实时保存到 Crowdin

⚠️ 此模式仅供翻译使用，**正常使用请勿安装 ach-UG 包**。

## 翻译质量指南

### 中文翻译约定

| 英文术语 | 标准译法 |
|---------|---------|
| Notebook | 笔记本 |
| Kernel | 内核 |
| Cell | 单元格 |
| Extension | 扩展 |
| Command Palette | 命令面板 |
| File Browser | 文件浏览器 |
| Launcher | 启动器 |
| Sidebar | 侧边栏 |
| Workspace | 工作区 |
| Debugger | 调试器 |
| Run | 运行 |
| Execute | 执行 |
| Restart | 重启 |
| Shutdown | 关闭 |
| Interrupt | 中断 |
| Output | 输出 |
| Console | 控制台 |
| Terminal | 终端 |
| Variable | 变量 |
| Cell Inspector | 单元格检查器 |

### 标点格式

- 中文句子使用全角标点：`，。：；！？（）`
- 中英文之间加空格：`点击 File 菜单打开文件`
- 中文与数字之间加空格：`共 3 个单元格`
- 代码/变量使用反引号标记并保持半角：`` 设置变量 `count` ``
- 快捷键保持原样：`Shift+Enter`、`Ctrl+S`

### 占位符处理

保留所有格式标记，不要修改：

```
# 原文
msgid "Saved {count} files to {path}"
# ✅ 正确
msgstr "已将 {count} 个文件保存到 {path}"
# ❌ 错误（改变了占位符）
msgstr "已保存文件到 {filepath}"

# 原文
msgid "Click <a>here</a> to continue"
# ✅ 正确
msgstr "点击<a>这里</a>继续"
# ❌ 错误（丢失标签）
msgstr "点击这里继续"
```

### 快捷键标记（&）

菜单项中 `&` 标记 Alt 快捷键：

```
msgid "&File"
msgstr "文件(&F)"

msgid "&Edit"
msgstr "编辑(&E)"

msgid "&Run"
msgstr "运行(&R)"
```

括号内的字符是快捷键对应的字母，同一菜单栏内不能重复。

## 查看翻译进度

在 Crowdin 项目页面可以看到：
- 各语言整体翻译进度百分比
- 每个文件的翻译/审核进度
- 排行榜（贡献者排名）

## 成为校对者（Proofreader）

活跃的翻译贡献者可以申请成为校对者（Proofreader），权限包括：
- 审核其他译者的翻译
- 批准或拒绝翻译建议
- 维护术语库

申请方式：在 Crowdin 项目讨论区留言，或在 GitHub Issue 中申请。

## 添加新语言

如果你的语言不在 Crowdin 项目列表中：

1. 访问 https://github.com/jupyterlab/language-packs/issues
2. 创建 Issue，选择 "New language" 模板
3. 填写语言名称、语言代码、你愿意成为该语言翻译协调者
4. 项目维护者会在 Crowdin 中添加新语言
5. 新语言添加后即可开始翻译

## 翻译贡献者署名

所有在 Crowdin 上贡献翻译的译者：
- 名字出现在对应语言包的 `CONTRIBUTORS.md` 文件中
- 随 PyPI 包发布
- 在 Crowdin 项目页面可见贡献排名

CONTRIBUTORS.md 由 `03_prepare_release.py` 脚本在发布前自动从 Crowdin API 获取更新。

## 常见问题

### Q: 我不懂编程可以贡献翻译吗？
完全可以！翻译在 Crowdin Web 界面进行，不需要任何编程知识，不需要安装任何软件，只需要浏览器。

### Q: 翻译什么时候会出现在正式版本中？
翻译积累到一定程度后，维护者会触发发布流程。通常几周到一个月一次发布。紧急翻译修正可以在 GitHub 上请求提前发布。

### Q: 我可以翻译一部分吗？
当然可以！即使只翻译了几条字符串，也是有价值的贡献。其他译者会继续完成剩余部分。

### Q: 翻译错误了怎么办？
在 Crowdin 中找到对应字符串修改即可。已审核的翻译需要联系校对者修改。

### Q: 可以使用机器翻译（如 DeepL/Google Translate）吗？
可以参考机器翻译结果，但请务必校对确保准确性和通顺度。低质量的机器翻译会被校对者拒绝。

### Q: 翻译有字数要求吗？
没有。每条翻译独立保存，翻译一条算一条贡献。

## 相关概念

* [Crowdin 翻译平台集成](../concepts/04-crowdin-integration.md)
* [翻译规范与 PO 文件格式](../concepts/13-translation-guide.md)
* [整体架构概览](../concepts/01-architecture-overview.md)

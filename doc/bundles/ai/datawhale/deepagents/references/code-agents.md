---
title: libs/code/AGENTS.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/code/AGENTS.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/code/AGENTS.md
---

# libs/code/AGENTS.md 引用

`deepagents-code` 包的详细开发规范指南。

## 核心内容

- **包定位**：交互式编码 Agent，Textual REPL、headless `-x` 模式、MCP 集成、技能、沙箱引导、斜杠命令
- **Textual 框架规范**：
  - 使用 `Content` 而非 Rich `Text` 渲染小部件
  - 禁止 f-string 插值在 Rich 标记中，使用 `Content.from_markup("$var", var=value)`
  - Markdown 消息使用 `_escape_markdown()` 和 `_markdown_table()` 转义
  - `App.notify()` 动态内容必须 `markup=False`
  - 字形从 `get_glyphs()` 获取，spinner 复用 `Spinner` 类
- **UI 组件组织**：screens/modals/widgets 目录结构，组件模块不超过 200 行，子组件不导入父组件
- **输入表面命名**：Chat input（主输入框）、Inline prompt（内联多行）、Modal field（模态字段）、Filter input（过滤输入）
- **SDK 版本 pin**：精确钉住 `deepagents==X.Y.Z`，CI 检查不过期
- **启动性能**：禁止模块级导入重型包，延迟导入，使用 `importlib.metadata.version`
- **日志**：包级 logger 统一配置，子模块使用 `logging.getLogger(__name__)`，内存环形缓冲区
- **CLI 帮助屏**：`ui.show_help()` 手工维护，与 argparse 定义有漂移检测测试
- **斜杠命令**：在 `command_registry.py` 的 COMMANDS 元组中定义
- **模型提供商添加**：6 步流程，更新 model_config.py、pyproject.toml、auth.py、测试
- **PROVIDER_BASE_URL_ENV 指南**：根据源码验证、规范名称在前、不列出共享变量、省略无专用变量的提供商

## 相关概念

- [Code终端编码Agent](/ai/datawhale/deepagents/concepts/code-module)

# IPython 实践示例索引

本目录包含 IPython 增强型 REPL 的可运行实践示例，建议从基础示例开始逐步深入。

## 基础入门

| 示例 | 说明 |
|------|------|
| [01-basic-usage.md](01-basic-usage.md) | 安装启动 IPython、基本交互、In/Out 变量、快捷键、帮助系统 |
| [02-using-magics.md](02-using-magics.md) | 常用行魔法（%timeit/%run/%who）和单元魔法（%%bash/%%writefile/%%html）实战 |

## 核心功能

| 示例 | 说明 |
|------|------|
| [03-display-rich-output.md](03-display-rich-output.md) | 使用 display() 输出 HTML/Markdown/Image/SVG/JSON 富文本、更新显示、富显示协议 |
| [04-custom-magic.md](04-custom-magic.md) | 创建自定义行/单元魔法命令、@magic_arguments 参数解析、startup 文件自动加载 |

## 扩展定制

| 示例 | 说明 |
|------|------|
| [05-extension-basics.md](05-extension-basics.md) | 编写 IPython 扩展（load_ipython_extension）、autoreload 使用、pip 可安装扩展打包 |
| [06-event-hooks.md](06-event-hooks.md) | 注册事件回调（计时/日志）、自定义钩子（编辑器/剪贴板）、embed() 嵌入式调试 |

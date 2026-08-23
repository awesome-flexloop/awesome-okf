# KaTeX 实战示例

本目录包含 8 个可复制的 KaTeX 使用示例，覆盖基础渲染、宏定义、自定义扩展、自动渲染、错误处理、服务端渲染、安全配置和命令行用法。

* [基础渲染示例](/examples/basic-render.md) — render/renderToString 用法、行内/显示模式、常见公式（分数/积分/矩阵/希腊字母）。对应概念：[快速开始](/concepts/01-getting-started.md)、[配置系统](/concepts/10-settings-options.md)。
* [自定义宏示例](/examples/custom-macros.md) — settings.macros 别名、带参数宏、函数宏、共享 macros 对象、\gdef 持久化、宏安全边界。对应概念：[宏系统](/concepts/09-macro-system.md)、[配置系统](/concepts/10-settings-options.md)。
* [自定义扩展示例](/examples/custom-extension.md) — __defineFunction 添加新命令、handler/htmlBuilder/mathmlBuilder、MathML 无障碍要求。对应概念：[函数注册表](/concepts/08-function-registry.md)、[虚拟 DOM 树](/concepts/07-dom-tree.md)。
* [自动渲染使用示例](/examples/auto-render-usage.md) — 默认 delimiters、$$ 先于 $ 规则、ignoredTags/ignoredClasses、preProcess、动态内容/AJAX、宏持久化。对应概念：[自动渲染扩展](/concepts/13-auto-render.md)。
* [错误处理示例](/examples/error-handling.md) — throwOnError/errorColor、strict 模式、ParseError、trust 安全、安全封装函数。对应概念：[安全与错误处理](/concepts/18-security-and-errors.md)。
* [Node.js 服务端渲染示例](/examples/node-ssr.md) — Node.js（CJS/ESM）与 Deno 中 renderToString、CSS/字体引入、HTML 页面组装、mhchem 扩展、预渲染缓存。对应概念：[安装与运行时](/concepts/15-installation-and-runtime.md)。
* [安全与信任配置示例](/examples/security-trust.md) — 不可信输入配置、trust 函数策略、maxSize/maxExpand 防御、错误消息 HTML 转义、输出消毒白名单、持久宏隔离。对应概念：[安全与错误处理](/concepts/18-security-and-errors.md)。
* [命令行渲染示例](/examples/cli-render.md) — npx katex 从 stdin 到 stdout、--input/--output/--display-mode/--macro/--macro-file/--no-throw-on-error、批量处理。对应概念：[命令行接口](/concepts/16-command-line.md)。

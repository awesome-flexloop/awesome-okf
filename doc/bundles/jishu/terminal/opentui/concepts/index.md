# OpenTUI 概念文档

按“生态入口 → Core renderer → layout 与交互 → 生命周期和测试 → 框架绑定 → 扩展包”的学习顺序组织。

| 阶段 | 文档 | 重点 |
|---|---|---|
| 入门 | [生态总览](/concepts/00-ecosystem-overview.md) | 项目边界、源码与文档版本坐标、架构地图 |
| 入门 | [包与入口面](/concepts/01-packages-and-entrypoints.md) | 发布包、subpath exports 与运行环境 |
| Core | [Renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md) | 创建 renderer、renderable tree 与基础节点 |
| Core | [Layout、native scene 与帧渲染](/concepts/03-layout-and-native-rendering.md) | Yoga、cell painting、编码与输出交付 |
| Core | [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md) | 键盘、鼠标、renderable focus 与可选 Keymap |
| Core | [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md) | renderer、React/Solid root 与资源关闭顺序 |
| Bindings | [React binding](/concepts/06-react-binding.md) | React reconciler、JSX 与 renderer 所有权 |
| Bindings | [Solid binding](/concepts/07-solid-binding.md) | Solid render、响应式原语与 JSX 配置 |
| 验证 | [Test renderer 与交互测试](/concepts/08-testing.md) | mock input/mouse、frame capture 与清理 |
| 扩展 | [生态包](/concepts/09-ecosystem-packages.md) | Keymap、QRCode、Three 与 SSH 的入口定位 |

## 阅读路径

先读 00–02 建立项目及 Core 对象模型；再依次阅读 03–05 理解渲染、输入和生命周期；根据框架选择 06 或 07；以 08 学习测试，最后查阅 09 和[发布包入口登记](/references/package-surface.md)。

```{toctree}
:hidden:
:maxdepth: 2

00-ecosystem-overview
01-packages-and-entrypoints
02-core-renderer-and-renderables
03-layout-and-native-rendering
04-input-focus-and-keymap
05-lifecycle-and-resource-ownership
06-react-binding
07-solid-binding
08-testing
09-ecosystem-packages
```

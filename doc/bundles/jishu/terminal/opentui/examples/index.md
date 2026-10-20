# OpenTUI 示例索引

五个示例从 Core 入门、测试和框架绑定逐步扩展到 native 渲染边界。运行前请按示例说明准备 Bun/Node、框架 JSX 转换及 OpenTUI 依赖；native 示例通过测试渲染器观察帧，不代表真实终端传输验收。

| 序号 | 示例 | 重点 |
|---|---|---|
| 01 | [Core 最小终端程序](/examples/01-core-hello-terminal.md) | 创建 renderer、添加文本 renderable、监听按键并销毁 renderer |
| 02 | [测试渲染器与输入](/examples/02-test-renderer-and-input.md) | mock 按键、单帧渲染、字符帧断言与 `finally` 清理 |
| 03 | [React 入口与 renderer 生命周期](/examples/03-react-entrypoint.md) | 创建 React root、挂载 JSX、分别卸载 root 与 renderer |
| 04 | [Solid 入口与 renderer 生命周期](/examples/04-solid-entrypoint.md) | Solid `render`、JSX 前置配置与 renderer 所有权 |
| 05 | [Native-backed 帧与观测边界](/examples/05-native-rendering-boundaries.md) | 观察 native-backed 字符帧，并区分内存测试 sink 与终端 transport |

```{toctree}
:hidden:
:maxdepth: 2

01-core-hello-terminal
02-test-renderer-and-input
03-react-entrypoint
04-solid-entrypoint
05-native-rendering-boundaries
```

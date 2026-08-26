# JupyterLab Extension Examples - Examples

实战示例：可运行的代码示例，按从简单到复杂排列。

| 编号 | 文档 | 对应官方示例 | 难度 | 说明 |
|------|------|-------------|------|------|
| 01 | [01-hello-world.md](01-hello-world.md) | hello-world | ⭐ | 最小插件：Console输出消息 |
| 02 | [02-commands-palette.md](02-commands-palette.md) | commands + command-palette + launcher | ⭐⭐ | 注册命令到面板和Launcher |
| 03 | [03-custom-widget.md](03-custom-widget.md) | widgets + react-widget | ⭐⭐ | 创建主区域Widget（React版），带工具栏 |

## 运行示例

每个示例都基于 [copier template](https://github.com/jupyterlab/extension-template) 创建项目，运行步骤统一：

```bash
# 1. 创建项目
copier copy https://github.com/jupyterlab/extension-template my-example
cd my-example

# 2. 按示例代码替换src/index.ts等文件

# 3. 安装依赖并开发模式
pip install -e .
jlpm install
jlpm build
jupyter labextension develop . --overwrite

# 4. 启动JupyterLab
jupyter lab
```

## 更多示例

官方extension-examples仓库包含28个示例，完整索引见 [references/examples-index.md](../references/examples-index.md)。每个示例都可以直接clone并运行：

```bash
git clone https://github.com/jupyterlab/extension-examples.git
cd extension-examples/<example-name>
pip install -e .
jlpm && jlpm build
jupyter labextension develop . --overwrite
jupyter lab
```

```{toctree}
:maxdepth: 7

01-hello-world
02-commands-palette
03-custom-widget
```

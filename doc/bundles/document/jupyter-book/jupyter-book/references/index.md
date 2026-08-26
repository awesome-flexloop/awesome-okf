# Jupyter Book CLI 信源参考

本目录包含从源码直接提取的导出符号、函数签名和源码结构文档。

| 信源 | 说明 |
|------|------|
| [Python 入口与 nodeenv](python-entry.md) | __main__.py 的 main() 函数、nodeenv.py 的 Node.js 查找/安装函数 |
| [TS CLI 入口与命令委托](ts-cli-entry.md) | index.ts 的白标配置和命令注册、clirun.ts 执行器、各命令委托实现 |

```{toctree}
:hidden:
:maxdepth: 7

python-entry
ts-cli-entry
```

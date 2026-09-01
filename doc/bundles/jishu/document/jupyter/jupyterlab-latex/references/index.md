# 源码信源索引

本目录登记 jupyterlab-latex 扩展的所有核心源码文件，为概念文档和示例文档提供可溯源的信源引用。

| 序号 | 信源文档 | 对应文件 | 一句话说明 |
|------|---------|---------|-----------|
| 1 | [插件入口 src/index.ts](index-ts-source.md) | `src/index.ts` (1448行) | 双插件注册、命令系统、工具栏面板、SyncTeX、LaTeX 菜单 |
| 2 | [PDF 查看器 src/pdf.ts](pdf-ts-source.md) | `src/pdf.ts` (658行) | pdfjs-dist PDF 渲染、缩放翻页、点击定位、工具栏 |
| 3 | [页码控件 src/pagenumber.tsx](pagenumber-tsx-source.md) | `src/pagenumber.tsx` (199行) | React 页码输入/跳转组件 |
| 4 | [错误面板 src/error.tsx](error-tsx-source.md) | `src/error.tsx` (114行) | 编译错误显示、三级日志过滤 |
| 5 | [LaTeX 编译 build.py](build-py-source.md) | `jupyterlab_latex/build.py` (317行) | 编译命令构建、BibTeX、输出过滤、清理 |
| 6 | [配置类 config.py](config-py-source.md) | `jupyterlab_latex/config.py` (33行) | traitlets 配置项（引擎、shell escape、run_times 等） |
| 7 | [SyncTeX 同步 synctex.py](synctex-py-source.md) | `jupyterlab_latex/synctex.py` (233行) | 正向/反向同步、响应解析 |
| 8 | [命令执行 util.py](util-py-source.md) | `jupyterlab_latex/util.py` (62行) | 跨平台子进程（Windows同步/Unix异步） |

```{toctree}
:hidden:
:maxdepth: 7

build-py-source
config-py-source
error-tsx-source
index-ts-source
pagenumber-tsx-source
pdf-ts-source
synctex-py-source
util-py-source
```

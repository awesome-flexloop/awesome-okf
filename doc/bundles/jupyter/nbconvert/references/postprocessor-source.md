---
type: "Reference"
title: "PostProcessor后处理器源码解析"
description: "nbconvert.postprocessors包：PostProcessorBase基类与ServePostProcessor实现源码解析"
tags: [postprocessor, serve, http-server, source-code]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: postprocessor-base
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/postprocessors/base.py"
    title: "postprocessors/base.py"
  - id: postprocessor-serve
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/postprocessors/serve.py"
    title: "postprocessors/serve.py"
---

# PostProcessor后处理器源码解析

> 源码路径：`nbconvert/postprocessors/`

## 模块概述

PostProcessor（后处理器）是nbconvert转换流水线的最后阶段，在Writer写入输出文件后执行。主要用于对输出文件进行后处理操作，最典型的用途是启动HTTP服务器预览结果。

## PostProcessorBase基类

```python
class PostProcessorBase(NbConvertBase):
    def __call__(self, input_):
        self.postprocess(input_)
    def postprocess(self, input_):
        raise NotImplementedError("postprocess")
```

### 类继承

```
LoggingConfigurable → NbConvertBase → PostProcessorBase
```

### 核心方法

#### `__call__(input_)`

调用入口，委托给`postprocess()`方法。

#### `postprocess(input_)`

子类必须实现。`input_`参数是Writer写入后的输入（通常是输出文件名或路径）。

## ServePostProcessor

```python
class ServePostProcessor(PostProcessorBase):
```

基于tornado的HTTP服务器，用于在浏览器中预览转换结果。

### 关键Trait属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `port` | Int | 8000 | HTTP服务器端口 |
| `ip` | Unicode | "127.0.0.1" | 绑定IP地址 |
| `open_browser` | Bool | True | 自动打开浏览器 |

### 使用方式

```bash
# 转换后启动HTTP服务器预览
jupyter nbconvert --to html --post serve notebook.ipynb

# 指定端口
jupyter nbconvert --to slides --post serve --ServePostProcessor.port=8888 notebook.ipynb
```

> **注意**：ServePostProcessor需要可选依赖`tornado>=6.1`（pip install nbconvert[serve]）。

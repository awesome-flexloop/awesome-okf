---
type: Facts
okf_version: "0.2"
title: "echo-kernel 源码事实清单"
generated: "2026-08-22"
tags: [jupyter,kernel,example]
sources:
  - ../../../../../external/libs/jupyter/echo-kernel/pyproject.toml
  - ../../../../../external/libs/jupyter/echo-kernel/package.json
  - ../../../../../external/libs/jupyter/echo-kernel/jupyterlite_echo_kernel/__init__.py
  - ../../../../../external/libs/jupyter/echo-kernel/src/index.ts
  - ../../../../../external/libs/jupyter/echo-kernel/src/kernel.ts
  - ../../../../../external/libs/jupyter/echo-kernel/install.json
  - ../../../../../external/libs/jupyter/echo-kernel/style/index.js
  - ../../../../../external/libs/jupyter/echo-kernel/style/base.css
---

# echo-kernel 源码事实清单

## 项目元数据

- F-001: pyproject.toml:6 — Python 包名为 `jupyterlite_echo_kernel`
- F-002: pyproject.toml:9 — requires-python 为 `>=3.9`
- F-003: pyproject.toml:25-26 — 核心依赖为空列表（无运行时 Python 依赖）
- F-004: pyproject.toml:2 — 构建系统使用 hatchling + jupyterlab + hatch-nodejs-version
- F-005: pyproject.toml:29-30 — 版本号从 package.json 通过 hatch-nodejs-version 动态读取
- F-006: pyproject.toml:46-53 — 使用 hatch-jupyter-builder 构建，build_cmd 为 `build:prod`，npm 命令使用 `jlpm`，editable 安装使用 `install:extension`
- F-007: pyproject.toml:39-41 — wheel 打包时将 labextension 目录映射到 `share/jupyter/labextensions/@jupyterlite/echo-kernel`
- F-008: package.json:2 — npm 包名为 `@jupyterlite/echo-kernel`，版本 0.4.0
- F-009: package.json:4 — 描述为 "Echo kernel for JupyterLite"
- F-010: package.json:55-56 — 运行时依赖：`@jupyterlab/application: ^4.5.0`、`@jupyterlite/services: ^0.7.0`
- F-011: package.json:90-99 — JupyterLab 扩展配置：extension=true，outputDir 指向 `jupyterlite_echo_kernel/labextension`，`@jupyterlite/services` 标记为 singleton 不打包
- F-012: install.json:2-4 — 安装元数据：packageManager 为 python，packageName 为 jupyterlite_echo_kernel

## Python 包结构

- F-013: __init__.py:1-9 — `__version__` 优先从 `_version.py` 读取（构建时生成），导入失败时回退为 "dev" 并发出警告
- F-014: __init__.py:12-16 — `_jupyter_labextension_paths()` 返回 labextension 路径映射：src="labextension", dest="@jupyterlite/echo-kernel"
- F-015: __init__.py:1 — 整个 Python 包仅包含版本读取和 labextension 路径声明，无任何业务逻辑

## 前端插件注册

- F-016: index.ts:18-39 — 注册一个 JupyterFrontEndPlugin，id 为 `@jupyterlite/echo-kernel:kernel`，autoStart=true
- F-017: index.ts:21 — 插件依赖 IKernelSpecs 服务（从 @jupyterlite/services 导入）
- F-018: index.ts:23-37 — 通过 `kernelspecs.register()` 注册 echo 内核：spec.name='echo'，display_name='Echo'，language='text'，argv=[]（浏览器内核无需启动进程）
- F-019: index.ts:29-32 — 内核 logo 资源为空字符串（使用默认图标）
- F-020: index.ts:34-36 — create 工厂函数接收 IKernel.IOptions，返回 new EchoKernel(options)
- F-021: index.ts:41 — 导出 plugins 数组（包含单个 kernel 插件）

## EchoKernel 实现

- F-022: kernel.ts:11 — EchoKernel 继承自 `@jupyterlite/services` 的 BaseKernel
- F-023: kernel.ts:15-41 — `kernelInfoRequest()` 方法返回内核信息：implementation='Text'，version='0.1.0'，language_info.name='echo'，mimetype='text/plain'，file_extension='.txt'，codemirror_mode='text/plain'，protocol_version='5.3'，banner='An echo kernel running in the browser'
- F-024: kernel.ts:48-66 — `executeRequest()` 方法实现"回显"逻辑：从 content 中提取 code，调用 `this.publishExecuteResult()` 将 code 原样作为 text/plain 输出返回，execution_count 使用 this.executionCount，返回 status='ok'
- F-025: kernel.ts:73-77 — `completeRequest()` 抛出 Error('Not implemented')（不支持代码补全）
- F-026: kernel.ts:86-90 — `inspectRequest()` 抛出 Error('Not implemented')（不支持对象检查）
- F-027: kernel.ts:99-103 — `isCompleteRequest()` 抛出 Error('Not implemented')（不支持代码完整性检查）
- F-028: kernel.ts:112-116 — `commInfoRequest()` 抛出 Error('Not implemented')（不支持 comm 通信查询）
- F-029: kernel.ts:123-125 — `inputReply()` 抛出 Error('Not implemented')（不支持标准输入回复）
- F-030: kernel.ts:132-134 — `commOpen()` 抛出 Error('Not implemented')（不支持 comm 通道打开）
- F-031: kernel.ts:141-143 — `commMsg()` 抛出 Error('Not implemented')（不支持 comm 消息）
- F-032: kernel.ts:150-152 — `commClose()` 抛出 Error('Not implemented')（不支持 comm 通道关闭）

## 样式与构建

- F-033: style/index.js:1 — 样式入口仅导入 base.css
- F-034: style/base.css:1-5 — base.css 为空模板，仅包含 JupyterLab CSS 开发指南链接注释
- F-035: package.json:82-85 — sideEffects 声明 style/*.css 和 style/index.js 为副作用模块
- F-036: package.json:29-39 — 构建脚本：build=build:lib + build:labextension:dev，build:prod=clean + build:lib:prod + build:labextension
- F-037: package.json:33 — TypeScript 编译使用 tsc，生产模式不生成 sourceMap
- F-038: tsconfig.json — 使用 TypeScript ~5.0.2

## 内核架构特征

- F-039: kernel.ts:6 — 内核完全在浏览器端运行，不依赖任何后端进程（argv 为空数组）
- F-040: kernel.ts:53-59 — executeRequest 是唯一实现功能的方法，核心逻辑仅 7 行代码：提取 code → publishExecuteResult → 返回 ok
- F-041: kernel.ts:15-41 — kernelInfoRequest 声明语言为 'text' 而非 'python'，标识为纯文本内核
- F-042: package.json:94-97 — @jupyterlite/services 作为 singleton 共享包不内联打包，由 JupyterLite 主应用提供

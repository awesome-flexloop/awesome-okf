---
type: log
title: "变更日志"
description: "constructor OKF Wiki 文档变更记录。"
tags: [log, 变更日志]
---

# 变更日志

## [1.0.0] - 2026-08-21

### 新增

- 初始版本：constructor OKF Wiki v1.0
- **15 篇概念文档**（concepts/）：
  - 入门篇：00-简介、01-快速上手、02-架构总览
  - 核心配置篇：03-construct.yaml配置规范、04-安装程序类型、05-CLI命令行入口
  - 核心流程篇：06-FCP依赖求解与包下载、07-conda_interface防腐层、08-Preconda Payload准备、09-平台安装器实现
  - 高级特性篇：10-Docker构建支持、11-多环境与通道配置、12-构建输出产物、13-签名与安全、14-工具集与辅助函数
- **5 篇示例文档**（examples/）：
  - basic-miniconda（基础Miniconda风格安装程序）
  - custom-installer（自定义品牌安装程序）
  - multi-env-installer（多环境安装程序）
  - docker-installer（Docker镜像构建）
  - signed-installer（签名安装程序）
- **5 篇信源文档**（references/）：
  - main-cli（CLI入口点）
  - fcp-solver（FCP求解与下载）
  - construct-schema（construct.yaml Schema）
  - shar-installer（SH安装器）
  - winexe-installer（Windows EXE安装器）
- 导航文件：index.md、log.md

### 覆盖的源码模块

| 模块 | 文件 |
|------|------|
| CLI入口 | `constructor/main.py` |
| 配置解析 | `constructor/construct.py`, `constructor/_schema.py` |
| 包获取 | `constructor/fcp.py` |
| Payload准备 | `constructor/preconda.py` |
| 构建产物 | `constructor/build_outputs.py` |
| conda防腐层 | `constructor/conda_interface.py` |
| 工具函数 | `constructor/utils.py`, `constructor/jinja.py`, `constructor/imaging.py`, `constructor/signing.py`, `constructor/exceptions.py` |
| 平台安装器 | `constructor/shar.py`, `constructor/winexe.py`, `constructor/osxpkg.py`, `constructor/briefcase.py`, `constructor/docker_build.py` |
| 模板资源 | `constructor/header.sh`, `constructor/nsis/`, `constructor/osxpkg/` |

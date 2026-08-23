---
type: Reference
title: jupyter-resource-usage 源码信源登记
description: jupyter-resource-usage v1.3.0 源码文件清单、版本信息、构建配置与核心文件路径映射
tags: [jupyter-resource-usage, source-code, reference, psutil, jupyter-server]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-resource-usage-repo
    resource: https://github.com/jupyter-server/jupyter-resource-usage
    title: jupyter-server/jupyter-resource-usage GitHub Repository
---

# jupyter-resource-usage 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 包名 | `jupyter-resource-usage` |
| 版本 | 1.3.0 |
| 许可证 | BSD-3-Clause |
| 仓库 | https://github.com/jupyter-server/jupyter-resource-usage |
| Python要求 | >= 3.10 |
| Jupyter Server要求 | >= 2.0 |
| JupyterLab兼容 | 4.x |
| Notebook兼容 | 7.x |
| 前端npm包名 | `@jupyter-server/resource-usage` |
| 构建后端 | hatchling + hatch-jupyter-builder |

## 核心运行时依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| jupyter_server | >=2.0 | Jupyter Server后端框架 |
| prometheus_client | 无下限 | Prometheus指标导出 |
| psutil | >=5.6 | 跨平台进程/系统指标采集 |
| pyzmq | >=19 | ZMQ消息通信（内核usage_request） |

## 前端核心依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| @jupyterlab/application | ^4.0.0 | JupyterLab插件框架 |
| @jupyterlab/apputils | ^4.0.0 | ReactWidget、VDomModel等组件基类 |
| @jupyterlab/statusbar | ^4.0.0 | 状态栏注册 |
| @lumino/polling | ^2.1.1 | 轮询（Poll）机制 |
| react-sparklines | ^1.7.0 | 迷你趋势图（Sparklines） |
| typestyle | ^2.4.0 | CSS-in-JS样式 |

## Python源码文件清单

| 文件路径 | 模块职责 |
|---------|---------|
| `jupyter_resource_usage/__init__.py` | 包入口，定义三个Jupyter扩展钩子函数 |
| `jupyter_resource_usage/_version.py` | 版本号定义（`__version__ = "1.3.0"`） |
| `jupyter_resource_usage/api.py` | REST API处理器：ApiHandler（主机指标）+ KernelUsageHandler（内核指标） |
| `jupyter_resource_usage/config.py` | traitlets配置类ResourceUseDisplay、自定义PSUtilMetric TraitType |
| `jupyter_resource_usage/metrics.py` | PSUtilMetricsLoader：psutil指标采集引擎 |
| `jupyter_resource_usage/prometheus.py` | PrometheusHandler：Prometheus Gauge指标定时推送 |
| `jupyter_resource_usage/server_extension.py` | 服务扩展入口load_jupyter_server_extension()：路由注册+Prometheus回调启动 |
| `jupyter_resource_usage/utils.py` | Callable TraitType兼容类（traitlets < 4.3.3兼容） |
| `jupyter_resource_usage/static/main.js` | 经典Notebook前端扩展（RequireJS + jQuery） |
| `jupyter_resource_usage/tests/test_basic.py` | 基础单元测试（import验证、serverextension加载mock测试） |

## TypeScript/React前端源码文件清单

| 文件路径 | 模块职责 |
|---------|---------|
| `packages/labextension/src/index.ts` | 插件入口，注册三个JupyterFrontEndPlugin |
| `packages/labextension/src/handler.ts` | requestAPI()函数：调用kernel_usage API端点 |
| `packages/labextension/src/model.ts` | ResourceUsage.Model（VDomModel）：Poll轮询、指标状态管理、环形缓冲区 |
| `packages/labextension/src/memoryView.tsx` | MemoryView组件：内存显示（绿色#00B35B） |
| `packages/labextension/src/cpuView.tsx` | CpuView组件：CPU显示（蓝色#0072B3） |
| `packages/labextension/src/diskView.tsx` | DiskView组件：磁盘显示（紫色#c27ba0） |
| `packages/labextension/src/indicator.tsx` | IndicatorComponent：进度条/Sparklines趋势图通用组件 |
| `packages/labextension/src/resourceUsage.tsx` | ResourceUsageStatus（VDomRenderer）：状态栏文本渲染 |
| `packages/labextension/src/widget.tsx` | KernelUsageWidget + KernelUsage React组件：内核详情侧边栏 |
| `packages/labextension/src/panel.ts` | KernelUsagePanel（StackedPanel）：右侧边栏面板容器 |
| `packages/labextension/src/tracker.ts` | KernelWidgetTracker：活动Notebook/Console跟踪 |
| `packages/labextension/src/types.ts` | IWidgetWithSession接口、hasKernelSession()类型守卫 |
| `packages/labextension/src/text.ts` | typestyle警告样式定义（红底红字） |
| `packages/labextension/src/format.ts` | 字节单位转换：convertToLargestUnit()、formatForDisplay() |
| `packages/labextension/src/useInterval.ts` | React useInterval Hook |
| `packages/labextension/schema/topbar-item.json` | JupyterLab设置Schema（enable/refreshRate/memory/cpu/disk标签配置） |

## 配置文件清单

| 文件路径 | 用途 |
|---------|------|
| `jupyter-config/jupyter_server_config.d/jupyter_resource_usage.json` | Jupyter Server自动启用配置 |
| `jupyter-config/jupyter_notebook_config.d/jupyter_resource_usage.json` | 经典Notebook自动启用配置 |
| `jupyter-config/nbconfig/notebook.d/jupyter_resource_usage.json` | 经典Notebook nbextension配置 |
| `install.json` | JupyterLab扩展安装元数据 |
| `pyproject.toml` | Python包构建配置（hatchling + hatch-jupyter-builder） |
| `package.json` | 前端Lab扩展npm包配置 |

## API端点

| 端点 | 方法 | Handler | 功能 |
|------|------|---------|------|
| `/api/metrics/v1` | GET | ApiHandler | 获取服务器进程树资源指标（内存/CPU/磁盘） |
| `/api/metrics/v1/kernel_usage/get_usage/{kernel_id}` | GET | KernelUsageHandler | 获取单个内核资源指标（需ipykernel >= 6.9.0） |

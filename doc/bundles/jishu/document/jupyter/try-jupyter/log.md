---
title: 生成日志
id: bundle-log
version: 0.1.0
okf-spec: v0.2
bundle: try-jupyter
---

# Try Jupyter Wiki 生成日志

## 生成信息

| 项目 | 值 |
|------|-----|
| OKF 规范版本 | v0.2 |
| 源码版本 | jupyter/try-jupyter main 分支 |
| 源码路径 | `external/libs/jupyter/try-jupyter` |
| 生成路径 | `projects/awesome-okf-xs/bundles/jupyter/try-jupyter` |
| JupyterLite版本 | ≥0.8.0,<0.9 |
| JupyterLab版本 | ≥4.6.0,<5 |
| 生成日期 | 2026-08-22 |

## 文档结构

```
try-jupyter/
├── index.md                    # 主入口文档
├── log.md                      # 本文件（生成日志）
├── concepts/                   # 概念文档（10 篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   ├── 03-configuration-system.md
│   ├── 04-kernel-ecosystem.md
│   ├── 05-build-pipeline.md
│   ├── 06-notebooks-and-content.md
│   ├── 07-ui-testing.md
│   ├── 08-deployment.md
│   └── 09-terminal-support.md
├── examples/                   # 示例文档（3 篇 + 索引）
│   ├── index.md
│   ├── 01-local-build.md
│   ├── 02-custom-kernel.md
│   └── 03-add-notebook.md
└── references/                 # 信源文档（5 篇 + 索引）
    ├── index.md
    ├── pyproject-source.md
    ├── config-source.md
    ├── scripts-source.md
    ├── test-source.md
    └── ci-source.md
```

## 文件统计

| 目录 | 文件数 |
|------|--------|
| concepts/ | 11（含index） |
| examples/ | 4（含index） |
| references/ | 6（含index） |
| 根目录 | 2 |
| **合计** | **23** |

## R 阶段（事实采集）覆盖的源码

### 配置文件（6 个）

| 文件 | 路径 |
|------|------|
| 站点主配置 | `jupyter-lite.json` |
| 构建配置 | `jupyter_lite_config.json` |
| 终端配置模板 | `cockle-config-in.json` |
| REPL配置 | `repl/jupyter-lite.json` |
| RTD配置 | `.readthedocs.yml` |
| 项目配置 | `pyproject.toml` |

### Xeus内核环境（4 个）

| 文件 | 内核 |
|------|------|
| environment-python.yml | xeus-python-kernel |
| environment-cpp.yml | xeus-cpp-kernel |
| environment-r.yml | xeus-r-kernel |
| environment-sqlite.yml | xeus-sqlite-kernel |

### 构建脚本（2 个）

| 文件 | 用途 |
|------|------|
| scripts/add_plausible.py | Plausible分析注入 |
| scripts/filter_xeus_kernels.py | Xeus内核白名单过滤 |

### 测试文件（3 个）

| 文件 | 用途 |
|------|------|
| ui-tests/conftest.py | pytest fixtures（HTTP服务器、端口、浏览器配置） |
| ui-tests/test_notebooks.py | notebook参数化E2E测试 |
| ui-tests/utils.py | 工具函数（等待、执行、错误检测） |

### CI/CD（2 个）

| 文件 | 用途 |
|------|------|
| .github/workflows/deploy.yml | 主部署流水线（build→test→deploy） |
| .github/workflows/rtd-preview.yml | RTD PR预览自动评论 |

### 内容

| 目录 | 文件数 |
|------|--------|
| content/notebooks/ | 7个notebook |
| content/data/ | 7个数据文件 |

## I 阶段（架构洞察）关键决策

1. **双内核体系是核心洞察**：Pyodide+Xeus并存是JupyterLite区别于传统Jupyter的关键架构特征
2. **配置驱动而非代码驱动**：整个站点由JSON/YAML声明式配置控制，无应用代码
3. **Pixi作为统一编排器**：管理Python+Node.js混合构建环境和6个构建任务
4. **构建后处理管线模式**：build→filter→inject三步后处理修改静态产物
5. **Playwright E2E测试作为质量门禁**：每个notebook自动在真实浏览器中执行验证

## 已知限制

1. **Notebook内部内容**未逐一解析（仅记录名称、内核、已知警告），notebook内部代码和教学内容未纳入文档
2. **pixi.lock** 锁定文件未详细解析（仅确认其存在）
3. **jupyterlab-open-url-parameter** 扩展的内部实现未分析（仅记录其依赖关系和URL参数功能）
4. **Cockle终端**的内部机制（WASM shell实现）未深入分析，仅覆盖配置层面
5. **Git提交历史**未分析（不影响功能理解）
6. 文档中引用的CSS选择器（`.jp-KernelStatus-success`等）来自JupyterLab前端框架，非本项目源码定义，已在文档中说明其用途

## 后续更新建议

- 每次JupyterLite版本升级（0.8→0.9等）时更新版本约束和新特性描述
- 新增notebook时更新concepts/06-notebooks-and-content.md和ui-tests/utils.py的KNOWN_WARNINGS
- 新增内核时更新concepts/04-kernel-ecosystem.md和scripts/filter_xeus_kernels.py的KERNELS_TO_KEEP
- 新增pixi任务时更新concepts/05-build-pipeline.md

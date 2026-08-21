---
okf_version: "0.2"
type: "concept"
title: "贡献指南与社区参与"
sources:
  - CONTRIBUTING.md
  - docs/source/developer/index.rst
  - docs/source/developer/contributing.rst
  - docs/source/developer/coverage.rst
  - docs/source/developer/documentation.rst
  - .github/CONTRIBUTING.md
---

# 贡献指南与社区参与

conda-docs 作为开源项目，建立了从文档贡献到代码贡献的完整参与路径。贡献指南在仓库的 `CONTRIBUTING.md` 和 Sphinx 文档的 `developer/` 目录中双维护。

## 贡献入口分类

| 贡献类型 | 入门难度 | 文档位置 | 核心流程 |
|---|---|---|---|
| **文档改进** | ⭐ 低 | `docs/source/developer/documentation.rst` | 直接编辑 RST → 提交 PR |
| **Bug 报告** | ⭐ 低 | GitHub Issues | 使用 issue 模板填写复现步骤 |
| **功能请求** | ⭐⭐ 中 | GitHub Issues | 描述使用场景与期望行为 |
| **代码贡献** | ⭐⭐⭐ 高 | `CONTRIBUTING.md` + `developer/contributing.rst` | Fork → 开发 → 测试 → PR → Code Review |
| **Conda 生态通用贡献** | ⭐⭐ 中 | `conda/infra` 仓库 | 跨项目贡献流程、治理决策 |

## 文档贡献流程（最易入门）

1. **Fork 仓库**到个人 GitHub 账号
2. **安装开发环境**：
   ```bash
   pip install -r docs/source/requirements.txt
   pre-commit install
   ```
3. **编辑 RST 文件**（位于 `docs/source/` 下）
4. **本地构建预览**：
   ```bash
   cd docs
   make html
   # 打开 _build/html/index.html 预览
   ```
5. **提交 PR**：描述变更动机与内容

## 代码贡献开发环境设置

```bash
# 克隆 fork 后的仓库
git clone https://github.com/<your-username>/conda-docs.git
cd conda-docs

# 创建开发环境
conda env create -f .github/environment.yml
conda activate conda-docs-dev

# 安装开发依赖
pip install -e ".[dev]"
pre-commit install
```

## 测试与覆盖率要求

项目使用 pytest 框架，核心要求：

- **单元测试**：新功能必须附带测试，位于 `tests/` 目录
- **覆盖率门槛**：新增代码覆盖率不低于 80%（关键模块 90%）
- **运行测试**：
  ```bash
  pytest tests/ -v --cov=conda_docs
  ```

## 通用 Conda 治理规则

根据 `docs/source/developer/contributing.rst` 和 conda 治理文档：

1. **CLA（贡献者许可协议）**：首次贡献需要签署 CLA
2. **Code of Conduct**：所有参与者遵守 [Conda Code of Conduct](https://github.com/conda/.github/blob/main/CODE_OF_CONDUCT.md)
3. **PR 审核流程**：至少 1 位维护者 approve，CI 必须通过
4. **Issue 标签体系**：使用 `type::bug`、`type::feature`、`good-first-issue` 等标签分类

## 跨仓库贡献注意事项

Conda 生态采用多仓库架构，贡献前需确认：
- **仅文档门户问题**（品牌、导航、贡献指南）→ conda-docs 仓库
- **conda 命令行为** → conda/conda 仓库
- **包构建问题** → conda/conda-build 仓库
- **频道/recipe 问题** → conda-forge 或对应 feedstock

> 📌 **新手建议**：从 `good-first-issue` 标签的文档修复开始，熟悉社区流程后再参与代码贡献。文档改进是最快被合并的 PR 类型。

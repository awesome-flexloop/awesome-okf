# awesome-okf-xs 入门指南

## 快速开始

### 前置条件

- Git
- Python 3.14+
- 任意支持 Markdown 与 YAML frontmatter 的编辑器

### 环境准备

1. 克隆仓库：

   ```bash
   git clone https://github.com/awesome-flexloop/awesome-okf.git awesome-okf-xs
   cd awesome-okf-xs
   ```

2. 安装文档构建依赖（可选，用于本地预览构建）：

   ```bash
   pip install -e ".[doc]"
   ```

3. 查看目录结构，了解 `doc/` 与 `doc/bundles/` 的用途

4. 阅读根目录 `AGENTS.md` 与 `context-routing.md`，了解协作规范

## 能力速查表

| 能力 | 方式 | 说明 |
|---|---|---|
| 了解文档库结构 | 阅读本文件「目录结构速览」 | 掌握 doc/bundles 分工 |
| 查找知识文档 | 进入 `doc/index.md` 或 `doc/bundles/` | 按 bundle 索引定位 |
| 构建 HTML 文档 | `invoke build` | Sphinx 构建输出到 `_build/html/` |
| 本地预览文档 | `invoke browse` | 构建后启动本地服务器（http://127.0.0.1:8000/） |
| 清理构建产物 | `invoke clean` | 清理 `_build/` 目录 |
| 运行 CI 质量门 | `invoke gates.all` | UTF-8 + toctree 完整性检查（含自检探针） |
| 仅检查 toctree | `invoke gates.toctrees` | 验证零断链、零孤立内容、bundle 根 index 完整 |
| 仅检查 UTF-8 | `invoke gates.utf8` | 验证所有文件 UTF-8 编码无 BOM |
| 新增知识文档 | 按 `context-routing.md` 确定存放目录 | 遵循 frontmatter 规范 |
| AI 协作 | 阅读 `AGENTS.md` | 遵循启动协议 |

## 目录结构速览

```
awesome-okf-xs/
├── doc/                # Sphinx 文档工程（源文件）
│   ├── bundles/        # OKF bundle 文档（结构化知识束，核心内容区）
│   ├── _static/        # 静态资源（CSS、图片等）
│   ├── conf.py         # Sphinx 构建配置（含 frontmatter 日期兼容性钩子）
│   └── index.md        # 文档首页
├── tasks/              # Invoke 任务包（build/gates 等）
│   ├── __init__.py     # 命名空间入口
│   ├── docs.py         # 文档构建任务（build/clean/browse）
│   └── gates.py        # CI 质量门任务（utf8/toctrees）
├── scripts/            # CI 检查脚本（被 tasks/gates.py 调用）
│   ├── check-toctrees.py   # toctree 完整性检查
│   ├── check-utf8.py       # UTF-8 编码检查
│   └── scan-history-utf8.py # Git 历史 UTF-8 扫描
├── .agents/            # AI 智能体规范（本目录）
│   ├── README.md       # 规范目录索引
│   ├── ONBOARDING.md   # 本文件 - 入门指南
│   ├── global-core-rules.md  # 全局核心规则
│   ├── context-routing.md    # 上下文路由表
│   └── rules/
│       └── frontmatter.md    # OKF v0.2 文档元数据规范
├── .github/workflows/  # CI/CD 工作流（GitHub Pages 自动部署）
├── AGENTS.md           # 智能体协作入口（启动协议）
├── pyproject.toml      # 项目元数据与依赖声明
└── README.md           # 项目说明
```

## 第一次任务？

如果你是第一次在本文档库中执行任务，请：

1. ✅ 已读取根目录 `AGENTS.md`（含启动协议）
2. ✅ 已完成内容敏感度预检（公开/私域判定）
3. 根据任务类型查阅 `context-routing.md`，按需读取对应规范
4. 涉及具体知识文档时，先确认其目标目录（`doc/bundles/` 或 `doc/`）
5. 新增/修改 bundle 后，运行 `invoke gates.toctrees` 验证导航完整性
6. 修改 `doc/conf.py` 等构建配置后，运行 `invoke build` 验证构建通过
7. 简单任务可直接执行，复杂任务先规划再动手

## 文档规范

- **语言**：正文中文，文件名 kebab-case 纯英文
- **格式**：Markdown + OKF v0.2 YAML frontmatter
- **路径引用**：相对路径，禁止 `file:///` 绝对路径
- **Bundle 规则**：含子目录的 bundle 根必须有 `index.md` 并配置 `{toctree}`

详细规范见 [global-core-rules.md](global-core-rules.md) 和 [rules/frontmatter.md](rules/frontmatter.md)。

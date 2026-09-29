---
title: 基本用法
type: example
bundle: tutorial-codebase-knowledge
related:
  - tutorial-codebase-knowledge/concepts/pipeline-architecture
  - tutorial-codebase-knowledge/concepts/code-analysis-workflow
  - tutorial-codebase-knowledge/references/utility-functions
---

# 基本用法

本示例展示如何使用 Codebase Knowledge Generator 从 GitHub 仓库或本地目录生成代码教程。

## 环境准备

### 1. 安装依赖

```bash
git clone https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge
cd PocketFlow-Tutorial-Codebase-Knowledge
pip install -r requirements.txt
```

### 2. 配置 LLM

项目默认使用 Google Gemini（推荐 gemini-2.5-pro），在 `.env` 文件中设置：

```bash
# 方式一：使用 Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# 方式二：使用 Vertex AI
GEMINI_PROJECT_ID=your_gcp_project_id
GEMINI_LOCATION=us-central1

# 方式三：使用 OpenAI 兼容 API（如 Ollama、xAI 等）
LLM_PROVIDER=OLLAMA
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_BASE_URL=http://localhost:11434/
```

验证 LLM 配置是否正确：

```bash
python utils/call_llm.py
```

### 3. （可选）配置 GitHub Token

为避免公共仓库的 API 速率限制，设置 GitHub Token：

```bash
GITHUB_TOKEN=your_github_token_here
```

## 命令行使用

### 分析 GitHub 仓库

最简用法（使用默认文件模式和英语输出）：

```bash
python main.py --repo https://github.com/pallets/flask
```

指定文件包含/排除模式：

```bash
python main.py \
  --repo https://github.com/pallets/flask \
  --include "*.py" \
  --exclude "tests/*" "docs/*"
```

限制文件大小、指定输出目录和项目名：

```bash
python main.py \
  --repo https://github.com/pallets/flask \
  -n Flask \
  -o ./tutorials \
  -s 50000 \
  --max-abstractions 8
```

### 分析本地目录

```bash
python main.py --dir ./my-project --include "*.py" "*.js" --exclude "*test*"
```

### 生成中文教程

```bash
python main.py --repo https://github.com/pallets/flask --language "Chinese"
```

支持的语言参数：任意语言名称（如 `"Chinese"`、`"Japanese"`、`"Spanish"` 等），LLM 会自动生成对应语言的教程内容。

### 禁用缓存（调试用）

```bash
python main.py --repo https://github.com/pallets/flask --no-cache
```

### 完整参数一览

```
用法: python main.py [--repo URL | --dir PATH] [选项]

数据源（二选一，必填）:
  --repo URL              GitHub 仓库 URL
  --dir PATH              本地目录路径

选项:
  -n, --name NAME         项目名称（默认从URL/目录推导）
  -t, --token TOKEN       GitHub 个人访问令牌
  -o, --output DIR        输出目录（默认: ./output）
  -i, --include PATTERNS  包含文件模式，空格分隔（如: *.py *.js）
  -e, --exclude PATTERNS  排除文件模式，空格分隔（如: tests/* docs/*）
  -s, --max-size BYTES    最大文件大小（字节，默认: 100000 ≈ 100KB）
  --language LANG         教程语言（默认: english）
  --no-cache              禁用 LLM 响应缓存
  --max-abstractions N    最大抽象数量（默认: 10）
```

## Python API 使用

除了命令行，也可以在 Python 代码中直接调用：

```python
from flow import create_tutorial_flow

# 初始化 shared 字典
shared = {
    "repo_url": "https://github.com/pallets/flask",
    "local_dir": None,
    "project_name": "Flask",
    "github_token": None,
    "output_dir": "./output",
    "include_patterns": {"*.py"},
    "exclude_patterns": {"tests/*", "docs/*"},
    "max_file_size": 50000,
    "language": "Chinese",
    "use_cache": True,
    "max_abstraction_num": 8,
    # 输出占位（节点会填充这些字段）
    "files": [],
    "abstractions": [],
    "relationships": {},
    "chapter_order": [],
    "chapters": [],
    "final_output_dir": None,
}

# 创建并运行流程
flow = create_tutorial_flow()
flow.run(shared)

print(f"教程已生成至: {shared['final_output_dir']}")
```

## 输出结构

运行成功后，输出目录结构如下：

```
output/{project_name}/
├── index.md                     # 教程首页（含摘要、Mermaid关系图、章节目录）
├── 01_{chapter1_name}.md        # 第一章
├── 02_{chapter2_name}.md        # 第二章
├── 03_{chapter3_name}.md        # 第三章
└── ...
```

首页 `index.md` 包含：
1. 项目标题和摘要（由 LLM 生成的新手友好概述）
2. 源仓库链接
3. Mermaid 关系图（展示核心抽象之间的依赖关系）
4. 带链接的章节目录

每个章节文件包含：
1. 章节标题和前章过渡
2. 动机和用例讲解
3. 代码示例（每段≤10行，附讲解）
4. Mermaid 序列图说明内部流程
5. 源码级实现讲解
6. 章节总结和下章过渡链接

## 自定义节点扩展

可以通过继承或替换节点来自定义行为。例如，自定义抽象识别逻辑：

```python
from pocketflow import Node, Flow
from nodes import (
    FetchRepo, AnalyzeRelationships, OrderChapters,
    WriteChapters, CombineTutorial
)

class CustomIdentifyAbstractions(Node):
    """自定义抽象识别：使用自己的分析策略"""
    def prep(self, shared):
        # 自定义准备逻辑
        return shared["files"]

    def exec(self, files_data):
        # 自定义抽象识别逻辑
        abstractions = [
            {"name": "MyCore", "description": "...", "files": [0, 1]},
            # ...
        ]
        return abstractions

    def post(self, shared, prep_res, exec_res):
        shared["abstractions"] = exec_res

# 使用自定义节点构建流程
fetch = FetchRepo()
identify = CustomIdentifyAbstractions(max_retries=3, wait=10)
analyze = AnalyzeRelationships(max_retries=5, wait=20)
order = OrderChapters(max_retries=5, wait=20)
write = WriteChapters(max_retries=5, wait=20)
combine = CombineTutorial()

fetch >> identify >> analyze >> order >> write >> combine
flow = Flow(start=fetch)
```

## Docker 运行

```bash
# 构建镜像
docker build -t pocketflow-app .

# 分析公共 GitHub 仓库
docker run -it --rm \
  -e GEMINI_API_KEY="your_key_here" \
  -v "$(pwd)/output_tutorials":/app/output \
  pocketflow-app --repo https://github.com/pallets/flask

# 分析本地目录
docker run -it --rm \
  -e GEMINI_API_KEY="your_key_here" \
  -v "/path/to/your/code":/app/code_to_analyze \
  -v "$(pwd)/output_tutorials":/app/output \
  pocketflow-app --dir /app/code_to_analyze
```

## 常见问题

**Q: LLM 输出解析失败怎么办？**
A: 节点配置了 `max_retries=5`，会自动重试。如果持续失败，可以尝试：
- 使用更强的模型（推荐 Gemini 2.5 Pro 或 Claude 3.7+）
- 减小 `--max-abstractions` 降低复杂度
- 使用 `--no-cache` 强制获取新响应

**Q: 生成速度慢怎么办？**
A: 主要耗时在 LLM 调用（共4+N次，N为章节数）。可以：
- 减少 `--max-abstractions`（默认10，减少到5-6会快很多）
- 确保 LLM 缓存启用（默认启用，不要加 `--no-cache`）
- 使用更快的模型（质量可能略有下降）

**Q: 如何生成特定子目录的教程？**
A: 在 GitHub URL 中指定路径：`--repo https://github.com/owner/repo/tree/main/src/subdir`

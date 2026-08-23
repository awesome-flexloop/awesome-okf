---
title: 工具函数
type: reference
bundle: tutorial-codebase-knowledge
source: utils/
---

# 工具函数

本页文档化项目中的所有工具函数，包括 LLM 调用、文件爬取、辅助函数和流程创建函数。

## 目录

- [call_llm](#call_llm) — LLM 统一调用接口（含缓存、多提供商支持）
- [crawl_github_files](#crawl_github_files) — GitHub 仓库文件爬取
- [crawl_local_files](#crawl_local_files) — 本地目录文件遍历
- [get_content_for_indices](#get_content_for_indices) — 按索引提取文件内容
- [create_tutorial_flow](#create_tutorial_flow) — 创建教程生成流程
- [main](#main) — 命令行入口函数

---

## call_llm

```python
def call_llm(prompt: str, use_cache: bool = True) -> str:
```

源码位置：[utils/call_llm.py#L128-L158](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py#L128-L158)

统一的 LLM 调用接口，支持多提供商（Google Gemini / OpenAI 兼容 API）和本地 JSON 缓存。

### 参数

- `prompt` (str)：发送给 LLM 的提示词
- `use_cache` (bool)：是否启用缓存，默认 `True`

### 返回值

- (str)：LLM 的文本响应

### 工作流程

1. 记录 prompt 到日志
2. 若启用缓存，从 `llm_cache.json` 加载缓存，若 prompt 命中缓存直接返回缓存结果
3. 通过 [get_llm_provider()](#get_llm_provider) 检测提供商类型
4. Gemini 提供商调用 [_call_llm_gemini()](#_call_llm_gemini)，其他调用 [_call_llm_provider()](#_call_llm_provider)
5. 记录响应到日志
6. 若启用缓存，将结果写入缓存文件

### 缓存机制

- 缓存文件：`llm_cache.json`（当前工作目录）
- 缓存键：完整的 prompt 字符串（精确匹配）
- 重试时缓存不生效：节点中通过 `use_cache and self.cur_retry == 0` 判断，首次尝试使用缓存，重试时跳过缓存

### 内部函数

#### get_llm_provider()

```python
def get_llm_provider():
```

源码位置：[utils/call_llm.py#L46-L51](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py#L46-L51)

检测 LLM 提供商：优先读取 `LLM_PROVIDER` 环境变量；若未设置但存在 `GEMINI_PROJECT_ID` 或 `GEMINI_API_KEY`，默认返回 `"GEMINI"`。

#### _call_llm_gemini(prompt)

```python
def _call_llm_gemini(prompt: str) -> str:
```

源码位置：[utils/call_llm.py#L161-L177](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py#L161-L177)

调用 Google Gemini API。支持两种认证方式：
- Vertex AI：设置 `GEMINI_PROJECT_ID`（可选 `GEMINI_LOCATION`，默认 `us-central1`）
- API Key：设置 `GEMINI_API_KEY`

默认模型：`gemini-2.5-pro-exp-03-25`，可通过 `GEMINI_MODEL` 环境变量覆盖。

#### _call_llm_provider(prompt)

```python
def _call_llm_provider(prompt: str) -> str:
```

源码位置：[utils/call_llm.py#L54-L125](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py#L54-L125)

调用 OpenAI 兼容 API（支持 Ollama、xAI 等）。通过环境变量配置：
- `LLM_PROVIDER`：提供商名称（如 `"OLLAMA"`、`"XAI"`）
- `{PROVIDER}_MODEL`：模型名称（如 `OLLAMA_MODEL`）
- `{PROVIDER}_BASE_URL`：API 基础 URL（如 `OLLAMA_BASE_URL=http://localhost:11434/`）
- `{PROVIDER}_API_KEY`：API 密钥（可选）

请求地址：`{base_url}/v1/chat/completions`

#### load_cache() / save_cache(cache)

源码位置：[utils/call_llm.py#L29-L43](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py#L29-L43)

从/向 `llm_cache.json` 读取/写入缓存 JSON 文件。加载失败时返回空字典，保存失败时记录警告。

---

## crawl_github_files

```python
def crawl_github_files(
    repo_url,
    token=None,
    max_file_size: int = 1 * 1024 * 1024,
    use_relative_paths: bool = False,
    include_patterns: Union[str, Set[str]] = None,
    exclude_patterns: Union[str, Set[str]] = None,
):
```

源码位置：[utils/crawl_github_files.py#L11-L343](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_github_files.py#L11-L343)

从 GitHub 仓库抓取文件内容，支持 HTTPS URL 和 SSH URL 两种方式。

### 参数

- `repo_url` (str)：GitHub 仓库 URL，支持：
  - HTTPS：`https://github.com/owner/repo` 或 `https://github.com/owner/repo/tree/branch/path`
  - SSH：`git@github.com:owner/repo.git`
- `token` (str|None)：GitHub 个人访问令牌
- `max_file_size` (int)：最大文件大小（字节），默认 1MB
- `use_relative_paths` (bool)：是否使用相对于子目录的路径
- `include_patterns` (str|set|None)：包含模式（fnmatch 格式）
- `exclude_patterns` (str|set|None)：排除模式（fnmatch 格式）

### 返回值

```python
{
    "files": {filepath: content, ...},
    "stats": {
        "downloaded_count": int,
        "skipped_count": int,
        "skipped_files": [(path, size), ...],
        "base_path": str | None,
        "include_patterns": set | None,
        "exclude_patterns": set | None,
        "source": "ssh_clone"  # SSH模式特有
    }
}
```

### 工作模式

**SSH URL 模式**（`git@` 开头或 `.git` 结尾）：
1. 使用 `git.Repo.clone_from()` 克隆到临时目录
2. 使用 `os.walk()` 遍历文件
3. 按大小和模式过滤后读取文件内容
4. 临时目录在 with 块结束时自动清理

**HTTPS URL 模式**：
1. 解析 URL 提取 owner/repo/ref/path
2. 递归调用 GitHub Contents API 获取目录树
3. 通过 `download_url` 或 base64 解码获取文件内容
4. 自动处理速率限制（403 + rate limit → 等待 X-RateLimit-Reset）
5. 目录排除检查在递归前进行（剪枝优化）

### 内部函数

- `should_include_file(file_path, file_name)`：根据 include/exclude 模式判断文件是否包含
- `fetch_branches(owner, repo)`：获取仓库分支列表
- `check_tree(owner, repo, tree)`：检查指定 tree SHA 是否存在
- `fetch_contents(path)`：递归获取指定路径下的文件和目录内容

---

## crawl_local_files

```python
def crawl_local_files(
    directory,
    include_patterns=None,
    exclude_patterns=None,
    max_file_size=None,
    use_relative_paths=True,
):
```

源码位置：[utils/crawl_local_files.py#L6-L129](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_local_files.py#L6-L129)

遍历本地目录抓取文件内容，自动尊重 `.gitignore` 规则。

### 参数

- `directory` (str)：本地目录路径
- `include_patterns` (set|None)：包含模式（fnmatch 格式）
- `exclude_patterns` (set|None)：排除模式（fnmatch 格式）
- `max_file_size` (int|None)：最大文件大小（字节）
- `use_relative_paths` (bool)：是否使用相对路径，默认 `True`

### 返回值

```python
{"files": {filepath: content, ...}}
```

### 工作流程

1. 验证目录存在
2. 读取 `.gitignore`（若存在），使用 `pathspec.PathSpec` 编译 gitwildmatch 规则
3. **第一遍遍历**：`os.walk()` 收集所有文件路径，同时：
   - 在目录级别排除被 gitignore 或 exclude_patterns 匹配的目录（剪枝）
4. **第二遍处理**：逐个文件检查：
   - 是否被 gitignore 排除
   - 是否被 exclude_patterns 排除
   - 是否匹配 include_patterns
   - 是否超过大小限制
   - 读取文件内容（UTF-8 with BOM 处理）
5. 打印带颜色的进度信息（绿色 ANSI 转义码）

---

## get_content_for_indices

```python
def get_content_for_indices(files_data, indices):
```

源码位置：[nodes.py#L11-L19](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py#L11-L19)

模块级辅助函数（定义在 nodes.py 中，不属于任何类），根据文件索引列表从 files_data 中提取对应文件内容。

### 参数

- `files_data`：`[(path, content), ...]` 文件元组列表
- `indices`：`[int, ...]` 文件索引列表

### 返回值

- (dict)：`{f"{i} # {path}": content}` 映射字典

### 注意事项

- 索引越界时自动跳过（不抛出异常）
- 键格式为 `"{index} # {path}"`，在 WriteChapters 的 exec 中会解析 `# ` 后的路径用于显示

---

## create_tutorial_flow

```python
def create_tutorial_flow():
```

源码位置：[flow.py#L12-L33](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/flow.py#L12-L33)

创建并返回完整的代码库教程生成流程（Flow 对象）。

### 返回值

- `Flow`：以 FetchRepo 为起始节点的 PocketFlow Flow 对象

### 节点配置

| 节点 | 类 | 重试配置 |
|------|-----|---------|
| fetch_repo | FetchRepo | 默认（无重试） |
| identify_abstractions | IdentifyAbstractions | max_retries=5, wait=20 |
| analyze_relationships | AnalyzeRelationships | max_retries=5, wait=20 |
| order_chapters | OrderChapters | max_retries=5, wait=20 |
| write_chapters | WriteChapters (BatchNode) | max_retries=5, wait=20 |
| combine_tutorial | CombineTutorial | 默认（无重试） |

### 流程连接

```python
fetch_repo >> identify_abstractions >> analyze_relationships >> order_chapters >> write_chapters >> combine_tutorial
```

所有节点使用默认边（`>>`）线性连接，无分支、无循环。

---

## main

```python
def main():
```

源码位置：[main.py#L39-L108](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/main.py#L39-L108)

命令行入口函数，解析命令行参数、初始化 shared 字典、创建并运行流程。

### 命令行参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--repo` | — | str | — | GitHub 仓库 URL（与 --dir 互斥） |
| `--dir` | — | str | — | 本地目录路径（与 --repo 互斥） |
| `--name` | `-n` | str | None | 项目名称（自动推导） |
| `--token` | `-t` | str | None | GitHub Token（或读 GITHUB_TOKEN 环境变量） |
| `--output` | `-o` | str | `"output"` | 输出基础目录 |
| `--include` | `-i` | str+ | DEFAULT_INCLUDE_PATTERNS | 包含文件模式 |
| `--exclude` | `-e` | str+ | DEFAULT_EXCLUDE_PATTERNS | 排除文件模式 |
| `--max-size` | `-s` | int | 100000 | 最大文件大小（字节，约100KB） |
| `--language` | — | str | `"english"` | 教程输出语言 |
| `--no-cache` | — | flag | False | 禁用 LLM 缓存 |
| `--max-abstractions` | — | int | 10 | 最大抽象数量 |

### 默认文件模式

**DEFAULT_INCLUDE_PATTERNS**（[main.py#L10-L14](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/main.py#L10-L14)）：
```
*.py, *.js, *.jsx, *.ts, *.tsx, *.go, *.java, *.pyi, *.pyx,
*.c, *.cc, *.cpp, *.h, *.md, *.rst, *Dockerfile,
*Makefile, *.yaml, *.yml
```

**DEFAULT_EXCLUDE_PATTERNS**（[main.py#L16-L36](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/main.py#L16-L36)）：
```
assets/*, data/*, images/*, public/*, static/*, temp/*,
*docs/*, *venv/*, *.venv/*, *test*, *tests/*, *examples/*,
v1/*, *dist/*, *build/*, *experimental/*, *deprecated/*,
*misc/*, *legacy/*, .git/*, .github/*, .next/*, .vscode/*,
*obj/*, *bin/*, *node_modules/*, *.log
```

### Shared 字典初始化

main() 函数初始化的 shared 字典包含以下键：
- 输入参数：`repo_url`, `local_dir`, `project_name`, `github_token`, `output_dir`, `include_patterns`, `exclude_patterns`, `max_file_size`, `language`, `use_cache`, `max_abstraction_num`
- 输出占位：`files`（空列表）, `abstractions`（空列表）, `relationships`（空字典）, `chapter_order`（空列表）, `chapters`（空列表）, `final_output_dir`（None）

### 源码位置

- [main.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/main.py)
- [flow.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/flow.py)
- [utils/call_llm.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py)
- [utils/crawl_github_files.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_github_files.py)
- [utils/crawl_local_files.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_local_files.py)

---
type: Example
title: 自动重定向写入
description: 使用rediraffewritediff构建器自动将Git重命名文件追加到重定向配置文件，设置相似度阈值
tags: [sphinxext-rediraffe, auto-redirect, writediff, git-rename, similarity-threshold]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 自动重定向写入

本示例演示如何使用 `rediraffewritediff` 构建器自动检测Git重命名文件并追加到重定向配置文件，减少手动维护重定向的负担。

## 工作原理

`rediraffewritediff` 在 `rediraffecheckdiff` 的检查基础上，额外执行自动写入：

1. 通过Git diff检测重命名文件（R状态）和相似度
2. 如果相似度 ≥ `rediraffe_auto_redirect_perc` 阈值，自动将重定向对追加到 `redirects.txt`
3. 自动使用双引号包裹路径（确保含空格路径也能正确解析）
4. 删除文件（D状态）无法自动推断目标，需要手动添加

## 前置条件

- 项目使用Git
- `rediraffe_redirects` 必须配置为**文件路径字符串**（dict方式不支持自动写入）
- `rediraffe_branch` 设置为对比基准

## 基本使用

### 配置conf.py

```python
# conf.py
extensions = ['sphinxext.rediraffe']

rediraffe_redirects = 'redirects.txt'  # 必须是文件路径，不能是dict
rediraffe_branch = 'HEAD~1'            # 对比上一个提交
rediraffe_auto_redirect_perc = 90       # 相似度>=90%自动添加
```

### 重命名文件

```bash
# 重命名一个文档文件（Git会检测为重命名）
git mv docs/old-tutorial.rst docs/tutorials/getting-started.rst

# 提交变更
git add docs/old-tutorial.rst docs/tutorials/getting-started.rst
git commit -m "Rename tutorial page"
```

### 运行自动写入

```bash
sphinx-build -b rediraffewritediff . _build/write
```

构建输出：
```
(okay) "docs/old-tutorial.rst" has been redirected to "docs/tutorials/getting-started.rst" in your redirects file!
```

检查 `redirects.txt`，新条目已被自动追加：

```text
# 原有重定向...
"docs/old-tutorial.rst" "docs/tutorials/getting-started.rst"
```

## 相似度阈值详解

Git的重命名检测基于文件内容相似度（0-100%）。阈值设置决定了"多像才算重命名"。

### Git如何检测重命名

Git使用相似性指数（similarity index）判断文件是否被重命名：
- `R100`：100%相似（纯重命名，内容未变）
- `R95`：95%相似（重命名后有少量修改）
- `R50`：50%相似（重命名后有大量修改）

### 阈值选择建议

```python
# 保守设置（默认）：只自动添加完全重命名
rediraffe_auto_redirect_perc = 100

# 推荐设置：允许小幅修改后的重命名
rediraffe_auto_redirect_perc = 90

# 积极设置：在大规模重构时使用
rediraffe_auto_redirect_perc = 70
```

| 阈值 | 适用场景 | 优点 | 风险 |
|------|---------|------|------|
| 100% | 安全优先 | 无误判 | 文件重命名后即使只改一个字也不会自动添加 |
| 90% | 日常开发（推荐） | 处理重命名后的小修改 | 极少误判 |
| 70-89% | 大规模重构 | 自动处理大部分重命名 | 可能将新文件误判为重命名 |
| <70% | 不推荐 | — | 误判风险高 |

### 测试中的阈值验证

测试用例验证了阈值行为：

**test-renamed_write_file_perc_low_pass（阈值50%）**：
```python
# conf.py 设置 rediraffe_auto_redirect_perc = 50
# 重命名相似度50%以上 → 自动追加
```

**test-renamed_write_file_perc_low_fail（阈值50%）**：
```python
# conf.py 使用默认 rediraffe_auto_redirect_perc = 100
# 重命名相似度50% → 不追加（低于100%阈值）
```

## 典型工作流

### 本地开发工作流

```bash
# 1. 创建新分支进行文档重构
git checkout -b docs/restructure

# 2. 移动/重命名文件
mkdir -p docs/tutorials
git mv docs/intro.rst docs/tutorials/introduction.rst
git mv docs/install.rst docs/tutorials/installation.rst

# 3. 编辑文件（做一些内容修改）
# ...编辑文档...

# 4. 提交变更
git add docs/
git commit -m "Restructure tutorials section"

# 5. 运行自动重定向写入
sphinx-build -b rediraffewritediff \
  -D rediraffe_branch=HEAD~1 \
  -D rediraffe_auto_redirect_perc=90 \
  docs docs/_build/write

# 6. 审查自动添加的条目
cat docs/redirects.txt

# 7. 手动补充删除文件的重定向（自动写入不处理删除）
# 编辑 redirects.txt 添加删除文件的重定向

# 8. 运行检查确认无误
sphinx-build -b rediraffecheckdiff \
  -D rediraffe_branch=HEAD~1 \
  docs docs/_build/check

# 9. 正常构建验证
sphinx-build -b html docs docs/_build/html

# 10. 提交重定向配置
git add docs/redirects.txt
git commit -m "Add redirects for restructured tutorials"
```

### PR审查工作流

在团队协作中，可以结合 checkdiff 和 writediff：

```yaml
# GitHub Actions
- name: Check redirects (strict)
  run: sphinx-build -b rediraffecheckdiff -D rediraffe_branch=origin/main docs docs/_build/check

# 开发者本地可以用writediff快速修复，CI用checkdiff严格把关
```

## 自动追加格式

自动写入的条目使用双引号包裹的POSIX路径格式：

```text
"old/path/file.rst" "new/path/file.rst"
```

这种格式的好处：
- **跨平台兼容**：使用正斜杠（通过`PurePosixPath`转换）
- **含空格安全**：双引号包裹，路径含空格不会解析错误
- **与手写格式兼容**：双引号格式和手动添加的无引号/单引号格式都能被正确解析

代码中的实现：

```python
rel_rename_from = f'"{str(PurePosixPath(renamed_file.relative_to(src_path)))}"'
rel_rename_to = f'"{str(PurePosixPath(hint_to.relative_to(src_path)))}"'
with redirects_path.open('a', encoding='utf-8') as redirects_file:
    redirects_file.write(f'{rel_rename_from} {rel_rename_to}\n')
```

## 注意事项

### 1. 仅支持文件方式配置

```python
# ✅ 正确：文件方式
rediraffe_redirects = 'redirects.txt'

# ❌ 错误：dict方式
rediraffe_redirects = {'old.rst': 'new.rst'}
```

使用dict方式时，writediff会报错：
```
(broken) Automatic redirects is only available with a redirects file.
```

### 2. 删除文件不自动处理

自动写入只处理重命名（R状态），不处理删除（D状态）。删除文件的重定向必须手动添加：

```text
# 手动添加删除文件的重定向
deleted-page.rst replacement-page.rst
```

### 3. 追加模式不删除旧条目

writediff使用追加模式（`'a'`）打开文件，不会删除或修改已有的重定向条目。如果重定向关系变了（如文件第二次移动），需要手动更新。

### 4. 追加前检查

writediff会先检查文件是否已在重定向配置中：

```python
if renamed_file in absolute_redirects:
    logger.info('renamed file %s redirects to %s.', renamed_file, absolute_redirects[renamed_file])
    continue  # 已有重定向，跳过
```

已配置的重定向不会重复追加。

### 5. 非源文件自动过滤

不在源目录内的文件、非文档后缀的文件会被自动过滤，不会被追加到重定向文件：

```python
def abs_path_in_src_dir_w_src_suffix(filename):
    abs_path = (repo_root / filename.strip()).resolve()
    if not str(abs_path).startswith(str(src_path)):
        return None  # 不在源目录
    if abs_path.suffix not in source_suffixes:
        return None  # 不是文档文件
    return abs_path
```

## 相关概念

- [Builder体系详解](/concepts/05-builders.md)
- [配置项详解](/concepts/04-configuration.md)
- [CI Diff检查集成](/examples/diff-checker-ci.md)
- [基础重定向配置](/examples/basic-redirects.md)

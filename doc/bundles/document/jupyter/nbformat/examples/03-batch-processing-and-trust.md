---
type: "example"
title: "Notebook批处理与信任管理"
description: "批量遍历和修改Notebook、NotebookNotary签名信任、cell元数据操作、标签管理"
tags: [batch, processing, trust, sign, notary, tags, metadata, traverse]
sources:
  - id: sign
    resource: /references/sign-source.md
    title: "签名与信任机制"
  - id: notebooknode
    resource: /references/notebooknode-source.md
    title: "NotebookNode源码"
---

# Notebook批处理与信任管理

## 示例目标

演示批量遍历Notebook目录、修改cell、添加标签、签名信任等高级操作。

## 完整代码

```python
"""
批量处理Notebook和信任签名管理示例。
"""
import os
import glob
import nbformat as nbf
from nbformat.corpus.words import generate_corpus_id
from nbformat.sign import NotebookNotary
from copy import deepcopy


# ── 1. 批量遍历目录中的Notebook ──────────────────────────

def list_notebooks(directory="."):
    """列出目录中所有.ipynb文件"""
    return glob.glob(os.path.join(directory, "**", "*.ipynb"), recursive=True)


def notebook_summary(nb, path=""):
    """打印Notebook摘要信息"""
    major, minor = nbf.reader.get_version(nb)
    code_cells = sum(1 for c in nb.cells if c.cell_type == "code")
    md_cells = sum(1 for c in nb.cells if c.cell_type == "markdown")
    executed = sum(1 for c in nb.cells
                   if c.cell_type == "code" and c.execution_count is not None)
    total_outputs = sum(len(c.outputs) for c in nb.cells if c.cell_type == "code")

    print(f"\n📓 {os.path.basename(path)} (v{major}.{minor})")
    print(f"   Cells: {len(nb.cells)} total ({code_cells} code, {md_cells} markdown)")
    print(f"   Executed: {executed}/{code_cells} code cells, {total_outputs} outputs")

    # kernelspec
    ks = nb.metadata.get("kernelspec", {})
    if ks:
        print(f"   Kernel: {ks.get('display_name', ks.get('name', 'unknown'))}")


# 扫描当前目录
notebooks = list_notebooks(".")
print(f"发现 {len(notebooks)} 个Notebook文件")
for path in notebooks:
    nb = nbf.read(path, as_version=nbf.NO_CONVERT)
    notebook_summary(nb, path)


# ── 2. 添加/移除Tags ─────────────────────────────────────

def add_tag(cell, tag):
    """安全地给cell添加tag"""
    if "tags" not in cell.metadata:
        cell.metadata["tags"] = []
    if tag not in cell.metadata.tags:
        cell.metadata.tags.append(tag)


def remove_tag(cell, tag):
    """安全地从cell移除tag"""
    if "tags" in cell.metadata and tag in cell.metadata.tags:
        cell.metadata.tags.remove(tag)
        if not cell.metadata.tags:
            del cell.metadata["tags"]


def tag_code_cells(nb, tag="auto-tagged"):
    """给所有code cell添加标签"""
    for cell in nb.cells:
        if cell.cell_type == "code":
            add_tag(cell, tag)


# 读取并标记
nb = nbf.read("example_notebook.ipynb", as_version=4)
tag_code_cells(nb, "example-tag")
for cell in nb.cells:
    if cell.cell_type == "code":
        print(f"Cell {cell.id[:8]} tags: {cell.metadata.get('tags', [])}")


# ── 3. 提取所有代码单元 ──────────────────────────────────

def extract_code(nb):
    """提取Notebook中所有code cell的源代码"""
    return [c.source for c in nb.cells if c.cell_type == "code"]


def extract_markdown_titles(nb):
    """提取所有Markdown标题"""
    titles = []
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for line in cell.source.split("\n"):
                if line.startswith("#"):
                    titles.append(line.strip())
    return titles


nb = nbf.read("example_notebook.ipynb", as_version=4)
codes = extract_code(nb)
print(f"\n代码单元数: {len(codes)}")
for i, code in enumerate(codes):
    first_line = code.split("\n")[0]
    print(f"  [{i}] {first_line[:60]}...")

titles = extract_markdown_titles(nb)
print(f"Markdown标题: {titles}")


# ── 4. 清除所有输出（重置执行状态） ──────────────────────

def clear_outputs(nb):
    """清除所有code cell的输出和执行计数（深拷贝，不修改原对象）"""
    nb_copy = deepcopy(nb)
    for cell in nb_copy.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    return nb_copy


# 创建一个清除输出的版本
nb_cleared = clear_outputs(nb)
executed_before = sum(1 for c in nb.cells
                      if c.cell_type == "code" and c.execution_count is not None)
executed_after = sum(1 for c in nb_cleared.cells
                     if c.cell_type == "code" and c.execution_count is not None)
print(f"\n清除输出前: {executed_before}个已执行cell")
print(f"清除输出后: {executed_after}个已执行cell")


# ── 5. 信任签名管理 ──────────────────────────────────────

def check_trust(notebook_path):
    """检查Notebook是否可信"""
    with NotebookNotary() as notary:
        nb = nbf.read(notebook_path, as_version=nbf.NO_CONVERT)
        trusted = notary.check_signature(nb)
        return trusted


def sign_notebook(notebook_path):
    """签名Notebook（标记为可信）"""
    with NotebookNotary() as notary:
        nb = nbf.read(notebook_path, as_version=nbf.NO_CONVERT)
        notary.sign(nb)
        nbf.write(nb, notebook_path)
        print(f"✅ 已签名: {notebook_path}")


def unsign_notebook(notebook_path):
    """取消Notebook信任"""
    with NotebookNotary() as notary:
        nb = nbf.read(notebook_path, as_version=nbf.NO_CONVERT)
        notary.unsign(nb)
        nbf.write(nb, notebook_path)
        print(f"🔓 已取消签名: {notebook_path}")


# 检查当前信任状态
path = "example_notebook.ipynb"
if os.path.exists(path):
    trusted_before = check_trust(path)
    print(f"\n签名前可信状态: {trusted_before}")

    # 签名
    sign_notebook(path)
    trusted_after = check_trust(path)
    print(f"签名后可信状态: {trusted_after}")

    # 验证签名存储在metadata中
    nb_signed = nbf.read(path, as_version=4)
    sig = nb_signed.metadata.get("signature")
    # 注意：写入时strip_transient会移除signature，所以sig可能为None
    # 签名实际存储在SQLite数据库中，通过check_signature验证

    # 取消签名
    unsign_notebook(path)
    trusted_unsigned = check_trust(path)
    print(f"取消签名后可信状态: {trusted_unsigned}")


# ── 6. 合并两个Notebook ──────────────────────────────────

def merge_notebooks(nb1, nb2):
    """将nb2的cells追加到nb1（深拷贝cells）"""
    merged = deepcopy(nb1)
    for cell in nb2.cells:
        cell_copy = deepcopy(cell)
        # 确保ID唯一
        existing_ids = {c.id for c in merged.cells if "id" in c}
        if cell_copy.get("id") in existing_ids:
            cell_copy.id = generate_corpus_id()
        merged.cells.append(cell_copy)
    nbf.validate(merged)
    return merged


# 创建第二个Notebook
nb2 = nbf.v4.new_notebook()
nb2.cells.append(nbf.v4.new_markdown_cell("## 第二部分\n\n这是追加的内容。"))
nb2.cells.append(nbf.v4.new_code_cell("print('from nb2')"))

# 合并
merged = merge_notebooks(nb, nb2)
print(f"\n合并后cell数: {len(merged.cells)}")

# 写入合并结果
nbf.write(merged, "merged.ipynb")
print("已写入 merged.ipynb")


# ── 7. 过滤Notebook（只保留特定cell） ────────────────────

def filter_cells(nb, cell_type=None, has_tag=None):
    """按类型/标签过滤cell，返回新Notebook"""
    nb_filtered = deepcopy(nb)
    nb_filtered.cells = []
    for cell in nb.cells:
        if cell_type and cell.cell_type != cell_type:
            continue
        if has_tag and has_tag not in cell.metadata.get("tags", []):
            continue
        nb_filtered.cells.append(deepcopy(cell))
    return nb_filtered


# 只保留Markdown单元
md_only = filter_cells(nb, cell_type="markdown")
print(f"\n仅Markdown: {len(md_only.cells)} 个单元")
for c in md_only.cells:
    first_line = c.source.split("\n")[0][:60]
    print(f"  - {first_line}")
```

## 预期输出

```
发现 1 个Notebook文件

📓 example_notebook.ipynb (v4.5)
   Cells: 7 total (5 code, 2 markdown)
   Executed: 3/5 code cells, 4 outputs
   Kernel: Python 3
Cell ... tags: ['example-tag']
Cell ... tags: ['example-tag']
...

代码单元数: 5
  [0] import math...
  [1] print(f'π ≈ {math.pi:.4f}')...
  [2] data = {'name': 'Jupyter', 'version': 4}...
  [3] 1 / 0...
Markdown标题: ['# 示例Notebook', '*以上代码由nbformat自动生成。*']

清除输出前: 3个已执行cell
清除输出后: 0个已执行cell

签名前可信状态: False
✅ 已签名: example_notebook.ipynb
签名后可信状态: True
🔓 已取消签名: example_notebook.ipynb
取消签名后可信状态: False

合并后cell数: 9
已写入 merged.ipynb

仅Markdown: 2 个单元
  - # 示例Notebook...
  - ---...
```

## 关键要点

- 批量操作Notebook时使用 `deepcopy` 避免修改原始对象
- 操作metadata.tags时要先检查key是否存在，避免AttributeError
- `clear_outputs()` 是常见操作（提交Notebook前清除执行状态）
- NotebookNotary作为上下文管理器使用，自动关闭SQLite连接
- 签名存储在SQLite数据库中（用户级），写入文件时signature字段被strip_transient移除
- 合并Notebook时要处理cell ID冲突
- 信任检查逻辑：check_signature验证HMAC签名，签名由jupyter trust CLI或NotebookNotary.sign()创建

## 相关概念

- [信任与签名](../concepts/08-trust-and-signing.md)
- [NotebookNode与Struct](../concepts/03-notebook-node.md)
- [v4格式详解](../concepts/09-v4-format.md)

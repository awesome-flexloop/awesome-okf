---
type: example
title: nbconvert 自动化转换与报告生成
description: 使用 nbconvert 将 Notebook 转换为 HTML/PDF/Markdown/Python脚本、执行参数化 Notebook、批量转换、集成到自动化流水线
tags: [example, nbconvert, automation, report, papermill, batch, pdf, html]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# nbconvert 自动化转换与报告生成

本示例演示如何使用 nbconvert 将 Jupyter Notebook 转换为各种格式，并将其集成到自动化报告和数据管道中。

## 前置条件

- 已安装 Jupyter：`pip install jupyter` 或 `pip install nbconvert`
- PDF 导出需要 LaTeX（TeX Live/MiKTeX）或 Chromium（webpdf）
- 已阅读 [Notebook 作为文档与转换](../concepts/10-notebook-doc-convert.md)

## 步骤 1：基础格式转换

### 转换为 HTML

```bash
# 基本转换
jupyter nbconvert --to html my_notebook.ipynb

# 输出指定文件名
jupyter nbconvert --to html --output report.html my_notebook.ipynb

# 输出到指定目录
jupyter nbconvert --to html --output-dir ./reports my_notebook.ipynb
```

生成的 HTML 文件包含所有输出（文本、图表、图片），可以直接在浏览器打开。

### 转换为 Markdown

```bash
jupyter nbconvert --to markdown my_notebook.ipynb
```

图片会被提取到 `my_notebook_files/` 子目录，Markdown 文件中引用这些图片。

### 转换为 Python 脚本

```bash
jupyter nbconvert --to script my_notebook.ipynb
```

生成 `my_notebook.py`：
- Code 单元格的代码原样保留
- Markdown 单元格变为 `#` 注释
- 输出不包含（代码中 print 的输出会丢失，只有代码本身）

### 转换为 PDF

```bash
# 方法 1：通过 LaTeX（需要安装 TeX Live/MiKTeX）
jupyter nbconvert --to pdf my_notebook.ipynb

# 方法 2：通过 Chromium headless（需要 Chrome/Chromium）
jupyter nbconvert --to webpdf my_notebook.ipynb

# 方法 3：先转 HTML 再打印为 PDF（简单但不推荐用于正式文档）
jupyter nbconvert --to html my_notebook.ipynb
# 然后用浏览器打开 HTML，Ctrl+P 打印为 PDF
```

如果遇到 LaTeX 错误，通常是缺少 LaTeX 包。在 Linux 上安装完整包：

```bash
sudo apt install texlive-xetex texlive-fonts-recommended texlive-plain-generic texlive-latex-extra
```

### 转换为 LaTeX

```bash
jupyter nbconvert --to latex my_notebook.ipynb
```

生成 `.tex` 文件，可以手动编辑后用 `xelatex` 编译，适合需要精细控制 PDF 排版的场景。

## 步骤 2：执行后转换（包含最新输出）

默认情况下，nbconvert 使用 Notebook 中已保存的输出。如果需要在转换前重新执行所有代码：

```bash
# 执行 Notebook 后转换为 HTML
jupyter nbconvert --to html --execute my_notebook.ipynb

# 指定执行超时（秒），默认 30 秒
jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=120 my_notebook.ipynb

# 遇到错误时继续转换（默认遇到错误停止）
jupyter nbconvert --to html --execute --allow-errors my_notebook.ipynb

# 原地执行（更新 .ipynb 文件中的输出，不生成新格式文件）
jupyter nbconvert --to notebook --execute --inplace my_notebook.ipynb
```

`--execute` 会启动一个 Kernel 执行所有单元格，确保报告中的数据和图表是最新的。

## 步骤 3：控制输出内容

### 隐藏代码（生成纯输出报告）

```bash
# 隐藏代码单元格，只显示 Markdown 和输出
jupyter nbconvert --to html --no-input my_notebook.ipynb

# 隐藏 In [1]:/Out[1]: 提示
jupyter nbconvert --to html --no-prompt my_notebook.ipynb

# 组合使用
jupyter nbconvert --to html --no-input --no-prompt my_notebook.ipynb
```

### 使用单元格标签控制显示

在 Notebook 中给单元格添加标签，nbconvert 根据标签选择性隐藏：

1. 在 JupyterLab 中：选中单元格 → 右侧属性面板 → 点击标签图标 → 添加标签
2. 或在经典 Notebook 中：View → Cell Toolbar → Tags

常用标签：

| 标签 | 用途 |
|------|------|
| `hide-input` | 隐藏代码但显示输出 |
| `hide-output` | 隐藏输出但显示代码 |
| `remove-cell` | 完全移除该单元格 |
| `parameters` | 参数单元格（papermill 使用） |

```bash
# 隐藏标记为 hide-input 的代码
jupyter nbconvert --to html \
  --TagRemovePreprocessor.remove_input_tags='{"hide-input"}' \
  my_notebook.ipynb

# 移除标记为 remove-cell 的整个单元格
jupyter nbconvert --to html \
  --TagRemovePreprocessor.remove_cell_tags='{"remove-cell"}' \
  my_notebook.ipynb

# 隐藏标记为 hide-output 的输出
jupyter nbconvert --to html \
  --TagRemovePreprocessor.remove_output_tags='{"hide-output"}' \
  my_notebook.ipynb
```

## 步骤 4：使用 Python API 编程式转换

nbconvert 可以在 Python 脚本中调用，适合自动化管道。

### 基本转换

```python
import nbformat
from nbconvert import HTMLExporter
import os

# 读取 Notebook
notebook_path = 'analysis.ipynb'
nb = nbformat.read(notebook_path, as_version=4)

# 创建 HTML 导出器
html_exporter = HTMLExporter()
html_exporter.exclude_input_prompt = True  # 隐藏 In[1]:
html_exporter.exclude_output_prompt = True  # 隐藏 Out[1]:

# 转换
body, resources = html_exporter.from_notebook_node(nb)

# 保存 HTML
with open('report.html', 'w', encoding='utf-8') as f:
    f.write(body)

print("报告已生成: report.html")
```

### 执行 + 转换

```python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

# 读取
nb = nbformat.read('analysis.ipynb', as_version=4)

# 执行
ep = ExecutePreprocessor(timeout=120, kernel_name='python3')
ep.preprocess(nb, {'metadata': {'path': '.'}})  # path 是工作目录

# 保存执行后的 Notebook（包含最新输出）
nbformat.write(nb, 'analysis_executed.ipynb')

# 转换为 HTML
html_exporter = HTMLExporter()
body, resources = html_exporter.from_notebook_node(nb)
with open('report.html', 'w', encoding='utf-8') as f:
    f.write(body)
```

### 批量转换目录下所有 Notebook

```python
import nbformat
from nbconvert import HTMLExporter, PDFExporter
from pathlib import Path
import glob

def convert_notebooks(input_dir='notebooks', output_dir='reports', fmt='html'):
    """批量转换目录下所有 Notebook"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 选择导出器
    exporters = {
        'html': HTMLExporter,
        # 'pdf': PDFExporter,  # 需要 LaTeX
    }
    exporter = exporters[fmt]()
    exporter.exclude_input_prompt = True
    
    for nb_file in glob.glob(f'{input_dir}/*.ipynb'):
        name = Path(nb_file).stem
        print(f"转换中: {nb_file} -> {output_dir}/{name}.{fmt}")
        
        nb = nbformat.read(nb_file, as_version=4)
        body, resources = exporter.from_notebook_node(nb)
        
        output_file = output_path / f'{name}.{fmt}'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(body)
        
        # 保存关联资源（图片等）
        if resources.get('outputs'):
            for filename, data in resources['outputs'].items():
                filepath = output_path / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(data)

convert_notebooks()
```

## 步骤 5：使用 papermill 进行参数化执行

[papermill](https://papermill.readthedocs.io) 是 nbconvert 的扩展，支持参数化执行 Notebook——同一模板 Notebook，不同参数生成不同报告。

安装：

```bash
pip install papermill
```

### 准备模板 Notebook

1. 创建一个 Notebook，例如 `sales_report_template.ipynb`
2. 在一个单元格中定义参数默认值
3. 给该单元格添加 `parameters` 标签
4. 在后续单元格中使用这些参数进行分析和可视化

示例参数单元格（添加 `parameters` 标签）：

```python
# parameters
start_date = "2024-01-01"
end_date = "2024-12-31"
region = "East"
threshold = 1000
```

### 命令行参数化执行

```bash
# 基本用法
papermill sales_report_template.ipynb sales_report_east_2024.ipynb \
  -p start_date "2024-01-01" \
  -p end_date "2024-12-31" \
  -p region "East" \
  -p threshold 1000

# 生成多份报告（不同地区）
for region in East West North South; do
  papermill sales_report_template.ipynb "report_${region}.ipynb" \
    -p region "$region" \
    -p start_date "2024-01-01"
done
```

### Python API 参数化

```python
import papermill as pm

# 执行参数化 Notebook
pm.execute_notebook(
    'sales_report_template.ipynb',
    'output_report.ipynb',
    parameters={
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'region': 'East',
        'threshold': 1000
    },
    kernel_name='python3',
    progress_bar=True  # 显示进度
)
```

### 完整自动化管道示例

```python
#!/usr/bin/env python3
"""自动化日报生成脚本"""
import papermill as pm
import nbformat
from nbconvert import HTMLExporter
from datetime import date, timedelta
from pathlib import Path

def generate_daily_report(report_date: str, output_dir: str = 'daily_reports'):
    """为指定日期生成日报"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. 参数化执行 Notebook
    executed_nb = f'{output_dir}/executed_{report_date}.ipynb'
    pm.execute_notebook(
        'daily_report_template.ipynb',
        executed_nb,
        parameters={'report_date': report_date},
        kernel_name='python3'
    )
    
    # 2. 转换为 HTML
    nb = nbformat.read(executed_nb, as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.exclude_input_prompt = True
    html_exporter.template_name = 'lab'  # 使用 JupyterLab 样式
    body, _ = html_exporter.from_notebook_node(nb)
    
    html_path = f'{output_dir}/report_{report_date}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    print(f"✅ 报告已生成: {html_path}")
    return html_path

# 生成最近 7 天的报告
for i in range(7):
    d = date.today() - timedelta(days=i)
    generate_daily_report(d.isoformat())
```

## 步骤 6：集成到 CI/CD 流水线

### GitHub Actions 示例

```yaml
# .github/workflows/notebook-report.yml
name: Generate Notebook Report

on:
  schedule:
    - cron: '0 8 * * 1'  # 每周一 UTC 8:00 运行
  workflow_dispatch:      # 支持手动触发

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install jupyter nbconvert papermill pandas matplotlib
      
      - name: Execute and convert notebooks
        run: |
          jupyter nbconvert --to html --execute --no-input \
            --output-dir=reports \
            notebooks/weekly_analysis.ipynb
      
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: weekly-report
          path: reports/
```

### Makefile 集成

```makefile
# Makefile
NOTEBOOKS := $(wildcard notebooks/*.ipynb)
REPORTS := $(patsubst notebooks/%.ipynb,reports/%.html,$(NOTEBOOKS))

.PHONY: all clean

all: $(REPORTS)

reports/%.html: notebooks/%.ipynb
	@mkdir -p reports
	jupyter nbconvert --to html --execute --no-input \
	  --TagRemovePreprocessor.remove_input_tags='{"hide-input"}' \
	  --output-dir=reports $<

clean:
	rm -rf reports/
```

使用：`make all` 自动执行并转换所有 Notebook。

## 步骤 7：自定义模板

### 使用内置模板

```bash
# 使用 JupyterLab 样式（推荐）
jupyter nbconvert --to html --template lab my_notebook.ipynb

# 使用经典样式
jupyter nbconvert --to html --template classic my_notebook.ipynb

# 基础样式（无额外 CSS）
jupyter nbconvert --to html --template basic my_notebook.ipynb
```

### 创建自定义模板

创建 `templates/custom/index.html.j2`：

```html
{%- extends 'lab/index.html.j2' -%}

{% block html_head_css %}
{{ super() }}
<style>
body {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
/* 自定义代码样式 */
div.input_area {
    border-left: 3px solid #2196F3;
}
/* 自定义标题 */
h1 { color: #1976D2; border-bottom: 2px solid #1976D2; }
</style>
{% endblock html_head_css %}
```

使用自定义模板：

```bash
jupyter nbconvert --to html --template-file templates/custom/index.html.j2 my_notebook.ipynb
```

## 常见问题排查

### 问题 1：执行超时

```bash
# 增加超时时间
jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=600 notebook.ipynb
```

### 问题 2：Kernel 启动失败

确保 `kernel_name` 正确：

```python
# Python API 中指定正确的 kernel
ep = ExecutePreprocessor(kernel_name='python3')
```

```bash
# 命令行指定 kernel
jupyter nbconvert --to html --execute --ExecutePreprocessor.kernel_name=python3 notebook.ipynb
```

### 问题 3：Matplotlib 图表不显示

在 Notebook 开头添加：

```python
%matplotlib inline
import matplotlib.pyplot as plt
```

### 问题 4：图片未嵌入 HTML

默认情况下 HTML 中图片以 base64 嵌入（单文件）。如果图片被保存为外部文件，检查 `resources` 输出：

```python
body, resources = html_exporter.from_notebook_node(nb)
# resources['outputs'] 包含外部文件
if 'outputs' in resources:
    for filename, data in resources['outputs'].items():
        with open(filename, 'wb') as f:
            f.write(data)
```

使用 FilesWriter 自动处理：

```python
from nbconvert.writers import FilesWriter
writer = FilesWriter(build_directory='output')
writer.write(body, resources, notebook_name='report')
```

### 问题 5：中文 PDF 导出乱码

使用 XeLaTeX 引擎并配置中文字体：

```python
# 在 Notebook 中配置
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('pdf', 'svg')
```

或在命令行指定：

```bash
jupyter nbconvert --to pdf --PDFExporter.latex_engine=xelatex notebook.ipynb
```

确保安装了中文字体包（如 `texlive-lang-chinese`）。

## 验证清单

- [ ] 成功将 Notebook 转换为 HTML
- [ ] 使用 `--execute` 在转换前执行 Notebook
- [ ] 使用标签隐藏特定单元格
- [ ] 使用 Python API 编程式转换
- [ ] 使用 papermill 参数化生成多份报告
- [ ] 成功配置自定义模板样式
- [ ] 了解批量转换和 CI/CD 集成方法

## 相关概念

- [Notebook 文件格式（.ipynb）](../concepts/07-notebook-format.md) — Notebook 数据结构
- [Notebook 作为文档与转换](../concepts/10-notebook-doc-convert.md) — nbconvert 六阶段流程
- [交互式控件与富显示](../concepts/09-widgets-display.md) — Widget 输出在转换中的处理

---
type: "concept"
title: "Notebook执行与生态集成"
description: "ExecutePreprocessor执行机制、Jupyter Kernel集成、nbclient依赖、与Notebook/Papermill等工具协作"
tags: [execute, kernel, nbclient, execution, papermill, jupyter-ecosystem]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: preprocessor
    resource: ../references/preprocessor-source.md
    title: "预处理器系统源码解析"
  - id: nbconvert-base
    resource: ../references/nbconvert-base-source.md
    title: "NbConvertBase基础配置源码解析"
---

# Notebook执行与生态集成

nbconvert不只是静态格式转换工具，它通过ExecutePreprocessor可以执行Notebook代码并捕获输出，这是"可重复研究"和"自动化报告生成"的核心能力。

## ExecutePreprocessor 执行机制

ExecutePreprocessor是nbconvert中最强大的预处理器，它通过Jupyter Kernel执行Notebook中的代码单元，并将输出（stdout、stderr、display_data、错误）回写到Notebook对象中。

### 执行流程

```
ExecutePreprocessor.preprocess(nb, resources)
│
├─ 1. 启动Kernel（或连接已有Kernel）
│   └─ 通过jupyter_client连接内核
│
├─ 2. 按顺序执行每个code cell
│   ├─ 发送code到kernel
│   ├─ 等待执行完成
│   ├─ 收集output messages
│   │   ├─ stream → Stream输出
│   │   ├─ execute_result → 执行结果
│   │   ├─ display_data → 富媒体输出
│   │   └─ error → 错误traceback
│   └─ 将输出写入cell.outputs
│
├─ 3. 记录执行metadata
│   ├─ 执行耗时
│   └─ Kernel信息
│
└─ 4. 关闭Kernel
```

**注意**：ExecutePreprocessor的实现已迁移到独立包`nbclient`，nbconvert通过依赖nbclient来使用它。

### 关键配置选项

```python
c = get_config()

# 启用执行
c.ExecutePreprocessor.enabled = True

# Kernel设置
c.ExecutePreprocessor.kernel_name = "python3"  # 内核名称
c.ExecutePreprocessor.timeout = 30             # 单cell超时时间（秒），None为无超时
c.ExecutePreprocessor.startup_timeout = 60     # Kernel启动超时时间

# 错误处理
c.ExecutePreprocessor.allow_errors = False     # 遇到错误是否继续
c.ExecutePreprocessor.interrupt_on_timeout = True  # 超时后中断Kernel

# 执行记录
c.ExecutePreprocessor.record_timing = True     # 记录每个cell的执行时间
```

### CLI执行

```bash
# 基本执行+转换
jupyter nbconvert --execute --to html notebook.ipynb

# 执行出错时继续
jupyter nbconvert --execute --allow-errors --to html notebook.ipynb

# 指定超时时间（10分钟）
jupyter nbconvert --execute --ExecutePreprocessor.timeout=600 --to html notebook.ipynb

# 执行后原地保存（更新输出）
jupyter nbconvert --execute --to notebook --inplace notebook.ipynb
```

### Python API执行

```python
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.exporters import HTMLExporter
import nbformat

# 读取Notebook
with open("notebook.ipynb") as f:
    nb = nbformat.read(f, as_version=4)

# 创建执行预处理器
ep = ExecutePreprocessor(
    timeout=600,
    kernel_name="python3",
    allow_errors=False
)

# 执行Notebook
ep.preprocess(nb, {"metadata": {"path": "."}})

# 导出为HTML
exporter = HTMLExporter()
output, resources = exporter.from_notebook_node(nb)

# 保存结果
with open("output.html", "w") as f:
    f.write(output)
```

## 依赖生态

### 核心依赖

| 包 | 作用 | 是否必需 |
|----|------|---------|
| nbformat | Notebook文件格式读写 | 必需 |
| mistune | Markdown解析 | 必需（HTML导出） |
| jinja2 | 模板引擎 | 必需 |
| pygments | 代码高亮 | 必需 |
| jupyter_core | Jupyter核心工具 | 必需 |
| traitlets | 配置框架 | 必需 |
| bleach | HTML清洗（XSS防护） | HTML导出必需 |
| pandoc | 通用文档格式转换 | LaTeX/Markdown/RST/AsciiDoc必需 |
| defusedxml | XML安全解析 | SVG处理必需 |
| beautifulsoup4 | HTML解析 | 某些过滤器必需 |
| nbclient | Notebook执行 | ExecutePreprocessor必需 |

### 可选依赖

| 包 | 作用 | 安装方式 |
|----|------|---------|
| pandoc | LaTeX/PDF等格式转换 | 系统安装pandoc + pip install nbconvert[pandoc] |
| tornado | ServePostProcessor预览 | pip install nbconvert[serve] |
| playwright | WebPDF导出 | pip install nbconvert[webpdf] |
| pyqtwebengine | QtPDF/QtPNG导出 | pip install nbconvert[qt] |
| ipykernel | Python内核执行 | pip install nbconvert[execute] |

### 外部工具依赖

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| pandoc | 通用格式转换引擎 | apt install pandoc / brew install pandoc |
| TeX发行版 | PDF生成 | 安装TeX Live/MiKTeX |
| Chromium/Chrome | WebPDF截图 | playwright install chromium |

## 与其他Jupyter工具的协作

### Jupyter Notebook / JupyterLab

nbconvert是Jupyter生态的转换后端：
- Notebook界面的"Download as"菜单底层调用nbconvert
- JupyterLab的导出功能同样使用nbconvert

### Papermill（参数化Notebook执行）

Papermill在nbconvert基础上提供参数化执行能力：
1. Papermill执行参数化Notebook（注入参数、记录输出）
2. nbconvert将执行后的Notebook转换为报告格式

```python
import papermill as pm

# 参数化执行
pm.execute_notebook(
    "template.ipynb",
    "output.ipynb",
    parameters={"date": "2024-01-01", "ticker": "AAPL"}
)

# 使用nbconvert转换
import subprocess
subprocess.run([
    "jupyter", "nbconvert", "--to", "html",
    "--no-input", "output.ipynb"
])
```

### nbmake（Notebook测试）

nbmake是基于nbclient的pytest插件，将Notebook作为测试用例执行：
- 使用nbclient执行Notebook（与ExecutePreprocessor相同内核）
- 适合Notebook文档的CI测试

### jupytext

jupytext将Notebook与脚本/Markdown格式双向转换，可与nbconvert配合：
- jupytext处理Notebook ↔ py/md双向同步
- nbconvert处理Notebook → 输出格式转换

## 自动化报告生成模式

nbconvert的一个典型高级用法是自动化报告生成流水线：

```python
"""自动化报告生成示例"""
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.exporters import HTMLExporter
from nbconvert.exporters.pdf import PDFExporter
from nbconvert.writers import FilesWriter
from traitlets.config import Config
import datetime

def generate_report(template_path, output_dir, params=None):
    """
    执行Notebook模板并生成报告
    
    参数:
        template_path: Notebook模板路径
        output_dir: 输出目录
        params: 注入参数（通过修改首个code cell或papermill-style）
    """
    # 1. 读取模板Notebook
    with open(template_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    # 2. （可选）注入参数到第一个code cell
    if params:
        param_cell = nbformat.v4.new_code_cell(
            source="\n".join(f"{k} = {repr(v)}" for k, v in params.items())
        )
        nb.cells.insert(0, param_cell)
    
    # 3. 执行Notebook
    ep = ExecutePreprocessor(
        timeout=600,
        kernel_name="python3",
        allow_errors=False
    )
    ep.preprocess(nb, {"metadata": {"path": "."}})
    
    # 4. 生成HTML报告
    html_config = Config()
    html_config.HTMLExporter.exclude_input_prompt = True
    html_config.HTMLExporter.exclude_output_prompt = True
    html_config.TemplateExporter.template_name = "lab"
    
    html_exporter = HTMLExporter(config=html_config)
    html_output, html_resources = html_exporter.from_notebook_node(nb)
    
    # 5. 写入文件
    writer = FilesWriter(build_directory=output_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    writer.write(html_output, html_resources, notebook_name=f"report_{timestamp}")
    
    return f"{output_dir}/report_{timestamp}.html"

# 使用
report_path = generate_report(
    "analysis_template.ipynb",
    "./reports",
    params={"start_date": "2024-01-01", "end_date": "2024-12-31"}
)
print(f"报告已生成: {report_path}")
```

## 常见执行问题排查

### Kernel启动失败

```
RuntimeError: Kernel died before replying to kernel_info
```

排查：
1. 确认ipykernel已安装：`pip install ipykernel`
2. 确认kernel存在：`jupyter kernelspec list`
3. 检查kernel_name是否正确

### 执行超时

```
TimeoutError: Cell execution timed out
```

解决：
1. 增加timeout：`--ExecutePreprocessor.timeout=1200`
2. 检查是否有无限循环代码
3. 检查网络依赖是否可达

### Pandoc未找到

```
PandocMissing: Pandoc wasn't found
```

解决：
- Ubuntu/Debian: `sudo apt install pandoc`
- macOS: `brew install pandoc`
- Windows: 从pandoc官网下载安装
- 或者使用`--to html`/`--to markdown`（不需要pandoc的格式）

### LaTeX PDF生成失败

LaTeX导出PDF需要完整的TeX发行版：
- 推荐安装TeX Live
- 可能需要额外包：texlive-xetex, texlive-fonts-recommended, texlive-latex-extra
- 替代方案：使用`--to webpdf`（基于Playwright，不需要TeX）

## 相关概念

- [预处理器系统](04-preprocessor-system.md)
- [CLI与配置](08-cli-and-configuration.md)
- [5分钟快速上手](01-getting-started.md)

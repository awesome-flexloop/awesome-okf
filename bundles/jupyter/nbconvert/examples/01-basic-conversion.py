#!/usr/bin/env python
"""
示例1：基本Notebook转换
========================
演示nbconvert Python API的基本用法：
1. 将Notebook转换为各种格式
2. 使用不同的Writer
3. 配置导出选项

运行方式: python 01-basic-conversion.py
"""

import os
import nbformat

# 首先创建一个示例Notebook用于演示
def create_sample_notebook(path="sample_notebook.ipynb"):
    """创建一个示例Notebook"""
    nb = nbformat.v4.new_notebook(metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.8.0"}
    })
    
    # Markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("""# 示例Notebook

这是一个用于演示nbconvert的示例Notebook。

## 第一部分：基本计算
"""))
    
    # Code cell 1
    nb.cells.append(nbformat.v4.new_code_cell("""# 简单计算
x = 42
y = 18
print(f"x + y = {x + y}")
print(f"x * y = {x * y}")"""))
    
    # Code cell 2 with output
    cell = nbformat.v4.new_code_cell("""import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.legend()
plt.title('Sine and Cosine')
plt.savefig('plot.png', dpi=72)
plt.show()""")
    
    nb.cells.append(cell)
    
    # Markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("""## 第二部分：数据分析

使用pandas进行简单的数据分析。
"""))
    
    # Code cell
    nb.cells.append(nbformat.v4.new_code_cell("""import pandas as pd
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'score': [92, 85, 78]
})
df"""))
    
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    return path


def example_html_export():
    """示例1：HTML导出"""
    from nbconvert.exporters import HTMLExporter
    
    exporter = HTMLExporter()
    exporter.template_name = "lab"  # 使用lab模板
    
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    # output是渲染后的HTML字符串
    with open("output_basic.html", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✓ HTML导出完成: output_basic.html ({len(output)} 字符)")
    return output, resources


def example_markdown_export():
    """示例2：Markdown导出"""
    from nbconvert.exporters import MarkdownExporter
    
    exporter = MarkdownExporter()
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✓ Markdown导出完成: output.md ({len(output)} 字符)")
    
    # resources["outputs"]包含提取的图片资源
    if "outputs" in resources:
        print(f"  提取的资源文件: {list(resources['outputs'].keys())}")
    return output, resources


def example_python_export():
    """示例3：Python脚本导出"""
    from nbconvert.exporters import PythonExporter
    
    exporter = PythonExporter()
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    with open("output.py", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✓ Python脚本导出完成: output.py ({len(output)} 字符)")
    return output, resources


def example_with_config():
    """示例4：带配置的导出"""
    from nbconvert.exporters import HTMLExporter
    from traitlets.config import Config
    
    c = Config()
    # 隐藏输入提示
    c.HTMLExporter.exclude_input_prompt = True
    # 隐藏输出提示
    c.HTMLExporter.exclude_output_prompt = True
    # 使用lab主题
    c.HTMLExporter.theme = "dark"
    
    exporter = HTMLExporter(config=c)
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    with open("output_dark.html", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✓ 暗色主题HTML导出完成: output_dark.html")
    return output, resources


def example_files_writer():
    """示例5：使用FilesWriter自动处理资源文件"""
    from nbconvert.exporters import MarkdownExporter
    from nbconvert.writers import FilesWriter
    
    exporter = MarkdownExporter()
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    # FilesWriter会自动将图片等资源写入文件系统
    writer = FilesWriter(build_directory="./markdown_output")
    writer.write(output, resources, notebook_name="sample")
    print("✓ FilesWriter写入完成: markdown_output/ 目录")
    print("  文件列表:")
    for f in os.listdir("./markdown_output"):
        print(f"    - {f}")


def example_stdout_writer():
    """示例6：使用StdoutWriter输出到stdout"""
    from nbconvert.exporters import MarkdownExporter
    from nbconvert.writers import StdoutWriter
    import sys
    from io import StringIO
    
    exporter = MarkdownExporter()
    output, resources = exporter.from_filename("sample_notebook.ipynb")
    
    writer = StdoutWriter()
    # 重定向stdout以捕获输出（演示用）
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    writer.write(output, resources, notebook_name="sample")
    sys.stdout = old_stdout
    
    result = captured.getvalue()
    print(f"✓ StdoutWriter输出: {len(result)} 字符")
    print("  （在终端中运行会直接输出Markdown文本）")


if __name__ == "__main__":
    print("=" * 60)
    print("nbconvert 基本转换示例")
    print("=" * 60)
    
    # 创建示例Notebook
    print("\n[1] 创建示例Notebook...")
    nb_path = create_sample_notebook()
    print(f"✓ 示例Notebook已创建: {nb_path}")
    
    print("\n[2] HTML导出...")
    example_html_export()
    
    print("\n[3] Markdown导出...")
    example_markdown_export()
    
    print("\n[4] Python脚本导出...")
    example_python_export()
    
    print("\n[5] 带配置导出（暗色主题）...")
    example_with_config()
    
    print("\n[6] 使用FilesWriter...")
    example_files_writer()
    
    print("\n[7] 使用StdoutWriter...")
    example_stdout_writer()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成！")
    print("生成的文件：")
    for f in ["sample_notebook.ipynb", "output_basic.html", "output.md", 
              "output.py", "output_dark.html"]:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"  ✓ {f} ({size} bytes)")
    if os.path.exists("markdown_output"):
        print(f"  ✓ markdown_output/ (目录)")
    print("=" * 60)

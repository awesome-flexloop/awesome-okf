#!/usr/bin/env python
"""
示例2：执行Notebook并生成报告
=================================
演示使用ExecutePreprocessor执行Notebook代码，
捕获输出后转换为各种报告格式。

运行方式: python 02-execute-notebook.py
依赖: pip install nbconvert[execute]  (需安装ipykernel)
"""

import os
import nbformat


def create_analysis_notebook(path="analysis.ipynb"):
    """创建一个数据分析Notebook模板"""
    nb = nbformat.v4.new_notebook(metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}
    })
    
    # 标题
    nb.cells.append(nbformat.v4.new_markdown_cell("""# 数据分析报告

本报告由nbconvert自动执行生成。
"""))
    
    # 导入库
    nb.cells.append(nbformat.v4.new_code_cell("""import sys
print(f"Python版本: {sys.version}")

import datetime
print(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")"""))
    
    # 数据生成
    nb.cells.append(nbformat.v4.new_code_cell("""import numpy as np
import pandas as pd

# 生成示例数据
np.random.seed(42)
n_samples = 1000
data = pd.DataFrame({
    'category': np.random.choice(['A', 'B', 'C'], n_samples),
    'value': np.random.randn(n_samples) * 10 + 50,
    'score': np.random.uniform(0, 100, n_samples)
})

print(f"数据形状: {data.shape}")
data.head()"""))
    
    # 统计分析
    nb.cells.append(nbformat.v4.new_code_cell("""# 描述性统计
stats = data.groupby('category').agg({
    'value': ['mean', 'std', 'min', 'max'],
    'score': ['mean', 'std']
}).round(2)
stats"""))
    
    # 可视化
    nb.cells.append(nbformat.v4.new_code_cell("""try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # 直方图
    axes[0].hist(data['value'], bins=30, alpha=0.7, color='steelblue')
    axes[0].set_title('Value Distribution')
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Frequency')
    
    # 箱线图
    data.boxplot(column='value', by='category', ax=axes[1])
    axes[1].set_title('Value by Category')
    axes[1].set_xlabel('Category')
    
    plt.tight_layout()
    plt.savefig('analysis_plot.png', dpi=100, bbox_inches='tight')
    plt.show()
    print("图表已生成")
except ImportError:
    print("matplotlib未安装，跳过图表生成")"""))
    
    # 结论
    nb.cells.append(nbformat.v4.new_markdown_cell("""## 结论

- 数据共包含{n_samples}条记录
- 三个类别的分布均匀
- Value字段近似正态分布

*本报告由nbconvert自动生成*
""".format(n_samples=1000)))
    
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    return path


def example_basic_execute():
    """示例1：基本执行并导出HTML"""
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.exporters import HTMLExporter
    from nbconvert.writers import FilesWriter
    
    # 读取Notebook
    with open("analysis.ipynb") as f:
        nb = nbformat.read(f, as_version=4)
    
    # 创建执行预处理器
    ep = ExecutePreprocessor(
        timeout=120,          # 单cell超时时间
        kernel_name="python3",
        allow_errors=False    # 遇错误中止
    )
    
    print("  执行Notebook...")
    # 执行Notebook（path参数用于设置工作目录，处理相对路径）
    ep.preprocess(nb, {"metadata": {"path": "."}})
    print("  ✓ Notebook执行完成")
    
    # 保存执行后的Notebook（包含输出）
    with open("analysis_executed.ipynb", "w") as f:
        nbformat.write(nb, f)
    print("  ✓ 已保存执行后的Notebook: analysis_executed.ipynb")
    
    # 导出为HTML
    exporter = HTMLExporter(template_name="lab")
    output, resources = exporter.from_notebook_node(nb)
    
    writer = FilesWriter(build_directory="./report_output")
    writer.write(output, resources, notebook_name="analysis_report")
    print("  ✓ HTML报告已生成: ./report_output/analysis_report.html")


def example_execute_with_timing():
    """示例2：记录执行时间"""
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.exporters import NotebookExporter
    
    with open("analysis.ipynb") as f:
        nb = nbformat.read(f, as_version=4)
    
    ep = ExecutePreprocessor(
        timeout=120,
        record_timing=True  # 记录每个cell的执行时间
    )
    
    ep.preprocess(nb, {"metadata": {"path": "."}})
    
    # 查看执行时间
    print("  Cell执行时间:")
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            timing = cell.metadata.get("execution", {})
            elapsed = timing.get("iopub.status.busy", None)
            if elapsed:
                # 实际时间存储在metadata中
                pass
            # 简单统计
            print(f"    Cell {i}: code cell executed")
    
    # 导出执行后的Notebook
    exporter = NotebookExporter()
    output, resources = exporter.from_notebook_node(nb)
    with open("analysis_with_timing.ipynb", "w") as f:
        f.write(output)
    print("  ✓ 已保存带时间记录的Notebook: analysis_with_timing.ipynb")


def example_execute_allow_errors():
    """示例3：允许错误继续执行"""
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.exporters import HTMLExporter
    
    # 创建一个包含错误的Notebook
    nb = nbformat.v4.new_notebook(metadata={
        "kernelspec": {"name": "python3"}
    })
    nb.cells.append(nbformat.v4.new_code_cell("print('正常执行')"))
    nb.cells.append(nbformat.v4.new_code_cell("1 / 0  # 这会抛出ZeroDivisionError"))
    nb.cells.append(nbformat.v4.new_code_cell("print('错误后的cell仍然执行')"))
    
    ep = ExecutePreprocessor(
        timeout=30,
        allow_errors=True  # 关键设置：允许错误继续执行
    )
    
    print("  执行含错误的Notebook（allow_errors=True）...")
    ep.preprocess(nb, {"metadata": {"path": "."}})
    
    # 导出HTML，错误信息会显示在输出中
    exporter = HTMLExporter()
    output, resources = exporter.from_notebook_node(nb)
    
    with open("output_with_errors.html", "w") as f:
        f.write(output)
    print("  ✓ 含错误输出的HTML: output_with_errors.html")
    print("  （错误信息会以红色traceback显示）")


def example_execute_to_pdf():
    """示例4：执行并生成PDF（需pandoc和LaTeX，或playwright）"""
    from nbconvert.preprocessors import ExecutePreprocessor
    
    with open("analysis.ipynb") as f:
        nb = nbformat.read(f, as_version=4)
    
    ep = ExecutePreprocessor(timeout=120)
    ep.preprocess(nb, {"metadata": {"path": "."}})
    
    # 方法1：通过LaTeX生成PDF（需要安装TeX Live）
    try:
        from nbconvert.exporters import PDFExporter
        exporter = PDFExporter()
        output, resources = exporter.from_notebook_node(nb)
        with open("analysis_report.pdf", "wb") as f:
            f.write(output)
        print("  ✓ PDF报告已生成（LaTeX方式）: analysis_report.pdf")
    except Exception as e:
        print(f"  LaTeX PDF生成跳过: {e}")
        print("  提示: 可使用 --to webpdf 通过Playwright生成PDF")


def example_inplace_update():
    """示例5：原地更新Notebook输出"""
    import shutil
    # 复制一份Notebook用于原地更新演示
    shutil.copy("analysis.ipynb", "analysis_inplace.ipynb")
    
    from nbconvert.preprocessors import ExecutePreprocessor
    
    with open("analysis_inplace.ipynb") as f:
        nb = nbformat.read(f, as_version=4)
    
    ep = ExecutePreprocessor(timeout=120)
    ep.preprocess(nb, {"metadata": {"path": "."}})
    
    # 写回原文件
    with open("analysis_inplace.ipynb", "w") as f:
        nbformat.write(nb, f)
    print("  ✓ Notebook原地更新完成: analysis_inplace.ipynb")


if __name__ == "__main__":
    print("=" * 60)
    print("nbconvert Notebook执行示例")
    print("=" * 60)
    
    # 检查ipykernel
    try:
        import ipykernel
        has_kernel = True
    except ImportError:
        has_kernel = False
        print("\n⚠️  警告: ipykernel未安装，执行示例需要安装:")
        print("   pip install nbconvert[execute]")
        print("   python -m ipykernel install --user")
    
    print("\n[1] 创建数据分析Notebook...")
    nb_path = create_analysis_notebook()
    print(f"✓ 已创建: {nb_path}")
    
    if has_kernel:
        print("\n[2] 基本执行并导出HTML...")
        example_basic_execute()
        
        print("\n[3] 记录执行时间...")
        try:
            example_execute_with_timing()
        except Exception as e:
            print(f"  跳过: {e}")
        
        print("\n[4] 允许错误继续执行...")
        example_execute_allow_errors()
        
        print("\n[5] 生成PDF（需要LaTeX）...")
        try:
            example_execute_to_pdf()
        except Exception as e:
            print(f"  跳过PDF生成: {e}")
        
        print("\n[6] 原地更新Notebook...")
        example_inplace_update()
    else:
        print("\n跳过执行示例（需要ipykernel）")
        print("可以使用CLI命令执行:")
        print("  jupyter nbconvert --execute --to html analysis.ipynb")
    
    print("\n" + "=" * 60)
    print("CLI命令参考:")
    print("  执行并导出HTML: jupyter nbconvert --execute --to html notebook.ipynb")
    print("  执行并原地保存: jupyter nbconvert --execute --to notebook --inplace nb.ipynb")
    print("  允许错误: jupyter nbconvert --execute --allow-errors --to html nb.ipynb")
    print("=" * 60)

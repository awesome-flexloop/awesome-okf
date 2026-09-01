#!/usr/bin/env python
"""
示例4：批量转换与自动化流水线
================================
演示nbconvert的批量处理、自动化报告生成、
配置文件使用、以及构建文档流水线的模式。

运行方式: python 04-batch-conversion-pipeline.py
"""

import os
import glob
import json
import nbformat
from pathlib import Path
from datetime import datetime
from traitlets.config import Config


# ============================================================
# 工具函数
# ============================================================

def create_example_notebooks(output_dir="notebooks"):
    """创建一组示例Notebook用于批量处理演示"""
    os.makedirs(output_dir, exist_ok=True)
    
    notebooks = {
        "01_introduction.ipynb": {
            "title": "介绍",
            "content": [
                ("markdown", "# 第一章：介绍\n\n欢迎阅读本教程。"),
                ("code", 'print("Hello, World!")'),
                ("markdown", "## 本节要点\n\n- 了解基础概念\n- 掌握核心方法"),
            ]
        },
        "02_basics.ipynb": {
            "title": "基础",
            "content": [
                ("markdown", "# 第二章：基础\n\n本章介绍基础知识。"),
                ("code", "x = 10\ny = 20\nprint(f'{x} + {y} = {x+y}')"),
                ("code", "numbers = [1, 2, 3, 4, 5]\nprint(f'总和: {sum(numbers)}')"),
            ]
        },
        "03_advanced.ipynb": {
            "title": "进阶",
            "content": [
                ("markdown", "# 第三章：进阶\n\n本章讨论进阶主题。"),
                ("code", """class Calculator:
    def __init__(self):
        self.result = 0
    def add(self, x):
        self.result += x
        return self

calc = Calculator()
calc.add(10).add(20)
print(f'结果: {calc.result}')"""),
                ("markdown", "## 总结\n\n恭喜完成进阶内容。"),
            ]
        }
    }
    
    for filename, config in notebooks.items():
        nb = nbformat.v4.new_notebook(metadata={
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"}
        })
        for cell_type, source in config["content"]:
            if cell_type == "markdown":
                nb.cells.append(nbformat.v4.new_markdown_cell(source))
            else:
                nb.cells.append(nbformat.v4.new_code_cell(source))
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
    
    print(f"  ✓ 创建了 {len(notebooks)} 个示例Notebook在 {output_dir}/")
    return output_dir


# ============================================================
# 批量转换器
# ============================================================

class BatchConverter:
    """批量Notebook转换器"""
    
    def __init__(self, input_dir, output_dir, format="html", config=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.format = format
        self.config = config or Config()
        self.results = []
    
    def get_exporter(self):
        """根据格式获取导出器"""
        from nbconvert.exporters import (
            HTMLExporter, MarkdownExporter, PythonExporter,
            LatexExporter, PDFExporter, NotebookExporter,
            SlidesExporter, RSTExporter
        )
        
        exporters = {
            "html": HTMLExporter,
            "markdown": MarkdownExporter,
            "python": PythonExporter,
            "latex": LatexExporter,
            "pdf": PDFExporter,
            "notebook": NotebookExporter,
            "slides": SlidesExporter,
            "rst": RSTExporter,
        }
        
        exporter_class = exporters.get(self.format, HTMLExporter)
        return exporter_class(config=self.config)
    
    def convert_file(self, notebook_path):
        """转换单个文件"""
        from nbconvert.writers import FilesWriter
        
        try:
            exporter = self.get_exporter()
            output, resources = exporter.from_filename(str(notebook_path))
            
            writer = FilesWriter(build_directory=str(self.output_dir))
            notebook_name = Path(notebook_path).stem
            writer.write(output, resources, notebook_name=notebook_name)
            
            ext = resources.get("output_extension", f".{self.format}")
            output_file = self.output_dir / f"{notebook_name}{ext}"
            
            return {
                "input": str(notebook_path),
                "output": str(output_file),
                "status": "success",
                "format": self.format
            }
        except Exception as e:
            return {
                "input": str(notebook_path),
                "status": "error",
                "error": str(e)
            }
    
    def convert_all(self):
        """批量转换所有Notebook"""
        notebooks = sorted(self.input_dir.glob("*.ipynb"))
        
        # 排除checkpoint文件
        notebooks = [nb for nb in notebooks if "checkpoint" not in nb.name]
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"  开始批量转换 {len(notebooks)} 个文件为 {self.format}...")
        
        for i, nb_path in enumerate(notebooks, 1):
            print(f"  [{i}/{len(notebooks)}] 转换: {nb_path.name}...", end=" ")
            result = self.convert_file(nb_path)
            self.results.append(result)
            print(result["status"])
        
        return self.results
    
    def summary(self):
        """生成转换摘要"""
        success = [r for r in self.results if r["status"] == "success"]
        errors = [r for r in self.results if r["status"] == "error"]
        
        return {
            "total": len(self.results),
            "success": len(success),
            "error": len(errors),
            "errors": [r["error"] for r in errors],
            "outputs": [r["output"] for r in success]
        }


# ============================================================
# 配置文件示例
# ============================================================

def create_config_file(path="nbconvert_config.py"):
    """创建一个示例配置文件"""
    config_content = '''# nbconvert配置文件示例
# 使用方式: jupyter nbconvert --config nbconvert_config.py notebooks/*.ipynb

c = get_config()

# === 导出设置 ===
c.NbConvertApp.export_format = "html"
c.FilesWriter.build_directory = "./docs_output"

# === 模板设置 ===
c.TemplateExporter.template_name = "lab"
c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True

# === HTML设置 ===
c.HTMLExporter.theme = "light"

# === 内容过滤 ===
# 取消注释以隐藏代码输入
# c.TemplateExporter.exclude_input = True

# === 预处理器 ===
# 启用TagRemove预处理器
c.HTMLExporter.preprocessors = [
    "nbconvert.preprocessors.TagRemovePreprocessor",
    "nbconvert.preprocessors.ClearMetadataPreprocessor",
]
c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell", "solution")
c.TagRemovePreprocessor.remove_input_tags = ("hide_input",)
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✓ 配置文件已创建: {path}")
    return path


# ============================================================
# 文档站点生成器
# ============================================================

class DocSiteGenerator:
    """从Notebook生成文档站点"""
    
    def __init__(self, notebooks_dir, output_dir, site_title="Documentation"):
        self.notebooks_dir = Path(notebooks_dir)
        self.output_dir = Path(output_dir)
        self.site_title = site_title
    
    def build(self):
        """构建文档站点"""
        # 1. 转换所有Notebook为HTML
        c = Config()
        c.HTMLExporter.template_name = "lab"
        c.HTMLExporter.exclude_input_prompt = True
        c.HTMLExporter.exclude_output_prompt = True
        
        converter = BatchConverter(
            str(self.notebooks_dir),
            str(self.output_dir),
            format="html",
            config=c
        )
        results = converter.convert_all()
        summary = converter.summary()
        
        if summary["error"] > 0:
            print(f"  警告: {summary['error']} 个文件转换失败")
        
        # 2. 生成索引页
        self._generate_index(summary["outputs"])
        
        return summary
    
    def _generate_index(self, output_files):
        """生成索引页"""
        # 提取标题
        pages = []
        for output_file in output_files:
            name = Path(output_file).stem
            # 尝试从文件名提取序号和标题
            parts = name.split("_", 1)
            if len(parts) == 2 and parts[0].isdigit():
                num = int(parts[0])
                title = parts[1].replace("_", " ").title()
            else:
                num = 0
                title = name.replace("_", " ").title()
            pages.append({
                "num": num,
                "title": title,
                "file": Path(output_file).name
            })
        
        pages.sort(key=lambda x: x["num"])
        
        # 生成HTML索引
        links_html = "\n".join(
            f'      <li><a href="{p["file"]}">{p["title"]}</a></li>'
            for p in pages
        )
        
        index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.site_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
        h1 {{ color: #2c5282; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 10px 0; }}
        a {{ color: #4a90d9; text-decoration: none; font-size: 1.1em; }}
        a:hover {{ text-decoration: underline; }}
        .meta {{ color: #888; font-size: 0.9em; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <h1>📚 {self.site_title}</h1>
    <p>最后生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <ul>
{links_html}
    </ul>
    <div class="meta">
        由 nbconvert 自动生成
    </div>
</body>
</html>"""
        
        index_path = self.output_dir / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        print(f"  ✓ 索引页已生成: {index_path}")


# ============================================================
# 示例执行
# ============================================================

def example_batch_html():
    """示例1：批量转换为HTML"""
    print("\n--- 批量转换为HTML ---")
    c = Config()
    c.HTMLExporter.template_name = "lab"
    c.HTMLExporter.exclude_input_prompt = True
    
    converter = BatchConverter("notebooks", "./batch_output/html", "html", c)
    converter.convert_all()
    summary = converter.summary()
    print(f"  完成: {summary['success']}/{summary['total']} 成功")
    return summary


def example_batch_markdown():
    """示例2：批量转换为Markdown"""
    print("\n--- 批量转换为Markdown ---")
    converter = BatchConverter("notebooks", "./batch_output/markdown", "markdown")
    converter.convert_all()
    summary = converter.summary()
    print(f"  完成: {summary['success']}/{summary['total']} 成功")
    return summary


def example_batch_python():
    """示例3：批量转换为Python脚本"""
    print("\n--- 批量转换为Python脚本 ---")
    converter = BatchConverter("notebooks", "./batch_output/scripts", "python")
    converter.convert_all()
    summary = converter.summary()
    print(f"  完成: {summary['success']}/{summary['total']} 成功")
    return summary


def example_generate_docs_site():
    """示例4：生成文档站点"""
    print("\n--- 生成文档站点 ---")
    site = DocSiteGenerator("notebooks", "./docs_site", "My Tutorial")
    summary = site.build()
    print(f"  文档站点生成完成: {summary['success']} 个页面")
    print(f"  查看: ./docs_site/index.html")
    return summary


def example_config_file():
    """示例5：生成配置文件"""
    print("\n--- 生成配置文件 ---")
    config_path = create_config_file("nbconvert_config.py")
    
    print(f"\n  使用配置文件的CLI命令:")
    print(f"    jupyter nbconvert --config {config_path} notebooks/*.ipynb")
    return config_path


def example_metadata_report():
    """示例6：生成转换报告JSON"""
    print("\n--- 生成转换元数据报告 ---")
    
    # 从之前的转换结果生成报告
    report = {
        "generated_at": datetime.now().isoformat(),
        "input_directory": "notebooks",
        "outputs": {}
    }
    
    # 收集各格式的输出
    for fmt in ["html", "markdown"]:
        output_dir = Path(f"./batch_output/{fmt}")
        if output_dir.exists():
            files = [f.name for f in output_dir.glob(f"*.{fmt}") if f.is_file()]
            report["outputs"][fmt] = files
    
    report_path = "./batch_output/conversion_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 转换报告: {report_path}")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    print("=" * 60)
    print("nbconvert 批量转换与自动化流水线示例")
    print("=" * 60)
    
    # 创建示例Notebook
    print("\n[1] 创建示例Notebook...")
    create_example_notebooks("notebooks")
    
    # 各种批量转换示例
    print("\n[2] 批量转换示例")
    example_batch_html()
    example_batch_markdown()
    example_batch_python()
    
    # 文档站点生成
    print("\n[3] 生成文档站点...")
    example_generate_docs_site()
    
    # 配置文件
    print("\n[4] 配置文件...")
    example_config_file()
    
    # 转换报告
    print("\n[5] 转换报告...")
    example_metadata_report()
    
    print("\n" + "=" * 60)
    print("批量转换完成！输出目录：")
    for d in ["./batch_output/html", "./batch_output/markdown", 
              "./batch_output/scripts", "./docs_site"]:
        if os.path.exists(d):
            files = os.listdir(d)
            print(f"  ✓ {d}/ ({len(files)} 个文件)")
    print("\nCLI批量转换命令参考：")
    print("  单文件:  jupyter nbconvert --to html notebook.ipynb")
    print("  多文件:  jupyter nbconvert --to html *.ipynb")
    print("  递归:    jupyter nbconvert --to html notebooks/*.ipynb")
    print("  配置:    jupyter nbconvert --config my_config.py *.ipynb")
    print("=" * 60)

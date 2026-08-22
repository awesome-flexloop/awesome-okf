---
type: Reference
title: "talks.yml 演讲配置源码解析"
description: "talks.yml 中四种演讲场景（test_talk/scipy2017/jupytercon2017/demo）的配置明细与文件映射关系"
tags: [talks, yaml, configuration, scipy, jupytercon, demo-setup]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: talks-source, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/talks.yml", title: "talks.yml source" }
---

# talks.yml 演讲配置源码信源

## 源码路径

`external/libs/jupyter/jupyterlab-demo/talks.yml`

## 四种演讲场景配置

### test_talk（测试配置）

最小测试配置，用于验证 build.py 基本功能。

```yaml
test_talk:
    folders:
        demofiles/TCGA: TCGA
    files:
        - data/iris.csv
    rename:
        iris.csv : iris_renamed.csv
```

- 复制 TCGA 数据目录
- 复制 iris.csv 并重命名为 iris_renamed.csv

### scipy2017（SciPy 2017 会议演示）

面向 SciPy 2017 会议的演示配置。

```yaml
scipy2017:
    files:
        - data/iris.csv
        - data/1024px-Hubble_Interacting_Galaxy_AM_0500-620_(2008-04-24).jpg
        - data/Museums_in_DC.geojson
        - narrative/scipy2017.md
    rename:
        demofiles/urban-data-challenge/public-transportation/geneva/schedule-real-time.csv: big.csv
        demofiles/tcga/extra_data/c2.cp.v3.0.symbols_edit.csv: smaller.csv
        demofiles/altair/altair/examples/json/field_spaces.vl.json: vega.vl.json
        demofiles/pythondatasciencehandbook/notebooks/03.08-aggregation-and-grouping.ipynb: notebook.ipynb
```

- 包含：iris数据、哈勃星系图片、DC博物馆GeoJSON、scipy2017演示脚本
- 重命名：大数据CSV→big.csv、小数据CSV→smaller.csv、Vega-Lite配置→vega.vl.json、Pandas手册Notebook→notebook.ipynb

### jupytercon2017（JupyterCon 2017 会议演示）

面向 JupyterCon 2017（纽约）的演示配置。

```yaml
jupytercon2017:
    files:
        - data/iris.csv
        - data/1024px-Hubble_Interacting_Galaxy_AM_0500-620_(2008-04-24).jpg
        - data/Museums_in_DC.geojson
        - narrative/markdown_python.md
    rename:
        # 与 scipy2017 相同的四个 rename
```

与 scipy2017 的区别：
- narrative 使用 `markdown_python.md` 而非 `scipy2017.md`
- rename 映射相同

### demo（通用演示配置）—— 最完整的配置

```yaml
demo:
    files:
        - slides/jupyterlab-slides.pdf
        - narrative/jupyterlab.md
        - narrative/markdown_python.md
    folders:
        demofiles/TCGA/Extra_Data: TCGA_Data
        notebooks: notebooks
        data: data
    rename:
        demofiles/Urban-Data-Challenge/.../schedule-real-time.csv: big.csv
        demofiles/tcga/.../c2.cp.v3.0.symbols_edit.csv: smaller.csv
        demofiles/altair/altair/v1/examples/json/bar.vl.json: vega.vl.json
        demofiles/PythonDataScienceHandbook/.../03.08-Aggregation-and-Grouping.ipynb: notebooks/pandas.ipynb
        "demofiles/bqplot/examples/Basic Plotting/Basic Plotting.ipynb": notebooks/bqplot.ipynb
        "1024px-Hubble_Interacting_Galaxy_...jpg": hubble.jpg
        notebooks/Lorenz.ipynb: Lorenz.ipynb
        notebooks/lorenz.py: lorenz.py
```

### 关键重命名映射表

| 源路径 | 目标名称 | 用途 |
|--------|---------|------|
| Urban-Data-Challenge/.../schedule-real-time.csv | big.csv | 200MB大数据CSV（DataGrid演示） |
| tcga/.../c2.cp.v3.0.symbols_edit.csv | smaller.csv | 小数据CSV（DataGrid对比演示） |
| altair/.../bar.vl.json | vega.vl.json | Vega-Lite图表示例 |
| PythonDataScienceHandbook/.../03.08-*.ipynb | notebooks/pandas.ipynb | Pandas数据处理示例 |
| bqplot/.../Basic Plotting.ipynb | notebooks/bqplot.ipynb | bqplot交互式绘图示例 |
| Hubble星系图片 | hubble.jpg | 图片查看器演示 |
| notebooks/Lorenz.ipynb | Lorenz.ipynb | 洛伦兹吸引子3D可视化 |
| notebooks/lorenz.py | lorenz.py | 洛伦兹求解辅助模块 |

---
type: Example
title: "添加新Notebook并通过测试"
description: "完整演示如何为Try Jupyter添加新的演示notebook：在线编辑、下载放置、注册已知警告、运行UI测试验证的全流程。"
tags: [example, add-notebook, content, testing, playwright, known-warnings]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebooks
    resource: "/concepts/06-notebooks-and-content.md"
    title: "Notebook内容与数据"
  - id: testing
    resource: "/concepts/07-ui-testing.md"
    title: "UI测试框架"
---

# 示例：添加新Notebook并通过测试

本示例演示如何为Try Jupyter站点添加一个新的演示notebook，并通过Playwright E2E测试验证。

## 前置条件

- 已完成[本地构建与预览](01-local-build.md)
- pixi环境已安装（`pixi install`）
- Playwright浏览器已安装（`pixi run playwright install --with-deps chromium`）

## 推荐方式：在线编辑

README推荐使用在线Try Jupyter站点编辑notebook，避免本地内核信息覆盖。

### 步骤1：在线创建Notebook

1. 打开 https://jupyter.org/try-jupyter
2. 选择目标内核（Launcher中点击对应内核的卡片）
3. 编写notebook内容
4. 保存notebook（Ctrl+S）

### 步骤2：下载Notebook

1. 在JupyterLab中，右键点击notebook文件
2. 选择 Download
3. 保存到本地 `content/notebooks/` 目录，命名为有意义的名称，如 `data-visualization.ipynb`

> 文件名使用kebab-case（小写字母+连字符），与现有notebook命名风格一致。

## 备选方式：本地编辑

如果需要在本地编辑（如使用本地Jupyter），注意：

1. 本地编辑的notebook会包含本地内核metadata
2. 提交前需要清理kernel metadata
3. 清理方法：用文本编辑器打开.ipynb文件，检查 `metadata.kernelspec` 字段是否指向JupyterLite内核

## 步骤3：添加示例数据（如需要）

如果notebook需要数据文件：

1. 将数据文件放入 `content/data/` 目录
2. 在notebook中使用相对路径引用数据：`data/your-data-file.csv`
3. 支持的数据格式：
   - CSV（pandas直接读取）
   - GeoJSON（jupyterlab-geojson查看器）
   - FASTA（jupyterlab-fasta查看器）
   - PNG/JPG图片
   - WAV音频
   - JSON/Vega-Lite规范

示例：
```python
import pandas as pd
df = pd.read_csv("data/iris.csv")
df.head()
```

## 步骤4：本地测试Notebook

构建站点并测试新notebook是否正常执行：

```bash
# 构建站点（如已构建可跳过）
pixi run build && pixi run filter-kernels

# 启动预览服务器
pixi run python -m http.server 8000 --directory dist
```

在浏览器中打开 http://localhost:8000/lab/index.html ，手动打开新notebook，执行 Run → Run All Cells，确认：
- 所有cell正常执行
- 没有红色错误输出
- 可视化图表正常显示
- Widget交互正常

## 步骤5：运行自动化测试

```bash
pixi run test
```

测试会自动发现 `content/notebooks/` 目录下的所有 `.ipynb` 文件（包括你新添加的），逐个在浏览器中执行。

### 如果测试失败

#### 情况1：预期的stderr输出

某些notebook会产生预期的stderr输出（如警告信息），需要注册到已知警告列表。

编辑 `ui-tests/utils.py`，在 `KNOWN_WARNINGS_BY_NOTEBOOK` 字典中添加条目：

```python
KNOWN_WARNINGS_BY_NOTEBOOK = {
    # ... 现有的 ...
    "data-visualization.ipynb": [
        "Matplotlib is building the font cache; this may take a moment.",
        # 添加你的notebook预期会产生的警告信息
    ],
}
```

匹配规则：使用**子字符串匹配**（`warning in stderr_text`），不需要完整匹配整行。

#### 情况2：Notebook执行超时

默认超时是5分钟（300,000ms）。如果notebook计算量较大（如光线追踪），可能需要调整超时。

但建议：
- 保持notebook轻量（demo性质，5分钟内完成）
- 如果确实需要更长时间，可在 `ui-tests/test_notebooks.py` 中调整TIMEOUT常量，或为特定notebook单独设置

#### 情况3：需要用户输入

如果notebook中有 `input()` 调用，测试框架会自动输入"test_input"并按回车。确保notebook在收到"test_input"时能正常继续执行。

#### 情况4：真正的代码错误

如果notebook中有代码错误，修复notebook后重新测试。

## 步骤6：检查测试产物

测试完成后：
- 控制台显示每个notebook的测试结果（PASSED/FAILED）
- HTML报告生成在 `ui-tests/report.html`，用浏览器打开查看详情
- 失败的测试会生成截图 `ui-tests/screenshot_{name}.png`

```bash
# 查看测试报告
start ui-tests/report.html  # Windows
# 或 open ui-tests/report.html  # macOS
```

## 现有Notebook的已知警告参考

| Notebook | 已知警告 | 原因 |
|----------|---------|------|
| Intro.ipynb | Matplotlib字体缓存 | Matplotlib首次加载 |
| Lorenz.ipynb | Matplotlib字体缓存 | Matplotlib首次加载 |
| r.ipynb | "Attaching package:" | R加载包的标准消息 |
| sqlite.ipynb | "Error: no such table: players" | 演示错误处理的预期错误 |
| cpp.ipynb | "some error" | C++内核的已知输出 |

## Notebook编写建议

### 保持轻量

- 每个notebook聚焦一个主题/语言
- 执行时间控制在5分钟以内
- 避免过大的数据文件（站点体积限制）

### 包含Markdown说明

- 开头1-2段介绍notebook内容
- 关键步骤使用Markdown标题分节
- 代码单元有注释说明

### 测试友好

- 避免需要用户输入（或确保输入"test_input"不会导致错误）
- 避免依赖网络请求（CORS限制）
- 设置随机种子以确保结果可重现
- 使用相对路径引用数据文件

### 多语言Notebook约定

| 语言 | 内核选择 | 参考Notebook |
|------|---------|-------------|
| Python | Pyodide/Xeus-Python | Intro.ipynb |
| C++ | C++23内核 | cpp.ipynb |
| R | R内核 | r.ipynb |
| SQL | SQLite内核 | sqlite.ipynb |

## 完整流程速查

```bash
# 1. 构建站点
cp README.md content
pixi run build && pixi run filter-kernels

# 2. 手动验证（浏览器打开 http://localhost:8000）
pixi run python -m http.server 8000 --directory dist

# 3. 如有已知警告，编辑 ui-tests/utils.py

# 4. 运行自动化测试
pixi run test

# 5. 查看报告
start ui-tests/report.html
```

## 相关示例

- [本地构建与预览](01-local-build.md)
- [自定义内核环境](02-custom-kernel.md)

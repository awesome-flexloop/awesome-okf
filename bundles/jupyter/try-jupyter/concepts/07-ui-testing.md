---
type: Concept
title: "UI测试框架：Playwright端到端测试"
description: "详解Try Jupyter的Playwright E2E测试体系：conftest.py fixtures、HTTP服务器自动启动、notebook自动发现与参数化、cell执行监控、stderr错误检测、已知警告过滤、失败重试与视频录制。"
tags: [playwright, e2e-testing, pytest, ui-tests, browser-automation, notebook-execution, automated-testing]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: test-source
    resource: "/references/test-source.md"
    title: "测试框架信源"
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml信源"
  - id: ci
    resource: "/references/ci-source.md"
    title: "CI/CD工作流信源"
---

# UI测试框架：Playwright端到端测试

Try Jupyter 使用 **Playwright + pytest** 构建端到端（E2E）测试体系，自动在真实浏览器中打开每个notebook，执行所有cell，并验证无未预期的错误。这是确保JupyterLite站点质量的核心防线。

## 测试架构概览

```
┌─────────────────────────────────────────────────────┐
│                   pytest 会话                        │
│                                                     │
│  conftest.py (session级fixtures)                     │
│  ├── find_free_port() → 随机空闲端口                 │
│  ├── dist_dir → 验证dist/存在                        │
│  ├── server_port → 空闲端口                         │
│  ├── http_server (autouse) → 启动Python HTTP服务器   │
│  ├── base_url → http://localhost:{port}             │
│  └── browser_context_args → 视频录制配置              │
│                                                     │
│  test_notebooks.py (参数化测试)                       │
│  └── 对每个.ipynb文件:                               │
│      ├── 构造URL → page.goto()                      │
│      ├── wait_for_jupyterlite_ready()               │
│      ├── wait_for_notebook_ready()                  │
│      ├── execute_all_cells() → 点击Run All Cells     │
│      ├── check_for_errors() → 检查stderr             │
│      └── assert not errors                          │
│                                                     │
│  utils.py (工具函数)                                 │
│  ├── wait_for_kernel_success()                      │
│  ├── wait_for_jupyterlite_ready()                   │
│  ├── wait_for_notebook_ready()                      │
│  ├── execute_all_cells() → 轮询执行状态              │
│  └── check_for_errors() → stderr检测+警告过滤        │
└─────────────────────────────────────────────────────┘
```

## 测试配置（pyproject.toml）

```toml
[tool.pytest.ini_options]
testpaths = ["ui-tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short --html=ui-tests/report.html --self-contained-html"
```

| 配置项 | 值 | 说明 |
|--------|---|------|
| `testpaths` | `["ui-tests"]` | 测试目录 |
| `python_files` | `["test_*.py"]` | 测试文件匹配模式 |
| `python_functions` | `["test_*"]` | 测试函数匹配模式 |
| `addopts` | `-v --tb=short --html=ui-tests/report.html --self-contained-html` | 默认参数 |

测试依赖4个包：

| 包 | 用途 |
|----|------|
| `playwright≥1.61.0` | 浏览器自动化引擎 |
| `pytest-playwright≥0.8.0` | Playwright的pytest插件 |
| `pytest-html≥4.2.0` | 生成HTML测试报告 |
| `pytest-rerunfailures≥15.1` | 失败自动重试 |

## Fixtures 详解（conftest.py）

### find_free_port() — 端口查找

```python
def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port
```

创建TCP socket绑定到端口0（让操作系统分配空闲端口），获取实际端口号后关闭socket。确保每次测试运行使用不同端口，避免端口冲突。

### dist_dir — 构建产物验证

```python
@pytest.fixture(scope="session")
def dist_dir() -> Path:
    dist_path = Path(__file__).parent.parent / "dist"
    if not dist_path.exists():
        pytest.fail("Distribution directory not found... Please run 'pixi run build' first.")
    return dist_path
```

session级fixture，验证dist/目录存在。如果未构建，直接pytest.fail并给出明确的构建提示。

### http_server — 自动HTTP服务器

```python
@pytest.fixture(scope="session", autouse=True)
def http_server(dist_dir: Path, server_port: int):
    process = subprocess.Popen(
        ["python", "-m", "http.server", str(server_port), "--directory", str(dist_dir)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    if process.poll() is not None:
        pytest.fail(f"Failed to start HTTP server on port {server_port}")
    yield process
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
```

关键设计：
- **autouse=True**：自动启动，无需在测试函数中显式声明
- **scope=session**：整个测试会话共享一个服务器实例
- 使用 `python -m http.server` 内置服务器，零额外依赖
- stdout/stderr重定向到DEVNULL，避免日志污染
- teardown阶段先terminate（优雅关闭），5秒超时后kill（强制终止）

### browser_context_args — 失败视频录制

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    videos_dir = Path(__file__).parent / "videos"
    videos_dir.mkdir(exist_ok=True)
    return {
        **browser_context_args,
        "record_video_dir": str(videos_dir),
        "record_video_size": {"width": 1280, "height": 720},
    }
```

覆盖pytest-playwright的默认browser_context_args，启用视频录制：
- 视频保存到 `ui-tests/videos/` 目录
- 分辨率 1280x720（720p）
- 失败时视频作为artifact上传，便于调试

## Notebook参数化测试（test_notebooks.py）

### 自动发现Notebook

```python
CONTENT_DIR = Path(__file__).parent.parent / "content" / "notebooks"
NOTEBOOKS = sorted(CONTENT_DIR.glob("*.ipynb"))
TIMEOUT = 300_000  # 5分钟

if not NOTEBOOKS:
    pytest.fail(f"No notebooks found in {CONTENT_DIR}")
```

- 自动扫描 `content/notebooks/*.ipynb`
- 按文件名排序确保测试顺序一致
- 如果没有发现notebook直接失败（防止路径错误导致零测试）

### 参数化与失败重试

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1, only_rerun=["TimeoutError"])
@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda p: p.stem)
def test_notebook_execution(page: Page, base_url: str, notebook_path: Path) -> None:
```

- `@pytest.mark.parametrize`：为每个.ipynb文件生成独立测试用例，测试ID使用文件名（不含扩展名）
- `@pytest.mark.flaky`：仅对TimeoutError重试2次，每次间隔1秒
- 浏览器WASM加载可能不稳定，超时重试能减少CI假阴性

### 测试流程

```python
# 1. 构造URL
relative_path = notebook_path.relative_to(notebook_path.parent.parent)
notebook_url = f"{base_url}/lab/index.html?path={quote(str(relative_path))}"

# 2. 导航到notebook
page.goto(notebook_url, wait_until="networkidle", timeout=60000)

# 3. 等待就绪
wait_for_jupyterlite_ready(page, timeout=60000)
wait_for_notebook_ready(page, timeout=60000)

# 4. 执行所有cell
execute_all_cells(page, notebook_name=notebook_path.name, timeout=TIMEOUT)

# 5. 检查错误
errors = check_for_errors(page, notebook_name=notebook_path.name)

# 6. 失败时截图
if errors:
    screenshot_path = Path(__file__).parent / f"screenshot_{notebook_path.stem}.png"
    page.screenshot(path=str(screenshot_path))

# 7. 断言无错误
assert not errors
```

URL构造使用 `urllib.parse.quote` 对路径进行URL编码，确保含特殊字符的文件名能正确处理。

## 工具函数详解（utils.py）

### KNOWN_WARNINGS_BY_NOTEBOOK — 已知警告白名单

```python
KNOWN_WARNINGS_BY_NOTEBOOK = {
    "Lorenz.ipynb": ["Matplotlib is building the font cache; this may take a moment."],
    "Intro.ipynb": ["Matplotlib is building the font cache; this may take a moment."],
    "r.ipynb": ["Attaching package:"],
    "cpp.ipynb": ["some error"],
    "cpp-tiny-ray-tracer.ipynb": [],
    "cpp-third-party-libs.ipynb": [],
    "sqlite.ipynb": ["Error: no such table: players"],
}
```

每个notebook可能产生预期的stderr输出（如Matplotlib字体缓存、R包加载消息、SQLite预期错误等），这些不作为测试失败依据。

### wait_for_kernel_success — 内核就绪等待

```python
def wait_for_kernel_success(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector(".jp-KernelStatus-success", timeout=timeout, state="attached")
```

等待JupyterLab内核状态指示器显示为成功状态（`.jp-KernelStatus-success` CSS类）。

### wait_for_jupyterlite_ready — JupyterLite就绪

```python
def wait_for_jupyterlite_ready(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector("#jp-main-dock-panel", timeout=timeout)
    wait_for_kernel_success(page, timeout)
```

两步等待：
1. 主面板（`#jp-main-dock-panel`）DOM元素出现
2. 内核状态变为成功

### wait_for_notebook_ready — Notebook加载完成

```python
def wait_for_notebook_ready(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector(".jp-Cell", timeout=timeout)
    wait_for_kernel_success(page, timeout)
```

等待第一个cell（`.jp-Cell`）出现，且内核就绪。

### execute_all_cells — 执行所有Cell（核心函数）

这是最复杂的函数，通过轮询机制监控cell执行状态：

```python
def execute_all_cells(page: Page, notebook_name=None, timeout=300000) -> None:
    # 1. 点击菜单：Run → Run All Cells
    page.click('text="Run"')
    page.click('text="Run All Cells"')
    page.wait_for_timeout(1000)

    start_time = page.evaluate("Date.now()")
    while True:
        # 2. 处理输入提示（如果notebook需要stdin输入）
        input_prompt = page.locator(".jp-Stdin-input")
        if input_prompt.count() > 0:
            page.keyboard.type("test_input")
            page.keyboard.press("Enter")
            page.wait_for_timeout(500)

        # 3. 检查错误
        errors = check_for_errors(page, notebook_name=notebook_name)
        if errors:
            try:
                wait_for_kernel_success(page, timeout=500)
                break  # 内核仍在运行但有错误，停止执行
            except:
                pass

        # 4. 检查最后一个code cell的执行计数
        code_cells = page.locator(".jp-CodeCell")
        if code_cells.count() > 0:
            last_cell = code_cells.last
            last_prompt = last_cell.locator(".jp-InputArea-prompt")
            prompt_text = last_prompt.inner_text().strip()
            # 执行完成条件：有编号（如"[1]:"），不是"[ ]:"（未执行），不含"*"（执行中）
            if prompt_text and prompt_text != "[ ]:" and "*" not in prompt_text:
                try:
                    wait_for_kernel_success(page, timeout=0)
                    break
                except:
                    pass

        # 5. 超时检查
        elapsed = page.evaluate("Date.now()") - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Notebook execution timed out after {timeout}ms")

        page.wait_for_timeout(500)
```

**关键设计点**：

1. **菜单操作**：通过点击JupyterLab的菜单栏（Run → Run All Cells）触发执行，模拟真实用户操作
2. **Stdin处理**：如果notebook中有 `input()` 调用，自动输入"test_input"并按回车
3. **执行状态判断**：通过检查最后一个code cell的prompt文本来判断执行是否完成
   - `"[ ]:"` → 未执行
   - `"[*]:"` → 正在执行
   - `"[1]:"` 等有编号的 → 执行完成
4. **内核健康检查**：每次循环都确认内核仍在运行
5. **500ms轮询**：平衡响应速度和CPU占用
6. **5分钟超时**：WASM环境中复杂计算（如光线追踪）需要较长时间

### check_for_errors — 错误检测

```python
def check_for_errors(page: Page, notebook_name=None, known_warnings=None) -> list[str]:
    if known_warnings is None:
        known_warnings = KNOWN_WARNINGS_BY_NOTEBOOK.get(notebook_name, [])

    errors = []
    stderr_outputs = page.locator(
        ".jp-OutputArea-output[data-mime-type='application/vnd.jupyter.stderr']"
    )
    for i in range(stderr_outputs.count()):
        stderr_text = stderr_outputs.nth(i).inner_text().strip()
        if not stderr_text:
            continue
        is_known_warning = any(warning in stderr_text for warning in known_warnings)
        if not is_known_warning:
            errors.append(stderr_text)
    return errors
```

**错误检测逻辑**：
1. 定位所有stderr输出区域（使用JupyterLab的CSS选择器）
2. 提取每个stderr区域的文本内容
3. 过滤掉匹配已知警告的输出（子字符串匹配）
4. 返回未被过滤的错误列表

## 运行测试

### 本地运行

```bash
# 首次需要安装Playwright浏览器
pixi run playwright install --with-deps chromium

# 构建站点（测试需要dist/目录）
pixi run build && pixi run filter-kernels

# 运行测试
pixi run test
```

### CI运行

在GitHub Actions中（test job）：
1. 从build job下载dist artifact
2. 安装Playwright浏览器（`pixi run playwright install --with-deps chromium`）
3. 运行 `pixi run test`
4. 失败时上传截图（`ui-tests/screenshot_*.png`）和视频（`ui-tests/videos/`）
5. 总是上传HTML报告（`ui-tests/report.html`）

### 测试产物

| 产物 | 路径 | 上传条件 |
|------|------|---------|
| HTML报告 | `ui-tests/report.html` | 总是上传（if: always()） |
| 失败截图 | `ui-tests/screenshot_*.png` | 失败时上传（if: failure()） |
| 执行视频 | `ui-tests/videos/` | 失败时上传（if: failure()） |

## 测试超时设置

| 操作 | 超时时间 | 说明 |
|------|---------|------|
| 页面导航 | 60秒 | `page.goto(wait_until="networkidle")` |
| JupyterLite就绪 | 60秒 | 主面板+内核启动 |
| Notebook就绪 | 60秒 | Cell加载+内核就绪 |
| Cell执行 | 300秒（5分钟） | 完整notebook执行 |

## 相关概念

- [构建管线](05-build-pipeline.md)
- [部署](08-deployment.md)
- [Notebook内容与数据](06-notebooks-and-content.md)

---
type: Reference
title: "UI测试框架源码"
description: "ui-tests/ 目录下 Playwright E2E测试框架完整解析：conftest.py fixtures、test_notebooks.py 参数化测试、utils.py 工具函数"
tags: [playwright, pytest, e2e-testing, ui-tests, notebook-execution, browser-automation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: conftest-py
    resource: "../../../../../external/libs/jupyter/try-jupyter/ui-tests/conftest.py"
    title: "try-jupyter/ui-tests/conftest.py"
  - id: test-notebooks-py
    resource: "../../../../../external/libs/jupyter/try-jupyter/ui-tests/test_notebooks.py"
    title: "try-jupyter/ui-tests/test_notebooks.py"
  - id: utils-py
    resource: "../../../../../external/libs/jupyter/try-jupyter/ui-tests/utils.py"
    title: "try-jupyter/ui-tests/utils.py"
---

# UI测试框架源码

本信源登记 `ui-tests/` 目录下3个Python文件的完整API与测试逻辑。

## 1. ui-tests/conftest.py — Pytest配置与Fixtures

### 函数：`find_free_port() -> int`

查找localhost可用端口：
1. 创建 `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`
2. `s.bind(("", 0))` 绑定到随机端口
3. `s.listen(1)` 开始监听
4. 通过 `s.getsockname()[1]` 获取分配的端口号
5. 返回端口号（整数）

### Fixture：`dist_dir() -> Path`（scope="session"）

返回JupyterLite构建产物目录路径：
- 路径为 `Path(__file__).parent.parent / "dist"`（即项目根目录/dist）
- 如果dist目录不存在，调用 `pytest.fail()` 并提示先运行 `pixi run build`

### Fixture：`server_port() -> int`（scope="session"）

返回 `find_free_port()` 获取的空闲端口号。

### Fixture：`http_server(dist_dir, server_port)`（scope="session", autouse=True）

自动启动HTTP服务器：
1. 使用 `subprocess.Popen` 启动命令：`python -m http.server {port} --directory {dist_dir}`
2. stdout和stderr均重定向到 `subprocess.DEVNULL`
3. 等待1秒让服务器启动
4. 如果进程已退出（`process.poll() is not None`），pytest.fail
5. yield 返回process对象
6. teardown：`process.terminate()` → 等待5秒 → 超时则 `process.kill()`

### Fixture：`base_url(server_port) -> str`（scope="session"）

返回基础URL：`f"http://localhost:{server_port}"`

### Fixture：`browser_context_args(browser_context_args)`（scope="session"）

配置浏览器上下文：
- 创建 `ui-tests/videos` 目录（录制失败时的视频）
- 返回合并后的配置：`record_video_dir` 设为videos目录，`record_video_size` 设为 1280x720

## 2. ui-tests/test_notebooks.py — Notebook执行测试

### 模块常量

| 常量 | 值 | 说明 |
|------|---|------|
| `CONTENT_DIR` | `Path(__file__).parent.parent / "content" / "notebooks"` | Notebook目录 |
| `NOTEBOOKS` | `sorted(CONTENT_DIR.glob("*.ipynb"))` | 自动发现的所有notebook文件列表 |
| `TIMEOUT` | `300_000` | 单notebook执行超时（5分钟，毫秒） |

如果NOTEBOOKS为空列表，直接调用 `pytest.fail()` 。

### 测试函数：`test_notebook_execution(page, base_url, notebook_path)`

装饰器：`@pytest.mark.flaky(reruns=2, reruns_delay=1, only_rerun=["TimeoutError"])`
- 对TimeoutError自动重试2次，每次延迟1秒
- 使用 `@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda p: p.stem)` 参数化

测试流程：
1. 计算相对路径：`notebook_path.relative_to(notebook_path.parent.parent)`
2. 构建URL：`f"{base_url}/lab/index.html?path={quote(str(relative_path))}"`
3. `page.goto(notebook_url, wait_until="networkidle", timeout=60000)` 导航到notebook
4. `wait_for_jupyterlite_ready(page, timeout=60000)` 等待JupyterLite加载完成
5. `wait_for_notebook_ready(page, timeout=60000)` 等待Notebook加载完成
6. `execute_all_cells(page, notebook_name=notebook_path.name, timeout=TIMEOUT)` 执行所有cell
7. `check_for_errors(page, notebook_name=notebook_path.name)` 检查错误
8. 如果有错误：截图保存到 `ui-tests/screenshot_{stem}.png`
9. 断言无错误：`assert not errors`

## 3. ui-tests/utils.py — 测试工具函数

### 常量：`KNOWN_WARNINGS_BY_NOTEBOOK`

按notebook名称映射可忽略的已知警告列表：

| Notebook | 已知警告（可忽略） |
|----------|-----------------|
| `Lorenz.ipynb` | `["Matplotlib is building the font cache; this may take a moment."]` |
| `Intro.ipynb` | `["Matplotlib is building the font cache; this may take a moment."]` |
| `r.ipynb` | `["Attaching package:"]` |
| `cpp.ipynb` | `["some error"]` |
| `cpp-tiny-ray-tracer.ipynb` | `[]`（无已知警告） |
| `cpp-third-party-libs.ipynb` | `[]`（无已知警告） |
| `sqlite.ipynb` | `["Error: no such table: players"]` |

### 函数：`wait_for_kernel_success(page: Page, timeout: int = 30000) -> None`

等待内核状态变为成功：
- `page.wait_for_selector(".jp-KernelStatus-success", timeout=timeout, state="attached")`

### 函数：`wait_for_jupyterlite_ready(page: Page, timeout: int = 30000) -> None`

等待JupyterLite完全就绪：
1. `page.wait_for_selector("#jp-main-dock-panel", timeout=timeout)` 等待主面板出现
2. `wait_for_kernel_success(page, timeout)` 等待内核就绪

### 函数：`wait_for_notebook_ready(page: Page, timeout: int = 30000) -> None`

等待Notebook加载完成：
1. `page.wait_for_selector(".jp-Cell", timeout=timeout)` 等待cell出现
2. `wait_for_kernel_success(page, timeout)` 等待内核就绪

### 函数：`execute_all_cells(page: Page, notebook_name: str | None = None, timeout: int = 300000) -> None`

执行Notebook中所有cell：
1. 点击菜单：`page.click('text="Run"')` → `page.click('text="Run All Cells"')`
2. 等待1秒
3. 进入轮询循环（每500ms检查一次）：
   - 检查是否有输入提示（`.jp-Stdin-input`）：有则输入"test_input"并按Enter
   - 检查错误（调用check_for_errors），如有错误则等待内核成功后break
   - 检查最后一个code cell的执行计数：通过 `.jp-CodeCell` 定位最后一个cell，读取 `.jp-InputArea-prompt` 文本
   - 判断执行完成条件：prompt_text非空、不是"[ ]:"、不含"*"号，且内核状态成功
   - 超时判断：elapsed > timeout 抛出 TimeoutError

### 函数：`check_for_errors(page: Page, notebook_name: str | None = None, known_warnings: list[str] | None = None) -> list[str]`

检查cell执行错误：
1. 确定known_warnings：显式传入 > 按notebook_name查表 > 空列表
2. 定位所有stderr输出：`.jp-OutputArea-output[data-mime-type='application/vnd.jupyter.stderr']`
3. 遍历每个stderr元素，提取inner_text
4. 跳过空文本
5. 检查是否匹配已知警告（`any(warning in stderr_text for warning in known_warnings)`）
6. 返回非已知警告的错误文本列表

## 测试执行命令

```bash
pixi run playwright install --with-deps chromium  # 安装浏览器
pixi run test                                      # 运行测试
```

测试报告生成到 `ui-tests/report.html`，失败截图保存到 `ui-tests/screenshot_*.png`，失败视频保存到 `ui-tests/videos/`。

## 相关信源

- [pyproject.toml 信源](pyproject-source.md)（pytest配置）
- [CI/CD工作流信源](ci-source.md)（test job步骤）

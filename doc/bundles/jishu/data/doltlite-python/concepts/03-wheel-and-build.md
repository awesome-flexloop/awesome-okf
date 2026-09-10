---
type: Concept
title: wheel tag 与构建系统
description: "doltlite-python 的 py3-none wheel tag 策略、cibuildwheel 配置、lockstep 版本管理与 CI 流程；F-004~F-007。"
tags: [doltlite-python, wheel, cibuildwheel, build-system]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: doltlite-python-local
    resource: "本地克隆（tag v0.50.7，commit ba3b46fa6f58e42aef4b929d97a28248832079cb）"
    title: doltlite-python 源码逐文件精读
---

# wheel tag 与构建系统

> **对应 F 编号**：F-004 ~ F-007

## 为何使用 py3-none tag

常规含 C 扩展的 Python 包需要 `cpXY-cpXY-platform` tag（每个 CPython 版本独立 wheel），因为 C 扩展编译结果与 CPython ABI 绑定。但 doltlite-python 不同：

- Python 代码极少（_loader.py 206行，纯 Python）
- 二进制依赖 libdoltlite 是**纯 native library**，不绑定任何 CPython ABI
- 只需匹配 OS + arch，与 CPython 版本无关

因此通过自定义 `PlatformWheel.get_tag()` 强制返回 `("py3", "none", plat)`（F-005）：

```python
# setup.py L17-L25
class PlatformWheel(bdist_wheel.bdist_wheel):
    def get_tag(self):
        return ("py3", "none", self.plat_name)
```

用户 `pip install doltlite` 后获得的是与 Python 版本无关的 wheel，只需匹配 OS 和架构。

## cibuildwheel 配置

pyproject.toml 中的 cibuildwheel 配置（F-006）：

```toml
[tool.cibuildwheel]
build = "cp39-* cp310-* cp311-* cp312-* cp313-*"
skip = "*-musllinux_* *-win_* *-manylinux_i686"
# 排除 Intel Mac（macos-13），只构建 Apple Silicon
```

构建平台覆盖：
- macOS arm64（Apple Silicon）+ x86_64（通过 GitHub Actions 的 macOS-latest）
- Linux x86_64 + aarch64（通过 manylinux 镜像）
- **不构建**：Windows、musllinux（Alpine）、i686（32位）

## libdoltlite 编译与 lockstep 版本管理

before-build 脚本在构建 wheel 前编译上游 doltlite 库（F-007）：

```bash
# scripts/build-libdoltlite.sh
DOLTLITE_REF="${DOLTLITE_REF:-v0.50.7}"
git clone --depth 1 --branch "$DOLTLITE_REF" https://github.com/dolthub/doltlite.git
cd doltlite
make libdoltlite  # 编译出 libdoltlite.{dylib,so}
```

**lockstep 版本管理**是 doltlite-python 的设计约束：pyproject.toml 的版本号和 `DOLTLITE_REF` 必须同步递增。若仅有 loader 修复而 libdoltlite 版本不变，使用 post-release（如 `0.50.7.post1`）绕过重新编译（F-007、洞察 5）。

```toml
# pyproject.toml L7-L9
[project]
version = "0.50.7"
# 注释说明：
# Tracks the bundled libdoltlite release.
# Bump in lockstep with DOLTLITE_REF in scripts/build-libdoltlite.sh.
# Loader-only fixes between libdoltlite releases use post-releases.
```

## CI 流程

GitHub Actions workflow（wheels.yml）（F-006）：

```
PR / Push to main
    └── GitHub Actions
        ├── macOS arm64 (GitHub Actions runner)
        │   ├── before-build: 编译 libdoltlite
        │   ├── cibuildwheel: 构建 py3-none 轮
        │   └── smoke 测试（Homebrew Python 独立环境验证）
        ├── Linux x86_64 (manylinux 镜像)
        │   └── cibuildwheel + smoke 测试
        └── Linux aarch64 (manylinux 镜像)
            └── cibuildwheel + smoke 测试
```

smoke 测试（F-021、F-022）：

```python
# tests/smoke.py
conn = sqlite3.connect(":memory:")
assert conn.execute("SELECT dolt_version()").fetchone()[0].startswith("v")
conn.execute("CREATE TABLE t(x INT)")
conn.execute("INSERT INTO t VALUES (1), (2), (3)")
conn.execute("DOLT_COMMIT('-A', '-m', 'smoke')")
rows = conn.execute("SELECT message FROM dolt_log()").fetchall()
assert any(r[0] == "smoke" for r in rows)
print(doltlite.libdoltlite_path())
```

## 学习路径

* [bootstrap() 加载机制](01-bootstrap-mechanism.md) — loader 的幂等性设计与环境标记
* [跨平台符号劫持策略](02-platform-strategies.md) — Linux vs macOS 的具体实现

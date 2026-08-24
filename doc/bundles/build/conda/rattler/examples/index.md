# 示例目录

本目录包含 Rattler 的实用代码示例，按使用场景分类。

## 入门示例

| 示例 | 难度 | 说明 |
|------|------|------|
| [基础求解与安装](basic-solve-install.md) | ⭐⭐ | 完整流程：虚拟包检测→repodata加载→依赖求解→包安装（Rust + Python） |

## 功能示例

| 示例 | 难度 | 说明 |
|------|------|------|
| [虚拟包检测](virtual-package-detection.md) | ⭐ | 系统能力检测、环境变量覆盖、交叉编译自定义虚拟包 |
| [Repodata 获取与缓存](repodata-fetch-cache.md) | ⭐⭐ | Gateway 高级 API、缓存管理、进度报告 |

## 前置条件

运行 Rust 示例需要：
- Rust 工具链（stable）
- C 编译器（libsolv 后端）
- 网络连接（首次运行需要下载 repodata 和包）
- `dirs` crate（获取缓存目录）

运行 Python 示例需要：
- Python 3.8+
- `py-rattler` 包（`pip install py-rattler` 或 `conda install -c conda-forge py-rattler`）

```{toctree}
:hidden:

basic-solve-install
repodata-fetch-cache
virtual-package-detection
```

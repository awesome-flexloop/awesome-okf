# Examples - olot 使用示例

本目录包含 olot 的可运行示例，每个示例都对应实际使用场景，可以直接复制修改后使用。

## 示例列表

| 序号 | 文件 | 场景 | 对应概念 |
|------|------|------|---------|
| 01 | [01-cli-usage.md](/bundles/containers/olot/examples/01-cli-usage.md) | CLI 命令行打包 ModelCar 完整流程 | [00-introduction](/bundles/containers/olot/concepts/00-introduction.md), [02-backends](/bundles/containers/olot/concepts/02-backends.md) |
| 02 | [02-python-api.md](/bundles/containers/olot/examples/02-python-api.md) | Python API 编程与自动化打包 | [03-python-api](/bundles/containers/olot/concepts/03-python-api.md), [02-backends](/bundles/containers/olot/concepts/02-backends.md) |

## 示例选择指南

- **快速体验/命令行使用**：从 [01-cli-usage.md](/bundles/containers/olot/examples/01-cli-usage.md) 开始
- **CI/CD 集成/代码中调用**：阅读 [02-python-api.md](/bundles/containers/olot/examples/02-python-api.md)
- **纯 Python 无外部依赖环境**：参考示例 2 中的 oras-py 后端
- **批量自动化处理**：参考示例 3 的自动后端检测模式

## 运行示例前准备

```bash
# 安装 olot
pip install olot

# 如果要使用纯 Python 后端
pip install olot[oras-py]

# 安装 skopeo（可选，用于示例 1）
# 参考你的操作系统包管理方式
```

# Concepts - olot 核心概念

本目录包含 olot 项目的核心概念文档，按照学习路径从入门到进阶排列。

## 概念文档列表

| 序号 | 文件 | 主题 | 难度 | 前置知识 |
|------|------|------|------|---------|
| 00 | [00-introduction.md](/bundles/containers/olot/concepts/00-introduction.md) | olot 定位与 ModelCar 标准 | ⭐ 入门 | 无 |
| 01 | [01-oci-layers.md](/bundles/containers/olot/concepts/01-oci-layers.md) | OCI 层操作与四元组注解 | ⭐⭐ 中级 | OCI 基本概念 |
| 02 | [02-backends.md](/bundles/containers/olot/concepts/02-backends.md) | 后端抽象层（skopeo/oras） | ⭐⭐ 中级 | 容器 registry 概念 |
| 03 | [03-python-api.md](/bundles/containers/olot/concepts/03-python-api.md) | Python API 编程 | ⭐⭐⭐ 进阶 | Python 编程基础 |

## 建议学习路径

1. **快速上手**：阅读 00-introduction → 直接看 examples/ 中的 CLI 示例
2. **理解原理**：00 → 01 → examples/01-cli-usage
3. **代码集成**：00 → 01 → 02 → 03 → examples/02-python-api
4. **深度使用**：全部阅读 + 阅读 references/ 中的源码信源

## 前置知识

阅读这些概念文档不需要深入的 OCI 知识，但了解以下概念会有帮助：
- 容器镜像基本概念（层、manifest、registry）
- 基本的命令行操作
- Python 基础（如果使用 Python API）

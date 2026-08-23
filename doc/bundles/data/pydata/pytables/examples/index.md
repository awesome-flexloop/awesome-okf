# 示例索引（Examples）

本目录提供 PyTables 的可运行代码示例，每个示例均为独立的 Markdown 教程，包含完整可执行的 Python 代码。

## 示例列表

| 文档 | 难度 | 覆盖内容 |
|------|------|---------|
| [hdf5-basics.md](hdf5-basics.md) | 入门 | 文件创建、Group/Array/CArray/EArray/VLArray/Table 创建、数据写入/读取/追加、where 条件查询、索引创建、压缩配置、pandas 转换、异常处理 |

## 运行示例

示例代码可直接复制到 Python 交互式环境或脚本中运行。要求：

- Python 3.8+
- PyTables 3.x（`pip install tables`）
- NumPy
- pandas（可选，用于 DataFrame 转换部分）

```bash
pip install tables numpy pandas
```

## 前置知识

阅读示例前建议先了解：
- [概念文档](../concepts/) 中的核心概念（00→01→02→03 顺序）
- [参考文档](../references/) 中的 API 细节

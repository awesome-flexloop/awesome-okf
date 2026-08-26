# 概念索引（Concepts）

本目录按学习顺序组织 PyTables 的核心概念文档。建议按编号顺序阅读。

## 概念列表

| 编号 | 文档 | 核心主题 | 前置概念 |
|------|------|---------|---------|
| 00 | [00-introduction.md](00-introduction.md) | PyTables 简介：定位、特性、架构概览 | 无 |
| 01 | [01-node-hierarchy.md](01-node-hierarchy.md) | 节点层次体系：Node/Group/Leaf 继承关系、路径系统、链接 | 00 |
| 02 | [02-table-atom.md](02-table-atom.md) | Table 与 Atom：结构化表、列访问、类型描述符、行操作、条件查询 | 01 |
| 03 | [03-compression-indexing.md](03-compression-indexing.md) | 压缩与索引：Filters 管道、Blosc2、CSI 索引、查询优化 | 02 |

## 概念依赖图

```
00-introduction
    │
    ▼
01-node-hierarchy ── Node / Group / Leaf / Array / Table / Link
    │
    ▼
02-table-atom ── Table / Cols / Column / Row / Atom / Col
    │
    ▼
03-compression-indexing ── Filters / Blosc2 / Index / CSI
```

## 学习建议

1. **初学者**：按 00→01→02→03 顺序通读，配合 [examples/](../examples/) 中的代码示例动手实践
2. **性能调优**：重点阅读 03，理解压缩级别选择、索引类型选择和查询优化技巧
3. **API 速查**：跳转到 [references/](../references/) 查看具体的类和方法签名

```{toctree}
:maxdepth: 7

00-introduction
01-node-hierarchy
02-table-atom
03-compression-indexing
```

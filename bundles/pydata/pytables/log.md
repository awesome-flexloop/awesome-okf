# PyTables Bundle 变更日志

## 2026-08-22 — 初始版本

- 基于 PyTables 源码（`external/libs/python/PyTables/tables/` 目录）核心模块深度阅读生成
- 覆盖 4 个概念文档 + 1 个示例文档 + 1 个信源登记文档
- 核心子系统覆盖：节点层次体系(Node/Group/Leaf/Table)、Atom类型系统、压缩与索引(Filters/CSI)、Blosc2动态加载
- Cython扩展模块：hdf5extension/tableextension/indexesextension等

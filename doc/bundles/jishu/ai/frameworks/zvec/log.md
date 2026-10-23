# 变更日志

## 2026-10-22

### 新增

- 新建 zvec 束（10 概念 + 3 示例 + 2 信源 + R/I 阶段产物），落位 `jishu/ai/frameworks/`。
- 概念：总览 / 源码架构 / 数据模型 / 索引类型 / 量化 / FTS 与过滤 / 混合检索 / Embedding 与 Reranker / 存储与配置 / Agent 集成。
- 示例：Python 快速上手 / 混合检索实战 / zvec-grep CLI 实战。
- 信源登记：源码（alibaba/zvec @ commit 8d49969，v0.8.0-4，镜像 `external/dao/alibaba/zvec`）与官方文档站（zvec.org 2026-10-22 快照）。
- spec/facts.md：73 条编号事实（F-001～F-110，按主题跳号分组；V 阶段计数复核勘误：初稿误记 60 条，实际 rg 计数 73 条），数量类事实经脚本计数（thirdparty 17、DataType 23、IndexType 10、QuantizeType 8、MetricType 3、IOBackendType 4、StatusCode 11、Collection 公共成员 24、python 测试 42、extension 模块 16、C 示例 7、C++ 示例 5、src 模块 6）。
- spec/insights.md：5 条洞察四元组（库即数据库 / 量化双轨 / FTS 一等公民但单 Query 互斥 / Agent 三件套分层 / 运维特性下放嵌入式）。

### 事实来源

- 源码：`external/dao/alibaba/zvec`（磁盘回读 + rg/grep 脚本计数）。
- 文档：zvec.org 中文站逐页抓取（首页、docs 总览、db 文档树 20+ 页、zvec-grep 文档树 8 页）。
- 已知差异：文档 DataType 列 21 个（缺 VECTOR_FP64/VECTOR_UINT8），以源码 23 个为准；文档向量索引页列 6 种，源码另有 Vamana 与 flat_sparse/hnsw_sparse 稀疏索引目录。

# 更新日志

## 2026-09-02

**Merge**: 从 SpecWeave learning 合并独有内容（03 分类迁移）

新增 1 篇参考文档（LangGraph 生产级落地实施路线图：12-16 周四阶段、Demo-Prod 六层能力模型对齐）。


## 2026-08-23

- 初始版本，基于 langgraph 源码生成 OKF v0.2 bundle
- R 阶段：阅读 graph/state.py、graph/message.py、channels 全部核心文件、pregel/main.py+_loop.py+_algo.py+_executor.py+_read.py+_write.py、_internal/_runnable.py+_config.py+_constants.py、config.py、types.py、errors.py、runtime.py、constants.py，以及 checkpoint/base/__init__.py+id.py、serde/base.py+jsonplus.py、store/base/__init__.py+batch.py，提取 128 条编号事实
- I 阶段：提炼 6 个架构洞察（Channel/Actor 模型、BSP 超步循环、版本向量检查点、统一控制流、interrupt/resume 协议、三层错误处理）
- E 阶段：生成 3 篇 references、8 篇 concepts、2 篇 examples，以及 index.md 和 log.md

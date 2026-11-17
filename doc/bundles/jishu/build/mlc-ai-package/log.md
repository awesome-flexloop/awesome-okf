# 更新日志

## 2026-11-13

**Initial**: 知识包首次入库（`jishu/build/mlc-ai-package/`）

- 源码基线：`external/dev/libs/mlc-ai/package`（`README.md` 声明的四个发行物；`version.py` 记录 LLVM 23.1.1 / Z3 5.3.1 / Doxygen 1.18.0）
- R 阶段：新增 `spec/facts.md`，F-001 ~ F-162 共 162 条编号事实，覆盖仓库结构、标准包布局、版本单一源、scikit-build/CMake 流水线、上游钉扎、LLVM 构建配方、SDK 分片、打包后处理、运行期前端、Z3/Doxygen 姊妹包、nightly 流水线、CI 缓存与验证体系、许可与依赖策略
- I 阶段：新增 `spec/insights.md`，八条洞察（契约载体视角 / 一次构建两分片 / profile 是安装态的函数 / 可重定位性需构造并校验 / 体积预算是发布门禁 / 缓存键由配方源码决定 / 验证对象是真实链接 / nightly 与 stable 共享路径）与知识地图
- 新增 15 个概念文档：`00-introduction` ~ `14-verification-strategy`
- 新增 3 个实战示例：消费 LLVM SDK、从源码构建 LLVM SDK、消费 Z3 与 Doxygen
- 新增 3 个信源参考：源码与模块索引、环境变量与输入参数、依赖审计要点
- 更新 `jishu/build/index.md` 域内导航，登记本锚点组（构建系统与包管理生态 → MLC AI 原生工具链 wheel 打包）
- 更新总索引 `doc/bundles/index.md` 计数：734 → 735 束（分组数不变，仍为 64 组 / 9 域），同步 `doc/index.md` 与 `README.md` 的规模数字
- 交叉引用：与 [`scikit-build`](../scikit-build/index.md)（同用 scikit-build-core 构建后端）、[`jishu/ml/tvm-tirx`](../../ml/tvm-tirx/index.md)（LLVM 的下游消费者）建立互链

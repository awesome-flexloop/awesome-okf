# 变更日志

## 2026-08-23

### 新增

- 初始创建 FastAPI v0.141.1 OKF 知识束
- 完成 R 阶段：158 条源码事实（F-001~F-158），覆盖 29 个核心模块
- 完成 I 阶段：7 个架构洞察四元组（双层 AsyncExitStack、Param 继承 FieldInfo、Dependant 递归树、APIRouter 组合语义、OpenAPI 版本缓存、流式自动检测、Pydantic v2 兼容层）
- 完成 E 阶段：27 个内容文档
  - 14 个概念文档（concepts/00-13）
  - 5 个实战示例（examples/01-05）
  - 8 个信源登记（references/）
- 方法论：source-code-to-okf-wiki Skill，R→I→E→V→C 五阶段链路
- 完成 V 阶段：黑盒验证通过
  - 41 个公开 API 经源码 Grep 验证全部真实存在，零虚构
  - 60 个 bundle-relative 交叉链接全部有效，无死链
  - 27 个内容文档 frontmatter 合规，type 字段非空
  - 修复 1 处拼写错误（Dantanant→Dependant）和 7 处代码块语言标注缺失

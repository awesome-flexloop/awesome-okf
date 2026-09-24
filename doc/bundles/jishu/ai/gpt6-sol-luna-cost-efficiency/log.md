# 变更日志

## 2026-09-23

- 依据微信公众号文章生成 GPT-6 Sol/Luna 选型知识包。
- 采用 R→I→E→V 知识沉淀链路。
- 以 OpenAI 与 DeepSeek 官方资料核验核心价格、模型分工和价格口径。
- benchmark、内部统计与第三方实测保留为来源分层声明，未升级为独立事实。
- 按操作可复现性两问判定不创建 `examples/`。
- 事实登记双份比对通过：`F-001` 至 `F-025` 集合一致。
- `check-utf8.py` 通过：10,622 个文件为有效 UTF-8。
- `check-toctrees.py` 通过：全部 index.md 引用有效，所有内容文档均可达。
- `check-bundles-index.py` 通过：9 域 / 59 组 / 570 束，索引五面计数一致。
- `invoke gates.*` 未能启动，原因是本机 `invocations` 包缺少发行版元数据；已直接运行同一底层检查脚本及其自检探针。

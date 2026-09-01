# OMLMD Bundle 生成日志

## 生成信息

- **生成时间**：2026-08-26
- **Bundle 版本**：0.1.6
- **OKF 版本**：0.2
- **源项目**：https://github.com/containers/omlmd

## 文件清单

### 根目录
- `index.md` — Bundle 首页
- `log.md` — 本日志文件

### concepts/（核心概念）
- `00-introduction.md` — OMLMD 介绍与定位
- `01-model-metadata.md` — ModelMetadata 双格式序列化
- `02-helpers-listener.md` — Helper 类与 Listener 观察者模式
- `03-registry.md` — OMLMDRegistry 扩展 oras-py
- `index.md` — 概念导航

### references/（参考资料）
- `readme-source.md` — README 原始参考
- `model-metadata-source.md` — ModelMetadata 源码参考
- `provider-source.md` — Provider 源码参考
- `index.md` — 参考导航

### examples/（使用示例）
- `01-cli-push.md` — CLI 推送模型元数据
- `02-python-custom.md` — Python SDK 自定义扩展
- `index.md` — 示例导航

## 事实来源

基于源码分析的核心文件：
- `omlmd/constants.py` — 媒体类型与文件名常量
- `omlmd/model_metadata.py` — ModelMetadata 数据类与序列化
- `omlmd/provider.py` — OMLMDRegistry 注册表扩展
- `omlmd/helpers.py` — Helper 高层 API 门面
- `omlmd/listener.py` — Listener 观察者模式
- `omlmd/cli.py` — Click/Cloup 命令行界面
- `README.md` — 项目说明文档
- `pyproject.toml` — 项目配置与依赖

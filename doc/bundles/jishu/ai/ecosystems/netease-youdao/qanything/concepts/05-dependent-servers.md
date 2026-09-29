---
type: concept
title: 依赖服务化——五个本地推理/解析进程
description: embedding/rerank/ocr/pdf_parser/insert_files 五服务的接口契约、ONNX 推理后端与设备选择，以及 entrypoint 进程编排的就绪判定、模型软链接与运维要点。
tags: [qanything, dependent-server, sanic, onnx, deployment]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: QAnything 源码事实清单（F-qa-001~060）
  - id: insights
    resource: /references/insights.md
    title: QAnything 架构洞察与知识地图
---

# 依赖服务化——五个本地推理/解析进程

主 API 服务本身不做任何模型推理：向量化、重排序、OCR、PDF 解析被拆成四个独立的 Sanic 微服务进程，外加一个负责异步入库的 insert_files 进程。主服务通过 `model_config.py` 中的 localhost URL 常量以 HTTP 调用它们（F-qa-024）：

| 常量 | 值 | 对应服务 |
|---|---|---|
| `LOCAL_EMBED_SERVICE_URL` | localhost:9001 | embedding_server |
| `LOCAL_RERANK_SERVICE_URL` | localhost:8001 | rerank_server |
| `LOCAL_OCR_SERVICE_URL` | localhost:7001 | ocr_server |
| `LOCAL_PDF_PARSER_SERVICE_URL` | localhost:9009 | pdf_parser_server |

另有两个输入长度常量约束请求尺寸：`LOCAL_RERANK_MAX_LENGTH=512`、`LOCAL_EMBED_MAX_LENGTH=512`（F-qa-024）。

## 四个推理/解析服务的接口契约

### embedding_server（9001）

Sanic 应用 `"embedding_server"`，路由 `POST /embedding`，入参 `texts`，监听 9001 端口；启动参数 `--use_gpu`、`--workers`（默认 1），推理后端为 `EmbeddingOnnxBackend(use_cpu=not args.use_gpu)`——ONNX 模型，GPU 可用时走 GPU，否则 CPU（F-qa-028）。客户端侧 `YouDaoEmbeddings` 的 model_version 为 `'local_v20240725'`，`aembed_documents` 经 aiohttp 批量提交，且 `_process_query` 会过滤页内容中的 `![figure]`、`![equation]` 行（F-qa-018）。

### rerank_server（8001）

Sanic 应用 `"rerank_server"`，路由 `POST /rerank`，入参 `query`、`passages`，后端为 `RerankOnnxBackend`（F-qa-029）。客户端 `YouDaoRerank` 的 `arerank_documents()` 按 `LOCAL_RERANK_BATCH` 分批，分数四舍五入保留 2 位小数并降序排序（F-qa-019）。

### ocr_server（7001）

Sanic 应用 `"OCRService"`，路由 `POST /ocr`，入参 `img64`（base64 编码图像）。核心类 `OCRQAnything` 组合 `TextDetector`（DBPostProcess，box_thresh=0.5）与 `TextRecognizer`（CTCLabelDecode，字典文件 ocr.res），drop_score=0.5——即 DBNet 检测 + CTC 识别的经典 OCR 管线（F-qa-030）。

### pdf_parser_server（9009）

Sanic 应用 `"pdf_parser_server"`，路由 `POST /pdfparser`，入参 `filename`、`save_dir`，后端 `PdfLoader` 按 `--use_gpu` 选择 torch device，负责把 PDF 转为 Markdown 文本供入库链路消费（F-qa-031）。

## insert_files：异步入库的队列消费者

文件入库不走同步请求——`upload_files` 接口只把文件登记进 MySQL File 表（status='gray'）即返回，真正的解析、切分、向量化由 insert_files_server 异步完成。它是 Sanic 应用 `"InsertFileService"`，启动参数 `--port`（默认 8110）、`--workers`（默认 4），后台任务 `check_and_process()` 轮询 MySQL File 表中 `status='gray'` 且 `MOD(id, INSERT_WORKERS)=worker_id` 的记录（按 worker 取模分片），置为 `yellow` 后开始处理（F-qa-032）。

`process_data()` 的关键约束（F-qa-033）：

- `split_file_to_docs` 与 milvus insert 各以 300 秒超时执行；
- `content_length > MAX_CHARS`（1000000）或等于 0 时置 status='red' 失败；
- 入库完成后经 `update_file_upload_infos` 记录 time_record（各环节耗时）；
- 成功则置 green，进入可检索状态。

这套"登记-轮询-状态机"设计把上传接口的响应时间与重解析开销解耦，但也引入了 gray→green 的时延窗口，调用方必须以状态轮询而非同步等待的方式确认入库完成（F-qa-042）。

## 进程编排与运维

`scripts/entrypoint.sh` 是全部进程的唯一编排者：依次 nohup 启动 6 个进程（4 个推理/解析服务 + insert_files + sanic_api），将 PID 写入自动生成的 `close.sh`；启动期间轮询 main_server.log 中 `"Starting worker"` 字符串，180 秒超时即报错退出（F-qa-045）。运维上有三个要点：

1. **就绪判据是日志字符串匹配而非健康探测**。日志格式变更会使就绪判定静默失效，排障时应直接核查各进程日志与端口监听。
2. **模型目录依赖软链接**。entrypoint 以 `ln -s` 为 5 处模型/数据目录创建软链接（embedding/rerank 模型配置指向 `/root/models/linux_onnx/`，ocr 模型与 pdf_to_markdown/checkpoints 指向 `/root/models/`，nltk_data 指向 `/root/nltk_data`），链接缺失即启动失败（F-qa-046）。
3. **无进程守护**。nohup + PID 文件即全部容错，进程崩溃不会自动重启；`memory_usage.sh` 可对 6 个进程统计 RSS，传参 `long` 进入每 10 秒的长期记录模式，是容量规划与内存泄漏排查的基线工具（F-qa-047）。

## 一个值得注意的不对称

`local_doc_chat` 支持传入任意 `api_base` 对接外部 LLM（F-qa-038），即 LLM 可外置；但 embedding/rerank/ocr/pdf_parser 的地址是钉死的 localhost 常量——**LLM 可外置，检索能力不可外置**。水平扩展或分布式部署时，这一 1:1 进程假设是主要障碍，需要先把 `LOCAL_*` URL 常量改为可配置的服务发现地址，并自行补齐健康检查与进程守护（F-qa-024）。

## 相关概念

- [00 QAnything 全景](/concepts/00-overview.md)
- [04 Milvus 分区多租户与三存储分层](/concepts/04-storage-multitenancy.md)
- [06 API 层、Bot 配置与知识库运维](/concepts/06-api-ops.md)
- 示例：[知识库上传与检索流程](/examples/kb-upload-and-retrieval.md)

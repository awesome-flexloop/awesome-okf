# 变更记录

## 2026-09-20

- 按 `seven-concepts-cmd` 的 R → I → E → V 链路生成本 bundle。
- 从微信公众号正文提取五个项目及其安装、许可证、成本与边界声明；未复制全文、图片或视频。
- 登记 F-001～F-032；`facts.md` 与 `references/article-source.md` 使用同一连续编号。
- 判定为技术综述加部分可复现命令，设置 `concepts/` 与 `examples/`；示例明确标注“非实测”。
- 文章星标、订阅价格和“替代”效果未全部独立复现，bundle 保持 `flagged`。
- 完成静态内容审查准备；未安装五个项目、未调用付费 API、未运行 Sphinx 或 `invoke` 门禁。
- `scripts/check-toctrees.py`、`scripts/check-utf8.py`、`scripts/check-bundles-index.py` 均通过；检查快照为 9 域 / 59 组 / 563 束、10550 个 UTF-8 文件。
- F-001～F-032 双表连续一致；新 bundle 相对链接逐文件解析通过；未发现 `file:///`、用户目录或误路径残留。
- 由于未运行 `invoke` 与 Sphinx，本日志只报告底层脚本和手动等效验证，不宣称全量构建门禁通过。

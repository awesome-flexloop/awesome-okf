# EmotiVoice 知识束变更日志

## 2026-09-09 V 验证修复

- **计数修正**（V 验证）：ARPAbet 符号计数 85 → 84（15 元音 × 4 形态 = 60 + 24 辅音），连带修正"45 个"→"60 个"错误，共 5 文件 8 处。
- **内容修正**：`examples/mixed-lingual-g2p.md` 与 `concepts/01-g2p-pipeline.md` 原称"纯英文不触发 `tn_chinese`"与"只要文本含中文才转换"，经源码核验（frontend.py 第 24 行无条件调用 `tn_chinese`）确认两处均与实现不符，已改写为"任意文本无条件先经 `tn_chinese`，数字一律转中文数字落入中文路径"。

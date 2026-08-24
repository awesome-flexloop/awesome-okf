# FlashMLA API 与技术参考

本章节提供 FlashMLA 的完整 API 参考和技术细节文档。

## 参考文档列表

| 文档 | 说明 |
|---|---|
| [api](/ai/deepseek/flash-mla/references/api) | Python 公共 API 完整参考，包括 MLA 解码、稀疏预填充、变长注意力等函数签名与参数说明 |
| [kernel-architecture](/ai/deepseek/flash-mla/references/kernel-architecture) | SM90 (Hopper) 和 SM100 (Blackwell) 内核架构详解，包括 WGMMA/TMA/DSM/tmem/UTCMMA 等硬件特性利用 |
| [kv-cache-layout](/ai/deepseek/flash-mla/references/kv-cache-layout) | FP8 KV cache 内存布局（V32/MODEL1 两种模式）、分页结构、反量化机制与索引格式 |

```{toctree}
:hidden:

api
kernel-architecture
kv-cache-layout
```

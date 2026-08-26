# 概念文档

- [00. mdurl 简介](00-introduction.md) — mdurl 是什么、起源、核心 API 概览、设计哲学
- [01. URL 数据结构](01-url-data-structure.md) — URL namedtuple 八个字段语义、MutableURL 内部构建器、不可变设计模式
- [02. URL 解析与格式化](02-parse-and-format.md) — parse() 完整解析流程、slashes_denote_host 参数、format() 逆向拼接、与 urllib.parse 的差异
- [03. URL 编码与解码](03-encode-and-decode.md) — encode()/decode() 函数、DEFAULT 与 COMPONENT 两种模式、查找表缓存机制、UTF-8 多字节处理

```{toctree}
:maxdepth: 7

00-introduction
01-url-data-structure
02-parse-and-format
03-encode-and-decode
```

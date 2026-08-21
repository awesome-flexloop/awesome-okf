# 信源登记簿（references/）

本目录存放概念文档中 `sources` 字段指向的信源登记文件，记录源码关键 API 签名、函数签名与常量定义。

## 源码信源

* [commands.py CLI 入口 API 参考](commands-api.md) — CLI 命令定义、Click 选项、配置读取函数、6 个子命令签名、环境变量前缀规则。
* [basic.py 核心业务逻辑 API 参考](basic-api.md) — UpdateItem/UpdateResult 数据类、update/build/stat 核心函数、多进程并行更新机制。
* [catalog.py PO/POT/MO 文件操作 API 参考](catalog-api.md) — load_po/dump_po/write_mo 函数、条目过滤、update_with_fuzzy 合并逻辑、Babel 底层封装。
* [transifex.py Transifex 集成 API 参考](transifex-api.md) — Transifex CLI 检测、资源名规范化、tx add 命令模板、配置文件生成。

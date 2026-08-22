---
type: Facts
okf_version: '0.2'
title: nbformat 源码事实清单
tags:
- jupyter
- nbformat
- ipynb
- json-schema
- notebook
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/nbformat/pyproject.toml
- ../../../../../external/libs/jupyter/nbformat/nbformat/_version.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/notebooknode.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/_struct.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/__init__.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/nbbase.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/reader.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/validator.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/json_compat.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/nbjson.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/rwbase.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/converter.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/convert.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/sign.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/corpus/words.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/_imports.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/sentinel.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/warnings.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/__init__.py
- ../../../../../external/libs/jupyter/nbformat/nbformat/v4/nbformat.v4.schema.json
---

# nbformat 源码事实清单

## 项目元数据

- F-001: pyproject.toml:6 — 包名为 "nbformat"，描述为 "The Jupyter Notebook format"
- F-002: pyproject.toml:9 — 许可证类型为 BSD License（LICENSE 文件）
- F-003: pyproject.toml:24 — 要求 Python 版本 >=3.10
- F-004: pyproject.toml:25-30 — 运行时依赖为 fastjsonschema>=2.15、jsonschema>=2.6、jupyter_core>=4.12（排除5.0.*）、traitlets>=5.1
- F-005: pyproject.toml:83-84 — 注册了 CLI 脚本入口 `jupyter-trust`，指向 `nbformat.sign:TrustNotebookApp.launch_instance`
- F-006: pyproject.toml:86-87 — 版本号通过 hatch-nodejs-version 从 package.json 动态获取
- F-007: nbformat/_version.py:9 — __version__ 通过 importlib.metadata.version("nbformat") 获取，兜底值为 "0.0.0"
- F-008: nbformat/_version.py:28-38 — version_info 是一个包含 major、minor、patch 及可选 pre/dev 字段的元组
- F-009: pyproject.toml:2 — 构建系统使用 hatchling>=1.5 和 hatch-nodejs-version
- F-010: pyproject.toml:159-165 — mypy 配置启用 strict 模式，Python 目标版本为 3.10

## 目录结构

- F-011: nbformat/ — 主包目录包含 v1/、v2/、v3/、v4/ 四个版本子目录
- F-012: nbformat/v4/ — v4 版本目录包含 nbbase.py、nbjson.py、rwbase.py、convert.py、__init__.py 及 6 个 schema JSON 文件
- F-013: nbformat/v4/nbformat.v4.schema.json:2 — v4 schema 使用 JSON Schema draft-04 规范
- F-014: nbformat/corpus/ — 测试语料目录包含 words.py（生成 cell ID）
- F-015: tests/ — 测试目录包含 v1/、v2/、v3/、v4/ 子目录及多个 .ipynb 测试文件

## NotebookNode 类

- F-016: nbformat/notebooknode.py:14 — NotebookNode 继承自 Struct 类
- F-017: nbformat/notebooknode.py:15 — NotebookNode 文档描述为 "A dict-like node with attribute-access"
- F-018: nbformat/notebooknode.py:17-21 — __setitem__ 方法会自动将 Mapping 类型（非 NotebookNode）的值通过 from_dict 递归转换
- F-019: nbformat/notebooknode.py:11 — _ATOMIC_TYPES 包含 str、int、float、bool、bytes、NoneType、complex，deepcopy 时直接复制
- F-020: nbformat/notebooknode.py:23-49 — __deepcopy__ 方法做了性能优化，避免 copy 模块的通用 _reconstruct 路径，原子类型直接 dict.__setitem__
- F-021: nbformat/notebooknode.py:51-70 — update 方法支持 MutableMapping 风格的更新，参数超过1个时抛出 TypeError
- F-022: nbformat/notebooknode.py:73-84 — from_dict 函数递归将 dict 转换为 NotebookNode，tuple/list 中的 dict 也会被转换
- F-023: nbformat/notebooknode.py:40 — 列表内的普通 dict 在 deepcopy 时保持为普通 dict，不转换为 NotebookNode

## Struct 基类（_struct.py）

- F-024: nbformat/_struct.py:13 — Struct 继承自 dict[Any, Any]
- F-025: nbformat/_struct.py:26 — _allownew 类属性默认为 True，控制是否允许添加新键
- F-026: nbformat/_struct.py:49 — __init__ 中通过 object.__setattr__ 设置 _allownew 为 True，避免触发 __setattr__
- F-027: nbformat/_struct.py:52-72 — __setitem__ 在 _allownew=False 时禁止创建新键，抛出 KeyError
- F-028: nbformat/_struct.py:74-104 — __setattr__ 保护类成员不被属性赋值覆盖（如 keys、items、get 等 dict 方法），将 KeyError 转换为 AttributeError
- F-029: nbformat/_struct.py:106-131 — __getattr__ 通过 dict.__getitem__ 获取值，将 KeyError 转换为 AttributeError
- F-030: nbformat/_struct.py:133-145 — __iadd__ 运算符重载为 self.merge(other) 并返回 self
- F-031: nbformat/_struct.py:147-160 — __add__ 运算符返回 self.copy().merge(other) 的新 Struct
- F-032: nbformat/_struct.py:162-191 — __sub__/__isub__ 运算符用于从 Struct 中移除 other 中存在的键
- F-033: nbformat/_struct.py:240-246 — allow_new_attr 方法通过 object.__setattr__ 设置 _allownew 标志
- F-034: nbformat/_struct.py:248-367 — merge 方法支持可定制的冲突解决策略，内置 preserve、update、add、add_flip、add_s 五种策略

## 格式版本体系

- F-035: nbformat/__init__.py:38-43 — versions 字典将主版本号 1-4 映射到对应的模块 v1-v4
- F-036: nbformat/__init__.py:48-49 — 当前版本 current_nbformat 和 current_nbformat_minor 从 v4 模块导入
- F-037: nbformat/v4/nbbase.py:20 — v4 主版本号 nbformat = 4
- F-038: nbformat/v4/nbbase.py:23 — v4 次版本号 nbformat_minor = 5（即 v4.5）
- F-039: nbformat/v4/nbbase.py:26-34 — nbformat_schema 字典映射 (major, minor) 到 schema 文件名，包含 4.0-4.5 各版本，(None, None) 映射到最新版
- F-040: nbformat/v4/nbformat.v4.schema.json:80-83 — v4.5 schema 要求 nbformat_minor >= 5
- F-041: nbformat/v4/nbformat.v4.schema.json:84-88 — v4 schema 要求 nbformat = 4（minimum: 4, maximum: 4）
- F-042: nbformat/reader.py:44-46 — get_version 函数从 notebook dict 中读取 nbformat（默认1）和 nbformat_minor（默认0）

## v4 Schema 结构

- F-043: nbformat/v4/nbformat.v4.schema.json:5 — 根级别 additionalProperties: false
- F-044: nbformat/v4/nbformat.v4.schema.json:6 — 根级别必需字段为 metadata、nbformat_minor、nbformat、cells
- F-045: nbformat/v4/nbformat.v4.schema.json:106-113 — cell 定义使用 oneOf 包含 raw_cell、markdown_cell、code_cell 三种类型
- F-046: nbformat/v4/nbformat.v4.schema.json:98-104 — cell_id 类型为 string，pattern 为 ^[a-zA-Z0-9-_]+$，长度 1-64
- F-047: nbformat/v4/nbformat.v4.schema.json:115-151 — raw_cell 必需字段：id、cell_type、metadata、source，cell_type 枚举值为 ["raw"]
- F-048: nbformat/v4/nbformat.v4.schema.json:153-185 — markdown_cell 必需字段：id、cell_type、metadata、source，cell_type 枚举值为 ["markdown"]
- F-049: nbformat/v4/nbformat.v4.schema.json:187-275 — code_cell 必需字段：id、cell_type、metadata、source、outputs、execution_count，cell_type 枚举值为 ["code"]
- F-050: nbformat/v4/nbformat.v4.schema.json:301-309 — output 定义使用 oneOf 包含 execute_result、display_data、stream、error 四种类型
- F-051: nbformat/v4/nbformat.v4.schema.json:311-329 — execute_result 必需字段：output_type、data、metadata、execution_count，output_type 枚举为 ["execute_result"]
- F-052: nbformat/v4/nbformat.v4.schema.json:331-344 — display_data 必需字段：output_type、data、metadata，output_type 枚举为 ["display_data"]
- F-053: nbformat/v4/nbformat.v4.schema.json:346-365 — stream 必需字段：output_type、name、text，output_type 枚举为 ["stream"]
- F-054: nbformat/v4/nbformat.v4.schema.json:367-391 — error 必需字段：output_type、ename、evalue、traceback，output_type 枚举为 ["error"]
- F-055: nbformat/v4/nbformat.v4.schema.json:460-468 — multiline_string 定义为 oneOf: string 或 string 数组
- F-056: nbformat/v4/nbformat.v4.schema.json:277-299 — unrecognized_cell 定义用于未来版本的未知 cell 类型，additionalProperties: true
- F-057: nbformat/v4/nbformat.v4.schema.json:393-406 — unrecognized_output 定义用于未来版本的未知 output 类型
- F-058: nbformat/v4/nbformat.v4.schema.json:13-26 — metadata.kernelspec 必需 name 和 display_name 字段
- F-059: nbformat/v4/nbformat.v4.schema.json:28-53 — metadata.language_info 必需 name 字段

## 验证器（validator.py）

- F-060: nbformat/validator.py:21 — validators 字典以 (validator_name, version, version_minor, relax_add_props) 为键缓存验证器实例
- F-061: nbformat/validator.py:36-47 — _relax_additional_properties 递归将 schema 中所有 additionalProperties 设置为 True
- F-062: nbformat/validator.py:50-53 — _allow_undefined 向 cell/output 的 oneOf 中添加 unrecognized_cell/unrecognized_output 定义
- F-063: nbformat/validator.py:56-93 — get_validator 函数在版本号超前时自动 relax schema，支持 relax_add_props 参数
- F-064: nbformat/validator.py:113-132 — isvalid 函数执行 deepcopy 后验证，不修改原对象，验证失败返回 False
- F-065: nbformat/validator.py:149-150 — _ITEM_LIMIT = 16，_STR_LIMIT = 64，用于截断验证错误信息
- F-066: nbformat/validator.py:181-220 — NotebookValidationError 继承自 ValidationError，通过 _truncate_obj 截断错误输出避免大段 traceback
- F-067: nbformat/validator.py:223-261 — better_validation_error 在 oneOf 失败时尝试根据 cell_type/output_type 单独验证以获得更精确的错误
- F-068: nbformat/validator.py:264-316 — normalize 公共函数 deepcopy 后调用 _normalize，返回 (changes, notebook)
- F-069: nbformat/validator.py:341-380 — _normalize 在 (4,5) 及以上版本检查 cell id，缺失时生成新 id 并发出 MissingIDFieldWarning，重复 id 时修复并发出 DuplicateCellId
- F-070: nbformat/validator.py:381-384 — strip_invalid_metadata 参数控制是否剥离不匹配 schema 的 metadata 字段
- F-071: nbformat/validator.py:489-512 — _get_errors 优先使用 fastjsonschema 获取快速结果，错误消息需要更详细时回退到 jsonschema
- F-072: nbformat/validator.py:589-649 — iter_validate 是生成器函数，逐个 yield ValidationError，支持 strip_invalid_metadata

## JSON 验证器后端（json_compat.py）

- F-073: nbformat/json_compat.py:12-16 — 同时支持 fastjsonschema 和 jsonschema（Draft4Validator）两个验证库
- F-074: nbformat/json_compat.py:27-52 — JsonSchemaValidator 包装类，提供 validate、iter_errors、error_tree 方法
- F-075: nbformat/json_compat.py:55-95 — FastJsonSchemaValidator 继承 JsonSchemaValidator，使用 fastjsonschema.compile 编译 schema，error_tree 方法抛出 NotImplementedError
- F-076: nbformat/json_compat.py:118-123 — get_current_validator 通过环境变量 NBFORMAT_VALIDATOR 选择验证器，默认值为 "fastjsonschema"

## 读写器

- F-077: nbformat/reader.py:12-14 — NotJSONError 继承自 ValueError
- F-078: nbformat/reader.py:16-26 — parse_json 函数捕获 ValueError 并抛出 NotJSONError，错误消息限制在 80 字符
- F-079: nbformat/reader.py:49-84 — reads 函数解析 JSON、获取版本号、调用对应版本模块的 to_notebook_json，不做版本转换
- F-080: nbformat/v4/nbjson.py:15-22 — BytesEncoder 自定义 JSONEncoder，将 bytes 类型按 ascii 解码
- F-081: nbformat/v4/nbjson.py:25-42 — JSONReader.reads 解析 JSON 后调用 to_notebook，to_notebook 执行 from_dict→rejoin_lines→strip_transient
- F-082: nbformat/v4/nbjson.py:45-60 — JSONWriter.writes 使用 indent=1、sort_keys=True、separators=(",",": ")、ensure_ascii=False，deepcopy 后 split_lines→strip_transient
- F-083: nbformat/v4/rwbase.py:27-52 — rejoin_lines 将 cell.source 及 output 中的多行字符串列表合并为单字符串
- F-084: nbformat/v4/rwbase.py:69-92 — split_lines 将多行字符串拆分为行列表（保留换行符），用于 VCS 友好的文件输出
- F-085: nbformat/v4/rwbase.py:95-105 — strip_transient 移除 metadata 中的 orig_nbformat、orig_nbformat_minor、signature 以及 cell.metadata.trusted
- F-086: nbformat/v4/rwbase.py:108-132 — NotebookReader/NotebookWriter 抽象基类，定义 reads/writes 和 read/write 接口
- F-087: nbformat/__init__.py:66-101 — reads 顶层函数调用 reader.reads→可选 convert→validate，验证错误仅记录日志不抛出
- F-088: nbformat/__init__.py:104-137 — writes 顶层函数可选 convert→validate→对应版本 writes_json
- F-089: nbformat/__init__.py:140-174 — read 顶层函数支持文件路径或文件对象，自动以 utf8 编码打开文件
- F-090: nbformat/__init__.py:177-211 — write 顶层函数确保输出以换行符结尾，支持文件路径或文件对象

## 版本转换（converter.py & v4/convert.py）

- F-091: nbformat/converter.py:12-68 — convert 函数递归实现逐步版本转换，升级用新版本的 upgrade，降级用旧版本的 downgrade
- F-092: nbformat/v4/convert.py:29-99 — upgrade 函数支持 v3→v4 和 v4 内部小版本升级，v4.4→v4.5 时为每个 cell 添加随机 id
- F-093: nbformat/v4/convert.py:57-60 — v3→v4 升级时在 metadata 中记录 orig_nbformat 和 orig_nbformat_minor
- F-094: nbformat/v4/convert.py:67-73 — v3→v4 升级时将 worksheets 展平为 cells 列表
- F-095: nbformat/v4/convert.py:102-132 — upgrade_cell 将 v3 heading cell 转为 markdown heading（# 前缀），code cell 的 input→source、prompt_number→execution_count
- F-096: nbformat/v4/convert.py:135-163 — downgrade_cell 将 markdown heading（单行 # 开头）转回 v3 heading cell，移除 id 和 attachments
- F-097: nbformat/v4/convert.py:166-175 — _mime_map 定义 v3 别名到 MIME type 的映射（text→text/plain, py→png 等）
- F-098: nbformat/v4/convert.py:195-229 — upgrade_output 将 pyout→execute_result、pyerr→error，stream.stream→stream.name，数据移入 data 子字典
- F-099: nbformat/v4/convert.py:270-296 — downgrade 函数将 v4 notebook 转回 v3，重建 worksheets 结构
- F-100: nbformat/__init__.py:58-63 — NO_CONVERT 是一个 Sentinel 单例，用于阻止自动版本转换

## v4 Notebook 构造 API（nbbase.py）

- F-101: nbformat/v4/nbbase.py:44-70 — new_output 函数根据 output_type 设置默认值（stream 默认 name=stdout、error 默认 ename=NotImplementedError 等），创建后立即 validate
- F-102: nbformat/v4/nbbase.py:73-114 — output_from_msg 从 kernel IOPub 消息创建 output，支持 execute_result、stream、display_data、error 四种消息类型
- F-103: nbformat/v4/nbbase.py:117-130 — new_code_cell 创建 code cell，默认包含 id（随机）、cell_type="code"、空 metadata、execution_count=None、空 source、空 outputs
- F-104: nbformat/v4/nbbase.py:133-144 — new_markdown_cell 创建 markdown cell，默认包含 id、cell_type="markdown"、source、空 metadata
- F-105: nbformat/v4/nbbase.py:147-158 — new_raw_cell 创建 raw cell，默认包含 id、cell_type="raw"、source、空 metadata
- F-106: nbformat/v4/nbbase.py:161-171 — new_notebook 创建 notebook 根节点，包含 nbformat=4、nbformat_minor=5、空 metadata、空 cells 列表

## 签名机制（sign.py）

- F-107: nbformat/sign.py:46-49 — algorithms 列表从 hashlib.algorithms_guaranteed 中排除 shake_* 算法（不兼容 HMAC）
- F-108: nbformat/sign.py:52-82 — SignatureStore 抽象基类定义 store_signature、check_signature、remove_signature、close 接口
- F-109: nbformat/sign.py:84-124 — MemorySignatureStore 使用 OrderedDict 实现 LRU 缓存，cache_size=65535，超量时淘汰最旧 25%
- F-110: nbformat/sign.py:127-282 — SQLiteSignatureStore 使用 SQLite 数据库持久化签名，nbsignatures 表包含 algorithm、signature、path、last_seen 字段，自动处理数据库损坏（重命名为 .bak 并重建）
- F-111: nbformat/sign.py:284-302 — yield_everything 生成器按排序后的键遍历 dict，递归将所有内容 yield 为 bytes，用于 HMAC 计算
- F-112: nbformat/sign.py:305-318 — yield_code_cells 版本无关地迭代所有 code cell（v4 直接遍历 cells，v3 遍历 worksheets→cells）
- F-113: nbformat/sign.py:321-332 — signature_removed 上下文管理器临时移除 metadata.signature，计算签名后恢复
- F-114: nbformat/sign.py:369-471 — NotebookNotary 继承 LoggingConfigurable，默认算法为 sha256，密钥文件为 1024 字节随机数据存储在 notebook_secret
- F-115: nbformat/sign.py:514-526 — compute_signature 使用 HMAC(secret, digestmod) 对 yield_everything 的输出逐个 update，返回 hexdigest
- F-116: nbformat/sign.py:548-557 — sign 方法计算签名后存入 store；unsign 方法从 store 中移除签名
- F-117: nbformat/sign.py:568-581 — mark_cells 在所有 code cell 的 metadata 上设置 trusted 标志
- F-118: nbformat/sign.py:583-614 — _check_cell 判定 cell 安全条件：显式 trusted 或不含 execute_result/display_data 等富输出
- F-119: nbformat/sign.py:647-721 — TrustNotebookApp 是 JupyterApp 子类，提供 jupyter-trust CLI，支持 --reset 清除缓存和重新生成密钥
- F-120: nbformat/corpus/words.py:8-10 — generate_corpus_id 生成 uuid4().hex[:8] 作为 cell id（8 字符十六进制）

## 依赖关系

- F-121: nbformat/notebooknode.py:5 — 从 collections.abc 导入 Mapping
- F-122: nbformat/sign.py:40-42 — 依赖 jupyter_core.application.JupyterApp 和 traitlets 配置系统
- F-123: nbformat/_imports.py:12-39 — import_item 工具函数实现按字符串路径导入模块（vendored from ipython_genutils）
- F-124: nbformat/sentinel.py:8-20 — Sentinel 类用于创建具有有用 repr 的单例常量（如 NO_CONVERT）
- F-125: nbformat/warnings.py:8-29 — 定义 MissingIDFieldWarning 和 DuplicateCellId，均继承自 FutureWarning

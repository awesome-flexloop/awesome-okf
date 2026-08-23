---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- server
- extension
- fileid
sources:
- ../../../../../external/libs/jupyter/jupyter_server_fileid/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_server_fileid/README.md
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/__init__.py
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/cli.py
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py
- ../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/pytest_plugin.py
type: Facts
title: jupyter_server_fileid 源码事实清单
---

# jupyter_server_fileid Facts

## 元数据

1. 包名为 `jupyter_server_fileid`，描述为 "Jupyter Server extension providing an implementation of the File ID service"。[pyproject.toml:6-10](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L6-L10)
2. 当前版本为 `0.9.3`，定义在 `__init__.py` 中。[__init__.py:7](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/__init__.py#L7)
3. 作者为 "David L. Qiu"，邮箱为 david@qiu.dev。[pyproject.toml:7](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L7)
4. 要求 Python ≥ 3.9，支持 Python 3.9 至 3.14。[pyproject.toml:11](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L11) [pyproject.toml:17-22](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L17-L22)
5. 核心依赖为 `jupyter_server>=2.10, <3` 和 `jupyter_events>=0.9.0`。[pyproject.toml:25-28](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L25-L28)
6. 可选依赖组 `cli` 需要 `click` 包。[pyproject.toml:38-40](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L38-L40)
7. 构建系统使用 `hatchling>=1.0` 作为 build-backend。[pyproject.toml:1-3](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L1-L3)
8. 版本号通过 hatch 从 `__init__.py` 动态读取。[pyproject.toml:83-84](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L83-L84)
9. CLI 入口点为 `jupyter-fileid = jupyter_server_fileid.cli:main`。[pyproject.toml:42-43](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L42-L43)
10. 许可证为 BSD License，项目主页在 GitHub 上的 jupyter-server 组织下。[pyproject.toml:14](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L14) [pyproject.toml:48-49](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/pyproject.toml#L48-L49)
11. jupyter-config 目录下的 JSON 配置文件将扩展自动注册到 ServerApp 的 jpserver_extensions。[jupyter_server_fileid.json:1-7](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter-config/jupyter_server_config.d/jupyter_server_fileid.json#L1-L7)

## 目录结构

12. 包的核心 Python 源码位于 `jupyter_server_fileid/` 子目录下。[目录结构]
13. 核心模块文件包括 `__init__.py`、`extension.py`、`manager.py`、`handler.py`、`cli.py`、`pytest_plugin.py`。[目录结构]
14. 测试位于 `tests/` 目录下，包含 `test_manager.py` 和 `test_handler.py`。[目录结构]
15. 包内包含 `py.typed` 标记文件，表示支持 PEP 561 类型提示。[目录结构]
16. 文档位于 `docs/` 目录，使用 Sphinx 构建。[目录结构]

## 核心类/接口

17. `StatStruct` 是一个数据结构，包含字段 `ino`（inode）、`crtime`（创建时间，可选）、`mtime`（修改时间）、`is_dir`、`is_symlink`。[manager.py:19-24](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L19-L24)
18. `BaseFileIdManager` 是所有 File ID manager 实现的抽象基类，继承自 `ABC` 和 `LoggingConfigurable`，元类为 `FileIdManagerMeta`（组合了 `ABCMeta` 和 `MetaHasTraits`）。[manager.py:49-57](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L49-L57)
19. `BaseFileIdManager` 定义了 traitlet 配置属性 `root_dir`（Unicode，不可通过配置文件设置，允许 None）。[manager.py:61-65](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L61-L65)
20. `BaseFileIdManager` 定义了可配置的 `db_path` traitlet，默认值为 `jupyter_data_dir()/file_id_manager.db`，支持设置为 `:memory:` 使用内存数据库。[manager.py:27](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L27) [manager.py:67-75](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L67-L75)
21. `db_path` 验证器要求路径必须是绝对路径或 `:memory:`，否则抛出 `TraitError`。[manager.py:77-85](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L77-L85)
22. `db_journal_mode` traitlet 配置 SQLite journal mode，可选值为 `DELETE`、`TRUNCATE`、`PERSIST`、`MEMORY`、`WAL`、`OFF`。[manager.py:87-102](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L87-L102)
23. `BaseFileIdManager._uuid()` 静态方法通过 `uuid.uuid4()` 生成 UUID4 字符串作为文件 ID。[manager.py:104-106](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L104-L106)
24. `BaseFileIdManager` 声明了抽象方法 `_normalize_path()` 和 `_from_normalized_path()`，用于 API 路径和持久化路径之间的转换。[manager.py:108-119](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L108-L119)
25. `BaseFileIdManager` 提供了三个递归辅助方法：`_move_recursive()`、`_copy_recursive()`、`_delete_recursive()`，使用 SQL GLOB 模式匹配子路径。[manager.py:121-162](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L121-L162)
26. `BaseFileIdManager` 声明了七个抽象操作方法：`index()`、`get_id()`、`get_path()`、`move()`、`copy()`、`delete()`、`save()`。[manager.py:164-238](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L164-L238)
27. `BaseFileIdManager` 声明了抽象方法 `get_handlers_by_action()`，返回事件 action 到处理函数的映射字典。[manager.py:240-250](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L240-L250)
28. `log()` 装饰器工厂接受 `log_before` 和 `log_after` 两个函数，在目标方法执行前后分别记录 INFO 级日志。[manager.py:30-46](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L30-L46)

## ArbitraryFileIdManager

29. `ArbitraryFileIdManager` 是面向任意文件系统（包括非本地文件系统如 S3）的实现，路径仅在调用 `move()`、`copy()`、`delete()` 时更新。[manager.py:253-259](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L253-L259)
30. `ArbitraryFileIdManager` 默认 `db_journal_mode` 为 `"DELETE"`。[manager.py:270-272](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L270-L272)
31. `ArbitraryFileIdManager` 初始化时创建 SQLite 连接，创建 `Files` 表（`id TEXT PRIMARY KEY, path TEXT NOT NULL UNIQUE`）和 `ix_Files_path` 索引。[manager.py:274-300](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L274-L300)
32. `ArbitraryFileIdManager._normalize_separators()` 将反斜杠替换为正斜杠，实现跨平台路径分隔符统一。[manager.py:302-307](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L302-L307)
33. `ArbitraryFileIdManager._normalize_path()` 使用 `posixpath.commonprefix` 检查路径是否已包含 root_dir 前缀，如不包含则拼接，并使用 posixpath 处理路径。[manager.py:309-321](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L309-L321)
34. `ArbitraryFileIdManager._from_normalized_path()` 将持久化路径转换回相对于 root_dir 的 API 路径（正斜杠分隔），如果路径不在 root_dir 下则返回 None。[manager.py:323-337](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L323-L337)
35. `ArbitraryFileIdManager._create()` 内部方法先查询是否已有记录，有则返回已有 ID，无则生成新 UUID 并 INSERT。[manager.py:339-351](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L339-L351)
36. `ArbitraryFileIdManager.index()` 在事务中调用 `_create()` 并返回 ID。[manager.py:353-357](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L353-L357)
37. `ArbitraryFileIdManager.get_id()` 通过路径精确查询，未找到返回 None。[manager.py:359-364](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L359-L364)
38. `ArbitraryFileIdManager.move()` 在事务中：如果旧路径存在则 UPDATE 路径并递归移动子项；如果旧路径不存在则在新路径创建新记录。[manager.py:371-388](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L371-L388)
39. `ArbitraryFileIdManager.copy()` 在事务中为目标路径创建新记录，并递归复制子目录记录（生成新 UUID）。[manager.py:390-398](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L390-L398)
40. `ArbitraryFileIdManager.save()` 是一个空操作，直接返回 None。[manager.py:407-408](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L407-L408)
41. `ArbitraryFileIdManager` 的事件处理器映射中 `get` 和 `save` 设为 None（忽略），`rename`/`copy`/`delete` 分别映射到对应方法。[manager.py:410-419](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L410-L419)
42. `ArbitraryFileIdManager.root_dir` 验证器将 None 转换为空字符串，将路径分隔符统一为正斜杠。[manager.py:261-268](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L261-L268)

## LocalFileIdManager

43. `LocalFileIdManager` 是面向本地文件系统的实现，通过 inode 和创建时间追踪文件，支持 out-of-band 文件移动检测。[manager.py:435-449](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L435-L449)
44. `LocalFileIdManager` 要求 `root_dir` 必须是非 None 的绝对路径，否则抛出 `TraitError`。[manager.py:451-461](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L451-L461)
45. `LocalFileIdManager` 默认 `db_journal_mode` 为 `"WAL"`（Write-Ahead Logging）。[manager.py:463-465](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L463-L465)
46. `LocalFileIdManager` 的 `Files` 表字段更丰富：`id TEXT PRIMARY KEY, path TEXT NOT NULL, ino INTEGER NOT NULL UNIQUE, crtime INTEGER, mtime INTEGER NOT NULL, is_dir TINYINT NOT NULL`，path 字段没有 UNIQUE 约束（因为删除文件的记录需保留，新文件可能占用同一路径）。[manager.py:483-494](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L483-L494)
47. `LocalFileIdManager` 创建两个额外索引：`ix_Files_path`（path 列）和 `ix_Files_is_dir`（is_dir 列），`ino` 列通过 UNIQUE 约束自动建索引。[manager.py:497-498](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L497-L498)
48. `LocalFileIdManager` 初始化时调用 `_index_all()` 递归索引 root_dir 下的所有目录。[manager.py:495](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L495)
49. `LocalFileIdManager._normalize_path()` 将 API 路径转为文件系统绝对路径（拼接 root_dir），使用 `os.path.normcase()` 和 `os.path.normpath()` 规范化。[manager.py:501-509](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L501-L509)
50. `LocalFileIdManager._from_normalized_path()` 将文件系统路径转回相对于 root_dir 的 API 路径，路径分隔符统一替换为正斜杠。[manager.py:511-528](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L511-L528)
51. `LocalFileIdManager._index_dir_recursively()` 使用 `os.scandir()` 递归遍历目录并索引。[manager.py:537-546](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L537-L546)
52. `LocalFileIdManager._sync_all()` 遍历所有已索引目录，通过比较 mtime 检测"脏"目录（mtime 变化或未索引），调用 `_sync_dir()` 同步内容；维护 `_update_cursor` 标志处理路径变更导致的游标失效。[manager.py:548-604](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L548-L604)
53. `LocalFileIdManager._sync_file()` 通过 inode 查询数据库：如果 inode 未找到返回 None；如果 crtime 不匹配则删除旧记录返回 None（视为不同文件）；否则更新路径并递归移动子目录记录。[manager.py:633-687](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L633-L687)
54. `LocalFileIdManager._sync_file()` 遇到 symlink 直接返回 None，不做处理。[manager.py:662-663](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L662-L663)
55. `LocalFileIdManager._parse_raw_stat()` 从 `os.stat_result` 解析 `StatStruct`，crtime 在 Windows 使用 `st_ctime_ns`，在 macOS 使用 `st_birthtime`，其他平台（Linux）为 None。[manager.py:689-709](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L689-L709)
56. `LocalFileIdManager._stat()` 使用 `os.lstat()`（不跟随 symlink），捕获 OSError 返回 None。[manager.py:711-719](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L711-L719)
57. `LocalFileIdManager.index()` 遇到 symlink 时递归索引其真实路径（`os.path.realpath`）。[manager.py:811-813](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L811-L813)
58. `LocalFileIdManager.index()` 先调用 `_sync_file()` 尝试同步（检测 out-of-band 移动），同步成功返回已有 ID，否则调用 `_create()` 创建新记录。[manager.py:815-822](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L815-L822)
59. `LocalFileIdManager.get_path()` 采用乐观策略：先直接查询路径与 stat 比对（ino + crtime），匹配则立即返回；不匹配则调用 `_sync_all()` 后重试一次；仍失败返回 None。[manager.py:838-872](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L838-L872)
60. `LocalFileIdManager.move()` 使用 `@log` 装饰器记录日志，在事务中验证新路径存在后调用 `_sync_file()` 检测是否已被索引，否则创建新记录。[manager.py:874-904](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L874-L904)
61. `LocalFileIdManager.copy()` 重写了 `_copy_recursive()` 以在复制时获取 stat 信息并创建带 ino 的记录，copy 方法对目录递归复制并索引源路径和目标路径。[manager.py:906-946](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L906-L946)
62. `LocalFileIdManager.delete()` 在事务中处理目录递归删除，然后删除路径对应的记录。[manager.py:948-961](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L948-L961)
63. `LocalFileIdManager.save()` 通过 ino 和 path 联合查询记录，找到后更新 stat 信息（mtime 等），注释中说明这在 out-of-band 删除重建场景下可能错误保留旧 ID。[manager.py:963-990](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L963-L990)
64. `LocalFileIdManager` 的事件处理器映射中 `get` 设为 None，`save`/`rename`/`copy`/`delete` 都有对应处理。[manager.py:992-1001](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L992-L1001)
65. 两个 Manager 的 `__del__` 方法都尝试 commit 并关闭 SQLite 连接，捕获跨线程 GC 导致的 `sqlite3.ProgrammingError`。[manager.py:421-432](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L421-L432) [manager.py:1003-1008](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L1003-L1008)

## API 处理器

66. `BaseHandler` 继承自 `jupyter_server.base.handlers.APIHandler`，设置 `auth_resource = "contents"`，提供 `file_id_manager` 属性从 `self.settings` 获取 manager 实例。[handler.py:9-16](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L9-L16)
67. `FileIDHandler` 处理 GET `/api/fileid/id` 请求，接受 `path` 查询参数，调用 `file_id_manager.get_id(path)` 返回 `{"id": id, "path": path}` JSON。[handler.py:19-40](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L19-L40)
68. `FilePathHandler` 处理 GET `/api/fileid/path` 请求，接受 `id` 查询参数，调用 `file_id_manager.get_path(id)` 返回 `{"id": id, "path": path}` JSON。[handler.py:43-65](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L43-L65)
69. 两个 Handler 都使用 `@web.authenticated` 和 `@authorized` 装饰器进行认证和授权。[handler.py:22-23](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L22-L23) [handler.py:46-47](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L46-L47)
70. 缺少必需查询参数时返回 HTTP 400，未找到 ID/路径时返回 HTTP 404。[handler.py:30-40](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L30-L40) [handler.py:54-65](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py#L54-L65)

## 数据库/持久化

71. 默认数据库路径为 `jupyter_data_dir()/file_id_manager.db`，通过 `jupyter_core.paths.jupyter_data_dir()` 获取 Jupyter 数据目录。[manager.py:27](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L27)
72. 数据库可设置为 `:memory:` 使用 SQLite 内存数据库，不写磁盘。[manager.py:72](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py#L72)
73. CLI 提供 `jupyter-fileid drop` 命令，连接默认数据库并执行 `DROP TABLE Files;`。[cli.py:15-21](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/cli.py#L15-L21)

## 与 jupyter_server 集成

74. `FileIdExtension` 继承自 `jupyter_server.extension.application.ExtensionApp`，`name` 为 `"jupyter_server_fileid"`。[extension.py:11-12](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L11-L12)
75. `FileIdExtension.file_id_manager_class` 是一个 Type traitlet，默认值为 `ArbitraryFileIdManager`，允许用户配置替换为 `LocalFileIdManager` 或自定义实现。[extension.py:14-22](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L14-L22)
76. `FileIdExtension.handlers` 注册了两个路由：`/api/fileid/id` → `FileIDHandler` 和 `/api/fileid/path` → `FilePathHandler`。[extension.py:30-33](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L30-L33)
77. `initialize_settings()` 方法实例化配置的 file_id_manager_class，传入 `log`、`root_dir`（来自 serverapp.root_dir）和 `config`，并将实例存入 `self.settings["file_id_manager"]`。[extension.py:35-43](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L35-L43)
78. `initialize_event_listeners()` 通过 `jupyter_events` 的 EventLogger 添加监听器，监听 schema_id 为 `https://events.jupyter.org/jupyter_server/contents_service/v1` 的 contents manager 事件。[extension.py:49-63](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L49-L63)
79. 事件监听器 `cm_listener` 从事件 data 中提取 `action` 字段，查找 `handlers_by_action` 映射中对应的处理函数并调用，action 值为 None 时忽略该事件。[extension.py:52-57](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py#L52-L57)
80. 扩展通过 `_jupyter_server_extension_points()` 函数注册为 Jupyter Server 扩展点，返回 `FileIdExtension` 类。[__init__.py:10-11](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/__init__.py#L10-L11)

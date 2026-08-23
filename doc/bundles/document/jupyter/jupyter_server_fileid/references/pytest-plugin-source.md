---
okf_version: "0.2"
type: reference
title: "pytest_plugin.py 源码解析"
description: "pytest 测试插件：提供 LocalFileIdManager/ArbitraryFileIdManager 的测试 fixtures 和文件系统操作辅助类 FsHelpers。"
tags: [jupyter, fileid, pytest, fixture, testing, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pytest-plugin-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/pytest_plugin.py"
    title: "jupyter_server_fileid/pytest_plugin.py"
---

# pytest_plugin.py 源码解析

`pytest_plugin.py` 约 184 行，提供 pytest fixtures 和测试辅助工具。

## Fixtures 一览

| Fixture | 作用域 | 返回类型 | 说明 |
|---------|--------|---------|------|
| `jp_server_config` | function | `Dict[str, Any]` | 启用 jupyter_server_fileid 扩展的服务端配置 |
| `fid_db_path` | function | `str` | 测试数据库文件路径（`jp_data_dir/fileidmanager_test.db`） |
| `delete_fid_db` | function (autouse) | None | 每个测试后自动删除数据库文件 |
| `fid_manager` | function | `LocalFileIdManager` | 预配置的 LocalFileIdManager 实例（journal_mode=OFF） |
| `arbitrary_fid_manager` | function | `ArbitraryFileIdManager` | 预配置的 ArbitraryFileIdManager 实例（journal_mode=OFF） |
| `any_fid_manager_class` | function (parametrized) | `Type[BaseFileIdManager]` | 参数化 fixture，轮流返回 Local 和 Arbitrary 类 |
| `any_fid_manager` | function | `BaseFileIdManager` | 参数化创建任一管理器实例（journal_mode=OFF） |
| `fs_helpers` | function | `FsHelpers` | 文件系统操作辅助类 |

### 关键 Fixture 实现

**fid_manager**：
```python
@pytest.fixture
def fid_manager(fid_db_path, jp_root_dir):
    fid_manager = LocalFileIdManager(db_path=fid_db_path, root_dir=str(jp_root_dir))
    fid_manager.con.execute("PRAGMA journal_mode = OFF")  # 禁用journal防测试flakiness
    return fid_manager
```

禁用 journal mode 的原因：
1. 避免临时 journal 文件与已删除文件有相同 ino/crtime 导致误判为移动
2. 提升测试执行速度

**any_fid_manager_class** 参数化：
```python
@pytest.fixture(params=["local", "arbitrary"])
def any_fid_manager_class(request):
    class_by_param = {"local": LocalFileIdManager, "arbitrary": ArbitraryFileIdManager}
    return class_by_param[request.param]
```

让同一个测试用例自动对两种管理器实现都执行一遍。

## FsHelpers 类

测试文件系统操作的辅助类，提供带时间戳控制的文件操作：

| 方法 | 功能 | 关键行为 |
|------|------|---------|
| `touch(path, dir=False)` | 创建文件/目录 | 设置唯一 mtime，更新父目录 mtime |
| `move(old_path, new_path)` | 移动文件/目录 | os.rename + 更新父目录 mtime |
| `edit(path)` | 模拟编辑文件 | 增加文件 mtime |
| `delete(path)` | 删除文件/目录 | shutil.rmtree/os.remove + 更新父目录 mtime |
| `copy(old_path, new_path)` | 复制文件/目录 | shutil.copytree/copyfile + 更新父目录 mtime |

### 时间戳控制机制

所有方法使用 `self.fake_time`（初始值 1，每次操作递增）确保每个文件/目录的 mtime 唯一：

```python
def touch(self, path, dir=False):
    if not os.path.isabs(path):
        path = os.path.join(jp_root_dir, path)
    if dir:
        os.mkdir(path)
    else:
        Path(path).touch()
    parent = Path(path).parent
    stat = os.stat(path)
    current_time = stat.st_mtime + self.fake_time
    os.utime(parent, (stat.st_atime, current_time))
    os.utime(path, (current_time, current_time))
    self.fake_time += 1
```

这对于测试 `_sync_all()` 的 mtime 脏目录检测机制至关重要——确保测试环境中 mtime 变化可预测。

## conftest.py

根目录 `conftest.py` 仅注册 pytest 插件：
```python
pytest_plugins = [
    "jupyter_server.pytest_plugin",
    "jupyter_server_fileid.pytest_plugin",
    "pytest_jupyter",
]
```

---

**相关文档：**
- [manager.py 源码解析](manager-source.md) — 被测试的管理器实现
- [基本使用示例](../examples/01-basic-usage.md) — API 使用示例

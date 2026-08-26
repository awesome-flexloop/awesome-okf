# Sphinx API参考与信源索引

本目录包含Sphinx源码学习的参考文档，分为源码关键片段、API参考和外部资源三类。

## 源码关键片段

| 文档 | 说明 |
|------|------|
| [sphinx-app-init.md](sphinx-app-init.md) | Sphinx.__init__方法核心源码片段与初始化顺序 |
| [builder-base.md](builder-base.md) | Builder基类的类属性、初始化和核心构建方法源码 |
| [event-lifecycle.md](event-lifecycle.md) | 核心事件定义、回调签名与触发阶段 |
| [extension-setup.md](extension-setup.md) | 扩展setup函数签名、返回值元数据和Extension类 |

## API参考（源码Grep验证）

| 文档 | 说明 |
|------|------|
| [application-api.md](application-api.md) | Sphinx应用类完整API：__init__参数、属性、add_*方法、build方法 |
| [config-api.md](config-api.md) | 配置系统API：Config类、_Opt/ENUM类型、add_config_value参数 |
| [events-api.md](events-api.md) | 事件系统API：EventManager、connect/emit/add_event、EventListener |
| [registry-api.md](registry-api.md) | 组件注册表API：SphinxComponentRegistry各组件注册方法 |
| [builder-api.md](builder-api.md) | Builder基类API：属性、模板方法、write_doc/get_target_uri |
| [extension-metadata.md](extension-metadata.md) | ExtensionMetadata字段完整说明与并行安全声明 |
| [core-events-list.md](core-events-list.md) | 17个核心事件完整列表：参数、触发时机、用途 |

## 用户参考

| 文档 | 说明 |
|------|------|
| [rest-syntax-quickref.md](rest-syntax-quickref.md) | reStructuredText语法速查表：段落/列表/表格/代码块/指令/角色 |
| [official-docs.md](official-docs.md) | Sphinx官方文档关键页面URL索引 |

```{toctree}
:maxdepth: 7

application-api
builder-api
builder-base
config-api
core-events-list
event-lifecycle
events-api
extension-metadata
extension-setup
official-docs
registry-api
rest-syntax-quickref
sphinx-app-init
```

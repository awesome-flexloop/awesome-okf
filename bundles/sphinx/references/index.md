# 信源登记簿（references/）

本目录存放概念文档中 `sources` 字段指向的信源登记文件，记录源码关键片段与API签名。

* [Sphinx 应用初始化源码](sphinx-app-init.md) — `Sphinx.__init__` 核心初始化流程、内置扩展清单、关键步骤顺序。
* [核心事件列表与触发时机](event-lifecycle.md) — 16个核心事件定义、回调签名、触发阶段、Builder/扩展专用事件。
* [Builder 基类核心方法](builder-base.md) — Builder类属性、核心构建方法、构建流程阶段、13种内置构建器。
* [扩展 setup 函数签名与返回值](extension-setup.md) — Extension类、setup函数规范、add_*注册方法速查表。

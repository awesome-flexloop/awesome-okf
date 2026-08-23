# Sphinx 架构洞察

> I阶段产出：基于事实清单提炼的核心洞察四元组（陈述/证据/反常识/行动）+ 知识地图。

## 核心洞察

### I-001：三位一体核心架构

- **陈述**：Sphinx的核心架构是"应用-事件-注册表"三位一体模式。Sphinx类作为中心编排器，EventManager提供松耦合的扩展点，SphinxComponentRegistry作为所有可扩展组件的注册中心。
- **证据**：F-003, F-007, F-008, F-044
- **反常识**：与许多现代框架不同，Sphinx没有使用复杂的IoC容器或依赖注入框架，而是通过简单的注册表字典+事件回调实现了高度可扩展性。这证明了简单机制的持久生命力——Sphinx从2008年至今仍保持这一核心架构。
- **行动**：写扩展时，理解registry的add_*方法和events的connect/emit机制是第一要务。所有扩展功能都是通过这两个通道接入的。

### I-002：四阶段构建流水线+增量环境缓存

- **陈述**：Sphinx的构建是"读入-解析-转换-写入"四阶段流水线，通过BuildEnvironment的pickle缓存实现增量构建。
- **证据**：F-010, F-015, F-016, F-050, F-078
- **反常识**：environment.pickle缓存是Sphinx增量构建性能的关键——它缓存了解析后的doctree，使得重复构建只需处理变更文件。很多CI配置总是使用`sphinx-build -E`（freshenv=True），这会丢弃缓存导致构建时间成倍增长。
- **行动**：理解BuildEnvironment的生命周期（创建/缓存加载/purge-doc/merge-info）对优化构建性能至关重要；本地开发避免使用-E标志。

### I-003：极简扩展模型——setup(app)单入口

- **陈述**：Sphinx的扩展模型是"setup(app)"单入口+细粒度add_* API，而非基类继承。
- **证据**：F-041, F-055~F-075
- **反常识**：扩展不需要继承任何基类，只需要一个setup(app)函数接收Sphinx实例，然后调用app.add_*方法注册组件。这比许多框架要求继承特定基类更灵活，但也意味着缺少编译时类型检查——注册错误只能在运行时发现。
- **行动**：写扩展的核心就是在setup()中选择正确的add_*方法注册自定义组件，并通过connect()在适当事件点介入构建流程。返回的metadata字典中version字段必填。

### I-004：Domain——多语言语义抽象层

- **陈述**：Domain是Sphinx的"语义层"抽象，将通用文档处理与语言特定的对象描述分离。
- **证据**：F-037, F-063, F-085
- **反常识**：很多用户以为Sphinx只是Python文档工具，实际上Domain机制（py/c/cpp/js/rst/std/math/changeset/citation/index）使其成为真正的多语言文档框架。每个Domain独立管理自己的对象类型、指令、角色、索引和交叉引用。
- **行动**：为新语言或新对象类型添加Sphinx支持，核心是自定义Domain子类，而非修改核心代码。add_directive_to_domain/add_role_to_domain是扩展Domain的关键API。

### I-005：细粒度重建触发机制

- **陈述**：Sphinx的配置系统具有细粒度的重建触发机制（rebuild参数），实现精准的增量构建。
- **证据**：F-034, F-035, F-037, F-056
- **反常识**：配置值变更不总是触发全量重建。rebuild参数控制精度：''无需重建，'env'需重新解析文档（环境重建），'html'只需重写HTML，还有'epub'/'gettext'等格式特定级别。这种精确性是大型项目快速迭代的基础。
- **行动**：自定义add_config_value时必须正确设置rebuild参数。错误设置为'env'会导致不必要的全量文档重新解析，设置为''可能导致配置变更不生效。

## 知识地图

### 文档分组与学习路径

```
入门（零基础）
├── 00-introduction    → Sphinx是什么、核心特性、生态定位
└── 01-getting-started → 安装、quickstart、sphinx-build基本用法、conf.py概览

核心概念（理解架构）
├── 02-application     → Sphinx应用类、初始化流程、属性与生命周期
├── 03-config-system   → 配置系统、conf.py、Config类、add_config_value、_Opt/ENUM
├── 04-event-system    → 事件系统、核心事件列表、connect/emit/优先级
├── 05-build-pipeline  → 构建流水线、BuildEnvironment、增量构建、缓存机制
└── 06-registry        → 组件注册表、Builder/Domain/Directive/Role/Transform注册

高级主题（扩展开发）
├── 07-extension-dev   → 扩展开发指南、setup()函数、Extension元数据
├── 08-builders        → 构建器系统、Builder基类、输出格式
└── 09-domains         → Domain机制、跨语言对象描述、自定义Domain
```

### 概念文档覆盖事实映射

| 概念文档 | 覆盖事实 |
|---------|---------|
| 00-introduction | F-001, F-081~F-093 |
| 01-getting-started | F-005, F-032 |
| 02-application | F-003~F-017, F-078~F-080 |
| 03-config-system | F-032~F-038, F-056 |
| 04-event-system | F-021~F-031, F-057 |
| 05-build-pipeline | F-015~F-016, F-050~F-054, F-078~F-080 |
| 06-registry | F-043~F-049, F-055, F-059~F-075 |
| 07-extension-dev | F-039~F-042, F-055~F-077 |
| 08-builders | F-050~F-054, F-055 |
| 09-domains | F-063~F-065 |

### 示例文档规划

| 示例文档 | 对应概念 | 核心演示 |
|---------|---------|---------|
| 01-minimal-extension | 07-extension-dev | 最简setup()函数，hello world扩展 |
| 02-custom-directive | 06-registry, 07-extension-dev | add_directive自定义指令 |
| 03-custom-role | 06-registry, 07-extension-dev | add_role自定义角色 |
| 04-event-handler | 04-event-system | connect()监听build-finished事件 |
| 05-custom-config | 03-config-system | add_config_value自定义配置 |

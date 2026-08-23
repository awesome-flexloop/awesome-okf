# 概念文档索引

按学习路径顺序排列，建议从00开始依次阅读。

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| [00](00-introduction.md) | 项目介绍 | 定位、设计理念、核心能力、七个分类维度、项目背景 |
| [01](01-getting-started.md) | 5分钟快速上手 | GitHub App创建、项目板设置、本地运行、GitHub Action部署 |
| [02](02-architecture-overview.md) | 架构总览 | 目录结构、模块分层、数据流、全量对账同步模型 |
| [03](03-auth-and-octokit.md) | GitHub App认证与Octokit配置 | App认证流程、Octokit插件（paginateGraphQL/throttling）、限流处理、自定义日志 |
| [04](04-project-class.md) | Project管理类 | Project类API、Field/SingleSelectField类型、字段查找与创建、条目增删改、动态GraphQL Mutation构造 |
| [05](05-field-plugin-system.md) | 字段插件体系 | 四层类型系统（FieldDataType→FieldConfig→ExtractFieldValueType→FieldSpec）、条件类型映射、REQUIRED_FIELDS注册表模式、扩展机制 |
| [06](06-core-fields.md) | 七个核心字段详解 | Author Kind/Opened At/Total Lines Changed/Maintainer Engagement/CI Status/Merge Conflicts/Approval Status的计算逻辑与判定规则 |
| [07](07-sync-loop.md) | 同步循环与增量更新 | 全量对账算法、双源数据获取、映射构建、过期清理、值比较策略（Date时间戳/===）、Dry Run模式、幂等性保证 |
| [08](08-cli-and-action.md) | CLI与GitHub Action集成 | commander参数设计、composite action编排、私钥安全处理、SWC+tsc构建系统、CI/CD流水线、本地与Action部署对比 |

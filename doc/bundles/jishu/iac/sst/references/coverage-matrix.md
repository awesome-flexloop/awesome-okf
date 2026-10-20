# SST 教程主题覆盖矩阵

> 本表用于 E 阶段落实与 V 阶段验收。以下为最终文档路径；新增内容须同步本表。
> 固定源码事实：SST v4.17.2 / `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`。  
> 官网事实：2026-10-20 查阅，不等同于该源码版本行为。

| FR-2 主题 | 事实依据 | 计划文档 | 覆盖边界 / 验收要点 |
|---|---|---|---|
| SST 定位、`sst.config.ts`、应用/阶段/stack/state 的关系 | F-001、F-003–F-005、F-008；W-001–W-003 | `concepts/00-application-model.md`、`concepts/01-config-stage-state.md` | 源码字段与官网操作说明分层；state 格式、备份和 passphrase 仅作为官网采集日陈述。 |
| `sst dev`、部署、差异查看及 CLI 到项目/部署流程的主路径 | F-002、F-003、F-007–F-011；W-001、W-010、W-011 | `concepts/02-cli-project-lifecycle.md`、`examples/03-local-development-and-deployment.md` | 命令到 Pulumi 的源码映射限于 F-010；官网命令示例不冒充本地执行结果。 |
| Go CLI、项目模型、provider/server 桥接、语言运行时与平台组件之间的职责边界 | F-003–F-022 | `concepts/02-cli-project-lifecycle.md`、`concepts/03-components-and-providers.md`、`concepts/04-runtime-server-architecture.md` | 逐层呈现已核验的接口、调用和注册关系；不把相邻模块共存推定为未证实的调用链。 |
| 代表性 AWS/Cloudflare 组件、Pulumi/provider 扩展面和组件/底层资源关系 | F-014、F-021–F-027；W-004–W-007 | `concepts/03-components-and-providers.md` | 仅说明已核验的代表性 namespace 与 Linkable 示例；“150+ providers”带官网日期及厂商自述限定，不作源码计数。 |
| JavaScript SDK 资源链接，以及 Live/Mosaic 开发体验和相关运行时机制 | F-019–F-020、F-023–F-034；W-008–W-010、W-012–W-013 | `concepts/05-resource-linking.md`、`concepts/06-live-mosaic-development.md`、`examples/02-link-resources-to-runtime.md` | 区分 Link 环境变量链路、Mosaic 本地端点与官网 Live 远端通信说明；仅将官方语言列表描述为页面现行范围。 |
| 官方文档中的快速开始、组件、provider、link、CLI 和部署/阶段使用方式 | W-001–W-013、W-015 | `concepts/00-application-model.md`、`concepts/01-config-stage-state.md`、`concepts/02-cli-project-lifecycle.md`、`concepts/03-components-and-providers.md`、`concepts/05-resource-linking.md`、`examples/01-minimal-component-app.md`、`examples/02-link-resources-to-runtime.md`、`examples/03-local-development-and-deployment.md` | references 中登记本表所用的具体官方页面 URL 与采集日期；Monorepo 独立页曾返回 403，相关内容只引可访问的 Basics 与 CLI 页面。 |

## 最终源文档集合

### Concepts

| 文件 | 主要覆盖主题 |
|---|---|
| `concepts/00-application-model.md` | SST 定位、应用入口及阅读边界 |
| `concepts/01-config-stage-state.md` | 配置发现、App/Stage、官网 stage/state 使用说明 |
| `concepts/02-cli-project-lifecycle.md` | CLI 到项目执行、开发和部署命令主路径 |
| `concepts/03-components-and-providers.md` | 组件层级、命名空间和 provider 区分 |
| `concepts/04-runtime-server-architecture.md` | RPC、runtime、配置构建与平台入口 |
| `concepts/05-resource-linking.md` | Linkable、环境变量与 JS SDK 资源访问 |
| `concepts/06-live-mosaic-development.md` | Mosaic、事件流、部署触发及 Live 版本边界 |

### Examples

| 文件 | 最低验收内容 |
|---|---|
| `examples/01-minimal-component-app.md` | 固定源码配置骨架与官网 Bucket 组件写法；明确未执行安装、开发或部署。 |
| `examples/02-link-resources-to-runtime.md` | 展示 Bucket、Function `link` 与 JS SDK `Resource` 访问，并把产品用法和源码数据流分开。 |
| `examples/03-local-development-and-deployment.md` | 展示本地开发、差异查看、stage 部署命令顺序；说明凭证、云资源和未实测边界。 |

## 验收映射

- **FR-2 完整性**：表格中六项主题均有事实编号及一个或多个目标文档。
- **来源完整性**：每份正文在创建前均须有已经存在的 references 来源登记；新增概念不得只引用本矩阵。
- **示例覆盖**：至少三份示例，对应最小应用/组件、资源链接、本地开发到部署。
- **版本边界**：源码性结论只能依固定 commit；官网说明需同时保留 W 编号、具体 URL 与采集日期。
- **范围边界**：目录与索引不能宣称穷尽组件、provider 或 API；没有真实云端执行证据时不得标记部署成功。

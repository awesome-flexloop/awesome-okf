# 全局核心规则

本文件包含 awesome-okf-xs 文档库所有智能体必须遵守的基础规则。

## 1. 启动协议

所有任务必须严格遵循根目录 `AGENTS.md` 中的启动协议（步骤 1-4），包括：
- 步骤 1：读取 AGENTS.md 全文
- 步骤 2：按上下文路由表确定规范
- 步骤 3：按需读取对应规范（不要一次加载全部）
- 步骤 3.5：自检清单
- 步骤 4：执行任务

## 2. 内容敏感度分流

### 公开内容（Public）
- 公开发布的开源知识、官方文档、公开文章
- **工作流**：标准工作流，存放于 doc/bundles/ 或 doc/

### 私域内容（Private）
- 个人笔记、内部讨论、含访问控制的内容
- **工作流**：跳过公开规划，在用户指定目录执行
- 不确定时默认按私域处理或向用户确认

## 3. OKF 文档组织规范

- **bundle（知识束）**：结构化、有明确主题边界的知识文档，以 bundle 为单位组织，存放于 `doc/bundles/`
- **通用文档**：总览、索引、指南等，存放于 `docs/`
- **参考资料**：原始来源、外部资料、参考实现，存放于 `references/`
- 新增知识文档前，先确认其归属目录，避免内容分散
- **bundle 导航完整性**：每个 bundle 必须生成根 `index.md`，并以 `{toctree}` 引用该 bundle 的全部内容文档（含子目录 index，如 `concepts/index`、`concepts/00-introduction`）；被 toctree 引用为目录 index 的 `xxx/index.md` 必须存在，内容文档不得孤立于任何 toctree 链之外
- 新增/迁移 bundle 后运行 `python scripts/check-toctrees.py`（及 `--self-test`）验证零断链、零孤立内容；该脚本已接入 CI 作为构建前置门

## 4. 文档元数据（frontmatter）规范

所有 Markdown 文档采用 OKF v0.2 规定的 YAML frontmatter 作为唯一元数据来源（元数据内嵌，不引入外置元数据文件）：
- **唯一必填字段**：`type`
- **推荐字段**：`title`、`description`、`resource`、`tags`
- **可选家族**：`sources`（溯源）、`generated`/`verified`（信任）、`status`/`stale_after`（生命周期）
- 详细规范见 [rules/frontmatter.md](rules/frontmatter.md)

## 5. 三阶段递进工作法

处理问题时遵循三阶段递进：

1. **修复（Fix）**：先解决当前的具体问题
2. **预防（Prevent）**：分析问题根因，添加检查或文档避免再次发生
3. **闭环（Close）**：验证修复有效，必要时更新文档

不要过度设计，简单问题直接处理即可。

### 5.1 修复落地验证（修复即闭环的硬性要求）

修复完成后，**必须验证变更实际落地**，禁止仅凭过程描述自认为已完成：

- 用 `git diff` / `git status` 核对修改确实写入目标文件与提交
- 实际运行构建/测试命令验证效果（如 Sphinx 用 `sphinx-build -b dummy -E doc _build/dummy <文件>`）
- 上下文丢失或会话压缩后，若依赖摘要判断任务状态，必须先核实磁盘与 git 的真实状态

> 历史教训：曾因上下文丢失导致 `doc/conf.py` 修复逻辑未真正写入文件，构建仍崩溃，而任务被误报为"已完成并提交"。

## 6. 按需读取规范

- **不要**一次性读取 .agents/ 下所有规范文件
- 根据 `context-routing.md` 只读取与当前任务相关的规范
- 简单任务（如修改单个文档错别字）可只读取核心规则后直接执行

## 7. 其他基础规则

- **语言**：正文中文，文件名 kebab-case 纯英文
- **路径引用**：相对路径，禁止 file:/// 绝对路径
- **派生产物溯源**：源自外部的知识文档须标注 sources 字段
- **提交规范**：Conventional Commits，type(scope): subject，中文主体
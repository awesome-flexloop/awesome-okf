# 变更日志 —— Designer-RSI 程序记忆演化

## 2026-10-26 · 初始创建

### 1. 开工前幂等检查

- 目标目录 `jishu/ai/practice/designer-rsi-procedural-memory/` 不存在，按“新建”处理。
- 无同名 spec 目录；新建 `.trae/specs/designer-rsi-okf-wiki/`。
- 父级索引现有计数读取值：总 679 束 / 技术域 500 束 / ai 268 束 / practice 24 束；本束创建后分别为 680 / 501 / 269 / 25。

### 2. 信源获取

| 步骤 | 结果 |
|---|---|
| 微信文章 | browser 渲染后取 `#js_content`，正文 6,328 字；标题、账号「符智汇」、时间 2026-09-25 23:02 |
| 论文 abs | `https://arxiv.org/abs/2609.22086` 获取成功（200） |
| 论文全文 | `https://arxiv.org/html/2609.22086v1` 获取成功，约 120 KB；表 1–4、附录 C/D/E/F/G/H/I/K 逐项核对 |

### 3. 归属与骨架

- 归属：`jishu/ai/practice`，理由是该分类已容纳论文/方法论解读束，且本束无代码仓，不适合 frameworks。
- 骨架：`index + concepts/ + references/ + log`；不设 `examples/`（操作可复现性两问皆否）。
- 不新建分组（单篇博文禁止新建分组）。

### 4. 事实与核验

- F 编号 F-001–F-105，共 105 条；spec `facts.md` 与 bundle `references/article-source.md` 双份登记，表体逐字一致。
- P0 核验 17 组（C1–C17），全部通过。
- 勘误：
  - E-1 ⚠️ 源文称技能文件内含“规避计数”；论文附录 C.1 明确统计存放在文件外。
  - E-2 ⚠️ 源文称“计划中的小规模用户研究尚未完成”；论文只说未招募用户。
  - E-3 ⚠️ “内部 prompt 与轨迹没有公开”为合理推断；论文未提供公开数据/代码链接。
  - E-4 口径提示：+11.99 指 GenEval2 质量差，+7.70 指四基准平均质量差，不可混用。
  - E-5 源文省略项（触发阈值、tie band、工具面默认关闭、延迟与 token 对照），已按论文补全。

### 5. 生成顺序（信源先行）

1. `references/article-source.md`
2. `references/verification.md`
3. `references/glossary.md`
4. `concepts/00` → `concepts/07`
5. `concepts/index.md`、`references/index.md`
6. 根 `index.md`
7. 本 `log.md`

### 6. 对抗审查（四视角）

| 视角 | 检查 | 结果 |
|---|---|---|
| 事实溯源 | 正文数字是否都有 F 编号；是否有 F 之外的编造 | 通过；结果页所有数字可回查表 1–4 |
| 结构规范 | frontmatter 字段、toctree、目录层级 | 通过 |
| 读者可用性 | 相对链接逐一可达；学习路径是否闭环 | 通过 |
| 时效边界 | 单源声明、论文版本、价格/日期类信息 | 已设 `stale_after: 2027-03-31`；标注 v1 |

### 7. 机械门禁（依赖不可用时的等效验证）

| 检查 | 方法 | 结果 |
|---|---|---|
| UTF-8 严格 roundtrip | `UTF8Encoding(false,false)` 解码全部新增 .md | 通过 |
| 双份 F 编号一致 | 正则 `^\|\s*F-(\d{3})\s*\|` 提取两文件，集合比对 | 通过：105 = 105，F-001–F-105 连续 |
| 三级 toctree 完整 | 每个 index.md 含 toctree；条目逐一 `Test-Path` | 通过 |
| 相对链接可达 | 正则提取 Markdown 链接，逐一解析 | 通过 |
| 三级计数同步 | bundles/index.md、jishu/index.md、ai/index.md、practice/index.md | 已同步：680 / 501 / 269 / 25 |
| 敏感路径零残留 | 搜索家目录绝对路径与本地文件协议前缀 | 通过 |
| frontmatter 完整 | 10 个必填字段逐项检查 | 通过 |

> 本环境未安装 `invocations` 可选依赖，未运行 `invoke gates.*`；以上为手动等效验证，不声称“gates 通过”。

### 8. 后续复核

- 复核触发：arXiv 出现 v2；或 2027-03-31 到期。
- 复核重点：实验数字是否修订、是否补充人类用户研究、是否公开数据/代码。

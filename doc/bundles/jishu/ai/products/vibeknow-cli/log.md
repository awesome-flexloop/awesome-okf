# 变更日志（Log）

## 2026-10-21 · 初始生成（源码转化 R→I→E→V→C）

- **触发**：用户指定本地源码目录 `external/dao/flows/vibeknow/cli`，要求以七概念方法论生成 OKF v0.2 Wiki 教程至 `doc/bundles` 的恰当位置；方法论编排走七概念场景 4（知识沉淀 R→I→E→V→C）
- **信源稳定性（G0）**：`external/` 整体被主仓 `.gitignore` 忽略，属临时路径；已固定到不可变坐标——remote `git@github.com:vibeknow/cli.git`、tag `v0.9.2`、commit `93a26eca3383d480148c5cfd8da7995ee3352187`（2026-09-09 14:56:00 +0800 `chore(release): 0.9.2`）、仓库共 18 个 tag、工作树干净。**未使用 main/master 浮动引用**
- **公开性预检**：开源仓库（Go 源码 + 公开 tag），属公开内容 → 标准工作流，产出物入 `doc/bundles/jishu/ai/products/vibeknow-cli/`
- **归属判定**：按 `jishu/ai/products/` 域的既有分类（浏览器自动化、桌面工作台、创作工具等终端型 AI 产品），VibeKnow CLI 归入「AI 产品与终端工具」
- **事实登记**：F-001~F-104 连续 104 条，十四节分节（信源与形态 / 命令树与旗标 / 退出码与失败类型 / 付费授权门 / exit 6 三态 / 输出格式与事件 / 预览账本异步 / create 参数域 / preset 契约 / 字幕样式 / 批量清理 / 后端端点 / 统一快照 / AI Skill 资产）；每条标注仓库内相对路径与行号，数量陈述附统计口径
- **数量纪律**：所有数量由 4 个独立脚本产出（旗标 v2、命令树 v3、端点+i18n+行数 v4），经历四轮勘误（旗标正则首参限制、退出码常量定位、端点正则失配、命令树切分伪影），勘误过程写入 `references/source-facts.md` 的审计轨迹表
- **洞察产出**：5 条四元组洞察（退出码即契约 / 授权门两段式与载荷哈希 / 未知拆三态 / 三通道各司其职 / preset 只管长相与声音）+ 知识地图（4 分组 × 3 学习路径）+ E 阶段分批计划
- **文件**：24 个（root index + log + concepts 12 含 index + examples 4 含 index + references 6 含 index）
- **状态**：stable；`stale_after=2027-04-21`（v0.9.2 处于 0.9.x，退出码与旗标面仍在演进，给约半年窗口）
- **V 阶段机械门禁**：见本文件末尾「V 阶段门禁结果」段
- **边界声明**：全部内容来自 v0.9.2 源码与仓库自带 `AGENTS.md` / `skills/` 文档的静态阅读，**未连接后端实测**；examples 步骤未真机执行

## V 阶段门禁结果（2026-10-21）

### 内部校验（束内自建脚本，位于 spec 工作目录，不入库）

| 校验项 | 方法 | 结果 |
|--------|------|------|
| 标识符真实性 | 提取正文 `Ident`（大写开头）与 `funcName()` 候选，回信源 `git grep -w` 逐条核验 | 15 条待查全部为英文普通词、shell 变量或算法名，无虚假断言 |
| 数量断言复核 | 以**不同实现**（独立正则与遍历口径）复算 internal 包/行数、后端端点数、i18n 词条数、顶层命令数、分组子命令数 | 与 F-007/F-008/F-090~F-092 全部一致 |
| 相对链接 | 解析全部 Markdown 相对链接并验证目标存在 | 129 条全部可达 |
| toctree 覆盖 | 4 个 `index.md` 均含 `{toctree}`，全部内容文档均被登记 | 通过 |
| frontmatter | 解析 20 份 frontmatter，检查 `type` 必填、`okf_version` 未越位、`sources.resource` 必填、`generated.by` 必填 | 通过（`index.md`/`log.md` 按 OKF 规范豁免） |
| 敏感路径 | 匹配 `file:///[A-Za-z]`、`[A-Za-z]:\Users\`、`[A-Za-z]:\spaces\` | 零残留 |
| F 编号 | 登记 104 条连续无跳号；正文引用的 26 个编号全部已登记 | 通过 |

### 仓内交付门禁（awesome-okf-xs `scripts/`）

| 门禁 | 结果 |
|------|------|
| `check-bundles-index.py` | 通过——9 域 / 63 组 / 659 束，frontmatter、正文计数行、节标题、分组表、toctree 五面一致（本次同步 `doc/bundles/index.md`、`jishu/index.md`、`jishu/ai/index.md`、`jishu/ai/products/index.md` 共 4 处索引） |
| `check-toctrees.py` | 通过——全部 `index.md` 引用有效，所有内容文档均可达 |
| `check-utf8.py` | 通过——12015 个文件均为有效 UTF-8 |
| `sphinx-build -b dummy -E doc` | 退出码 0；本束 24 篇全部被读取并写出，**零 WARNING / 零 ERROR**（日志中残留 WARNING 均来自 `zhexue/first-principles`、`document/myst/myst-tutorial`、`wenxue/english-grammar` 等既有束，与本次变更无关） |

### G3 阶段纪律自检

- **信源先行**：`references/` 5 篇先于 `concepts/` 生成，事实底座（`references/source-facts.md`）先行落地
- **分批落盘**：每批 ≤7 篇（references → concepts 00~04 → 05~06 → 07~10 → examples → index/log）
- **索引最后写**：根 `index.md` 与 `log.md` 在全部内容文档完成后才生成


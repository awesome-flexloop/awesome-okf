# 更新日志

## 2026-10-15

- **新增 bundle**：在 `sheke/personal-growth/` 下创建 `wechat-anti-aging-er100-nmn`，来源为微信公众号「美因」2026-10-15 发布的抗衰老科普兼带货文（ER-100 基因疗法人体首针 + NMN 补充剂推广）。
- **信源先行（E 阶段）**：按 `references → concepts → index` 顺序生成。先生成 [博文事实清单](references/article-source.md) 与 [核验报告](references/verification.md)，再写 concepts×5 与 [知识地图](knowledge-map.md)，最后写各 index 与本日志。
- **事实登记**：F-001 ~ F-096 共 96 条，编号连续无跳号；与 spec 侧 `facts.md` 为**双份登记**，经正则 `^\|\s*F-(\d{3})` 提取两侧编号集合**相等且连续**（各 96 条）。（Review R1 修复时追加 F-075 ~ F-096 共 22 条，登记核验勘误的更正值与核验衍生值）四类来源标记：页面事实 / 作者观点 / 厂商自述 / 图片独有事实。
- **P0 核验**：41 条 P0 声明逐条独立检索权威来源，结果 **✅ 15 / ⚠️ 16 / ❌ 2 / single-source 6 / single-source/flagged 2**（覆盖率 100%）。零假核验：核验报告「已核验权威信源清单」40 条 URL（全文唯一 URL 41 条含博文）均为实际检索确认；检索不到者一律写「未检索到」。
- **勘误（13 条）**：勘-01 首例给药实为 2026-06-09（源文误作「3 月」）；勘-02「6–8 周 75%」缺物种/组织/读数三重限定词；勘-03「寿命近乎翻倍」判 ❌（权威 +7%~+8.5%）；勘-04 纯度口径不一致（以图 08「≥99%」呈现）；勘-05 图 04 引用编号错位；勘-06 2013 年研究被拔高；勘-07「Nature 子刊」应为 Cell Research；勘-08/09 文献 [4][6] 作者序列有误；勘-10「30 余年」应为「四十余年」；勘-11「全球首个」降为「率先之一」；勘-12 正文重复段；勘-13 共识题录补全为中华老年医学杂志 2026, 45(4): 497-508。
- **骨架判定（I 阶段）**：操作可复现性两问皆「否」（「三个选购标准」属选购判断，无固定输入—步骤—输出；无作者实测），**不设 `examples/`**；三层拆分 = concepts×5 + knowledge-map + references×2。
- **status 定档**：`flagged`——两项主推成效数字失实，符合「核心声明核验失败 → flagged」判据；`stale_after` 定为 **2027-06-30**。
- **索引接入状态（待后续任务）**：本 bundle 已落盘，但**尚未接入三级索引**——`sheke/personal-growth/index.md` 导航表加行 + toctree 追加 + 计数（14→15）、`sheke/index.md` 域束数（67→68）、`bundles/index.md` 的 `total_bundles`（635→636）**均待 V/C 阶段另行处理**，不在本次 T5 范围内（本次未修改任何既有索引文件，避免部分接入破坏全库计数一致性）。
- **机械门禁（官方脚本 + 手动等效验证）**：`invocations` 未安装，**未调用 `invoke gates.*`**，改以仓库官方检查脚本与手动等效验证清单双重取证，全程**不声称「gates 通过」**。
- **官方脚本实际执行记录**（工作目录 `projects/awesome-okf-xs/`，三条均退出码 0）：
  - `python scripts\check-utf8.py` → `UTF-8 检查通过: 11597 个文件均为有效 UTF-8。`
  - `python scripts\check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`
  - `python scripts\check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 61 组 / 636 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`
- **手动等效验证清单（8 项，逐项结论）**：
  - ① **UTF-8 strict roundtrip**：本 bundle 12 个 `.md` 均以严格 UTF-8 解码成功；全仓 `check-utf8.py` 亦通过 11597 个文件。**结论：通过**。
  - ② **双份 F 编号一致**：正则 `^\|\s*F-(\d{3})` 提取 spec `facts.md` 与 bundle `references/article-source.md` 两侧编号集合，**相等且连续**。**结论：一致**。
  - ③ **三级 toctree 完整可达**：`bundles/index.md` → `sheke/index.md` → `sheke/personal-growth/index.md` → 本束的链路，经 `check-toctrees.py` 自根 `index.md` 做 BFS，全库内容文档可达。**结论：通过**。
  - ④ **相对链接全可达**：逐一解析本 bundle 12 个文件的相对 Markdown 链接（共 **45 条**，排除 http/https、mailto 与纯锚点；较初版 42 条新增 3 条——R2-5 修复在 `concepts/00`、`concepts/04` 各新增 1 条，R4-B5 修复在 `concepts/01` 新增 1 条），解析路径全部命中实际文件。**结论：0 断链，通过**。
  - ⑤ **敏感路径与绝对路径零出现**：本 bundle 内检索**绝对路径协议字面量**、面向 Unix 与 Windows 的系统家目录路径关键字，命中数 = 0；禁止性引导文案关键词命中数 = 0。**结论：通过**。
  - ⑥ **frontmatter 齐备**：根 `index.md` 字段齐全；子索引 `concepts/index.md`、`references/index.md` 经本次修复补齐 `description`/`tags`/`generated`/`status`/`stale_after`/`sources`；`okf_version` 仍**仅出现在 bundle 根 `index.md`**。**结论：通过**。
  - ⑦ **勘误落实**：勘-01 ~ 勘-13 已登记于 `references/verification.md`，并以正确值或「源文口径 / 权威口径」对照形式落实于正文 `concepts/00`、`02`、`03`、`04`。**结论：落实**。
  - ⑧ **计数三处一致**：`check-bundles-index.py` 对账全库 636 束自洽；本束涉及的三处计数（`personal-growth/index.md` 15 束、`sheke/index.md` 68 束、`bundles/index.md` 636 束）表述一致。**结论：一致**。
- **未在本次完成**：四视角对抗审查记录（V 阶段）、三级索引接入与全库计数同步（V 阶段）、子模块与主仓库原子提交（C 阶段）。
- **三级索引接入与全库计数同步完成（后续任务 T7）**：`sheke/personal-growth/index.md` 导航表新增 `wechat-anti-aging-er100-nmn` 行（文档数 5+2，flagged）并追加隐藏 toctree 条目与阅读路径行，`total_bundles` 14→15；`sheke/index.md` 域内分组导航「个人成长与自我提升」束数 14→15 并补入本束说明，正文分组说明段落同步补入；`bundles/index.md` `total_bundles` 635→636、prose 全库计数与顶部 mermaid `sheke` 节点 67→68、sheke 段落标题 68 束、该分组行束数 15。`groups`(61) 与 `domains`(9) 不变；三处索引对个人成长束数（15）与 sheke 域束数（68）表述一致。
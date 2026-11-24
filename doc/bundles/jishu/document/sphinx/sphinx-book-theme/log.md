# sphinx-book-theme 知识包更新日志

## 2026-11-24

- 初始版本生成，覆盖本地源码快照 `1.5.0.dev`（最近正式版 `1.4.0`）
- 完成 9 篇概念文档：定位、安装、架构、布局、配置、页眉按钮、边注/margin、Notebook 交互、定制与子主题
- 完成 5 篇实战示例：书籍站点、仓库/启动按钮、边注与 CSS、Notebook 流水线、子主题与模板覆盖
- 完成 3 篇信源参考：源码路径映射、主题选项速查、版本与兼容性
- 完成 R/I 阶段工作稿：140 条源码事实、7 条架构洞察
- 覆盖范围：Python `setup()` 事件链、`theme.conf` 全选项、模板分层、SCSS/JS 资产管线、页眉按钮 URL 规则、脚注转边注变换、MyST-NB/Thebe 协作边界
- 已知边界：未实测上游 CI 与 Binder 构建；版本判断以本地 `pyproject.toml` 与 `__init__.py` 为准

## 2026-11-24（事实合并）

- 合并原 `myst/sphinx-book-theme` 知识包（2026-08-23 生成，源码事实采集口径）的独有事实：`spec/facts.md` 追加「补充事实」段，编号 F-141…F-185（共 45 条），覆盖旧包逐文件／逐函数粒度事实——`page_description` 160 字符算法、`_gen_hash` SHA-1 缓存、`DEFAULT_LOG_TYPE`、按钮 tooltip/icon 常量、JupyterHub `/hub/user-redirect/git-pull` URL、五平台图标路径、`index.js` 逐函数行为、SCSS 目录全枚举、翻译键 22 项全表
- 概念层并入 `concepts/08-customization-and-development.md`：新增「资产哈希与缓存清除」「与 Sphinx 扩展协作」「已弃用配置键」三节；重写「翻译」节（catalog 名 `booktheme`、locales 目录、22 键表、新增语言三步）
- 事实总数由 140 条增至 **185 条**（篇数不变，仍 9 概念 + 5 示例 + 3 信源）
- 未并入：旧包 `09-internationalization.md` 中 `pydata-sphinx-theme == 0.20.0` 的版本锁定断言（过时，本书主题实为 `0.23.0`）
- 删除重复知识包 `doc/bundles/jishu/document/myst/sphinx-book-theme/`（同项目在 `sphinx/` 下已有更新版本）

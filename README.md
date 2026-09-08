---
type: Reference
title: Awesome OKF for Xuanspace
sources:
  - id: xuanspace-readme
    resource: https://github.com/xinetzone/xuanspace
    title: XuanSpace（玄境）README 结构模板
  - id: bundles-index
    resource: doc/bundles/index.md
    title: 知识包总索引（规模数据单一真相源）
---

# Awesome OKF for Xuanspace

> 技术为器、思想为道，器以载道

![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green)
![OKF Version: 0.2](https://img.shields.io/badge/OKF-v0.2-blue)
![Bundles: 500+](https://img.shields.io/badge/Bundles-500%2B-orange)
![Domains: 9](https://img.shields.io/badge/Domains-9-purple)

## 这是什么

**awesome-okf-xs** 是 [XuanSpace（玄境）](https://github.com/xinetzone/xuanspace) 项目的**开源知识格式（Open Knowledge Format，OKF）文档库**。

它承载玄境项目"道"的一面——以 OKF bundle（知识包）为单元，系统化组织 **500+ 知识包、9 大学科域、57 个分组**的中文教程，涵盖开源项目源码解读与人文经典/自然科学/社会科学著作的结构化阅读指南；与承载"器"（代码与工具）的 xuanspace 正反向协同，共同实践"器以载道"的理念。

> 📊 规模数据以 [知识包总索引](doc/bundles/index.md) frontmatter 为单一真相源，当前实际值：**503 束 / 57 组 / 9 域**。

---

## 为什么用 OKF bundle（而非散文档）

普通 Markdown 文档堆的问题：**概念散、无信源、难迁移**。OKF 知识包用三层结构解决这三个痛点：

| 特性 | 说明 |
|------|------|
| 🧱 **三层结构化** | 每个 bundle 固定包含 `concepts/`（概念定义）→ `examples/`（实战示例）→ `references/`（信源溯源）三层，避免"只有代码没解释、只有结论没证据" |
| 🔗 **信源可追溯** | 所有事实陈述标注来源，关键概念经过双源/三源核对，不做无证据断言 |
| 🤖 **AI Agent 就绪** | 内置 `AGENTS.md` 与 `.agents/` 规范目录，每篇文档有 OKF frontmatter，AI 可按结构批量生成、校验与迁移知识 |
| 📦 **可迁移可复用** | bundle 是独立知识单元，跨仓库拷贝、按主题重组、增量同步均可直接操作 |
| 🌐 **Sphinx 一键发布** | 文档直接构建为 Read the Docs 在线站，支持搜索、索引、交叉引用与 Mermaid 图表 |

---

## 30 秒快速开始

### ① 在线阅读（推荐 · 零配置）

👉 **[📖 Read the Docs 文档站](https://awesome-okf-xs.readthedocs.io/)** — 直接浏览搜索，无需下载。

### ② 本地预览文档

```bash
# 前置：Python >= 3.14
pip install -e ".[doc]"

# 构建 HTML + 启动本地服务器预览
invoke build
invoke browse   # 自动打开浏览器预览
```

### ③ 本地开发 / 贡献

```bash
git clone git@github.com:awesome-flexloop/awesome-okf.git
cd awesome-okf

# 跑质量门（UTF-8 编码 + toctree 完整性 + 总索引计数对账）
invoke gates.all
```

### 🧭 你是谁？从这里开始

不同背景的读者，推荐不同入门路径（更详细见 [知识包总索引推荐入门](doc/bundles/index.md#推荐入门路径)）：

| 读者画像 | 推荐路径 | 为什么 |
|---------|---------|------|
| 📜 **人文爱好者** | [国学](doc/bundles/guoxue/index.md)（儒 → 道 → 易 → 阳明心学）→ [医学与养生](doc/bundles/yixue/index.md) → [科学元典](doc/bundles/kexue/index.md) | 从最经典的国学入门束开始，逐步打通医道互参、中西元典对读 |
| ⚙️ **技术开发者** | [OKF 规范](doc/bundles/meta/okf-spec/index.md) → [Python](doc/bundles/jishu/python/index.md) → [构建](doc/bundles/jishu/build/index.md) → [AI 生态](doc/bundles/jishu/ai/index.md) | 先搞懂知识包的格式规范，再按技术栈直接定位到需要的源码解读 |
| 🔄 **跨学科探索者** | [算学](doc/bundles/guoxue/suanxue/index.md) ↔ [数学](doc/bundles/kexue/math/index.md) · [道家](doc/bundles/guoxue/daojia/index.md) ↔ [道医](doc/bundles/yixue/daoyi/index.md) · [职场 OKR](doc/bundles/sheke/workplace/index.md) ↔ [思维方法论](doc/bundles/zhexue/methodology/index.md) | 中西对读、医道互参、理论与实践交叉，是这个库最有价值的打开方式 |

---

## 内容总览（9 大学科域）

按知识包束数降序排列（完整 503 束清单 → [知识包总索引](doc/bundles/index.md#九域分组导航)）：

| # | 学科域 | 束数 | 组数 | 代表内容 |
|:-:|--------|:---:|:---:|---------|
| 1 | ⚙️ **技术（jishu）** | 378 | 17 | AI & 大模型(171束) · 文档工程(110束) · 构建/通信/容器/ML/PyData/Rust/Web/GUI/IoT/自动驾驶 等 17 个技术生态 |
| 2 | 📜 **国学（guoxue）** | 46 | 15 | 儒道释法墨易 · 河洛 · 老子/庄子/鬼谷子/周易 · 法家 4 束 · 道家 19 束 · 阳明心学 5 束 · 算学 |
| 3 | 👥 **社会科学（sheke）** | 33 | 6 | 职场管理(7) · 亲密关系(6) · 性学(3) · 理财 · 营销 · **AI 行业趋势(15)** |
| 4 | 🔬 **科学（kexue）** | 17 | 3 | 中西化学经典对读(7) · 中西物理学经典(6) · 中外数学经典(4) |
| 5 | 🌿 **医学与养生（yixue）** | 10 | 6 | 中医经典 5 束 · 黄帝内经 · 道医 · 养生 · 房中 · 东亚医学 |
| 6 | 🎤 **艺术（yishu）** | 9 | 3 | 艺术疗愈 6 分支 · 声乐教学(咽音+手势) · 红歌教学 |
| 7 | 💭 **哲学（zhexue）** | 5 | 2 | Ψhē 自指递归理论体系(4) · 思维方法论(第一性原理等) |
| 8 | 📐 **规范与格式（meta）** | 3 | 3 | OKF v0.2 规范本体 · OKF 生态工具链 · OKF 桌面阅读器 |
| 9 | ✒️ **文学（wenxue）** | 2 | 2 | 中国古典文学（浮生六记等） · 英语语法学习 |
| **合计** | | **503** | **57** | 8 个学科域 + 1 个规范锚点 = **9 域** |

> ⚠️ 本表数据以 [doc/bundles/index.md](doc/bundles/index.md) frontmatter（`total_bundles` / `groups` / `domains`）为单一真相源。新增 / 删除 bundle 或分组后，请同步更新本表，或运行 `invoke gates.bundles` 校验计数一致性。

---

## 精选推荐（想先看这几篇试试）

| 知识包 | 域/组 | 一句话亮点 |
|--------|------|-----------|
| [OKF v0.2 规范本体](doc/bundles/meta/okf-spec/index.md) | 规范·格式 | 所有知识包的格式宪法——写包/读包之前先看这一本，含概念、示例、信源三层结构定义 |
| [王阳明心学 5 束合集](doc/bundles/guoxue/yangming/index.md) | 国学·阳明 | 《传习录》精读 + 心即理·知行合一·致良知·四句教 + 功夫论实践 + 生平年谱与弟子流派 |
| [AI & 大模型生态（171 束）](doc/bundles/jishu/ai/index.md) | 技术·AI | Trae / DeepSeek / Anthropic / Coze / 智谱 / 腾讯 NCNN / LangChain / 知乎 CLI 等 AI Agent 工具链源码教程 |
| [第一性原理方法论](doc/bundles/zhexue/methodology/index.md) | 哲学·方法论 | 可迁移的思维方法：哲学起源 → 物理学应用 → 商业创新案例 → 方法论框架 → 六步练习手册 |
| [AI 行业与商业趋势 15 束](doc/bundles/sheke/industry/index.md) | 社科·行业 | AI 变现指南 / Copilot 成本 / 国产大模型对比 / EMS 能源 / 硬件设计工具 / 监管治理 快照分析 |

---

## 构建与质量体系（给贡献者）

| 操作 | 命令 | 说明 |
|------|------|------|
| 构建 HTML 文档 | `invoke build` | Sphinx + MyST 构建，输出到 `_build/html/` |
| 本地预览 | `invoke browse` | 构建后启动 HTTP 服务自动打开 |
| 清理构建 | `invoke clean` | 移除 `_build/` |
| **跑全部质量门** | **`invoke gates.all`** | ✅ UTF-8 编码无 BOM · ✅ toctree 无断链/孤立文档 · ✅ 总索引计数对账（frontmatter/表格/toctree 五面一致） |
| 只查 toctree | `invoke gates.toctrees` | 新增/迁移 bundle 后必跑，防止断链 |
| 只查计数对账 | `invoke gates.bundles` | 新增/删除束或分组后必跑，防止数字失真 |
| 只查 UTF-8 | `invoke gates.utf8` | Windows 平台提交前注意 |

**技术栈**：Python >= 3.14 · Sphinx + MyST Parser · sphinx-book-theme · Invoke（任务系统） · GitHub Actions + Read the Docs 自动部署。

---

## 链接

- 📖 **在线文档**：[awesome-okf-xs.readthedocs.io](https://awesome-okf-xs.readthedocs.io/)
- 🏠 **基底项目（玄境代码）**：[xinetzone/xuanspace](https://github.com/xinetzone/xuanspace)（承载"器"的代码与工具）
- 💾 **本仓库**：[awesome-flexloop/awesome-okf](https://github.com/awesome-flexloop/awesome-okf)
- 🐛 **问题反馈**：[GitHub Issues](https://github.com/awesome-flexloop/awesome-okf/issues)
- 📚 **知识包完整索引**：[doc/bundles/index.md](doc/bundles/index.md)
- 📄 **许可证**：Apache License 2.0 — 详见 [LICENSE](LICENSE)

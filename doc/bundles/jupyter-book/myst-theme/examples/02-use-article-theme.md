---
type: example
title: "使用 Article 主题发布论文"
description: "使用 Article 主题创建学术论文，配置 frontmatter、导出 PDF 和多格式发布"
tags: [myst-theme, article-theme, academic-paper, pdf-export]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "themes/article/"
  - path: "packages/frontmatter/"
---

# 使用 Article 主题发布论文

本例演示如何使用 Article 主题创建一篇学术论文，配置丰富的 frontmatter，并导出为多种格式。

## 1. 创建项目

```bash
mkdir my-paper && cd my-paper
myst init
```

在 `myst.yml` 中选择 article 模板：

```yaml
version: 1
site:
  template: article-theme
  title: "基于 Transformer 的代码生成研究"
project:
  title: "基于 Transformer 的代码生成研究"
  authors:
    - name: 张三
      orcid: 0000-0000-0000-0000
      affiliations:
        - 某某大学计算机学院
    - name: 李四
      affiliations:
        - 某研究所
  date: 2026-08-23
  license: CC-BY-4.0
  open_access: true
  venue:
    title: 某某期刊
    volume: 42
    issue: 3
  bibliography: references.bib
  exports:
    - format: pdf
      template: arxiv
    - format: docx
    - format: tex
```

## 2. 编写论文（myst.yml + paper.md）

```markdown
---
title: 基于 Transformer 的代码生成研究
authors:
  - name: 张三
    orcid: 0000-0000-0000-0000
    corresponding: true
    email: zhangsan@example.edu
  - name: 李四
affiliations:
  - name: 某某大学计算机学院
    department: 人工智能实验室
    address: 北京市海淀区
funding:
  - name: 国家自然科学基金
    number: 6200000000
keywords:
  - 代码生成
  - Transformer
  - 深度学习
abstract: |
  本文提出了一种基于 Transformer 架构的代码生成方法...
---

# 引言

代码生成是软件工程领域的重要问题 [见 @smith2023; @lee2024]。

# 方法

## 模型架构

我们采用标准 Transformer encoder-decoder 架构 {eq:architecture}：

$$
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$ {#eq:architecture}

# 实验

实验在 CodeSearchNet 数据集上进行 {numref}`table:results`：

```{table} 实验结果
:name: table:results
| 模型 | BLEU | 准确率 |
|------|------|--------|
| Baseline | 24.5 | 67% |
| Ours | **28.3** | **74%** |
```

# 参考文献
```

## 3. 启动 Article 主题预览

```bash
myst start
```

浏览器打开后可以看到 Article 主题渲染的论文：
- 标题、作者、机构信息自动排版
- 摘要在标题下方突出显示
- 公式编号和交叉引用可点击
- 右侧（或顶部）有下载按钮

## 4. 多格式导出

```bash
# 导出 PDF（通过 LaTeX）
myst build --pdf

# 导出 DOCX（Word）
myst build --docx

# 导出 LaTeX 源码
myst build --tex

# 同时导出所有配置的格式
myst build
```

## 5. Article 主题的 frontmatter 渲染

Article 主题自动渲染以下 frontmatter 字段：

| 字段 | 渲染位置 | 说明 |
|------|---------|------|
| `title` | 页面顶部 | 大字号标题 |
| `authors` | 标题下方 | 作者名+ORCID图标+通讯标记 |
| `affiliations` | 作者下方 | 编号机构列表 |
| `date` | 作者旁边 | 发布日期 |
| `abstract` | 标题区域下方 | 摘要块 |
| `keywords` | 摘要下方 | 关键词标签 |
| `funding` | 正文末尾 | 资助信息 |
| `license` | 页脚 | 许可证徽章 |
| `exports` | 右上角 | 下载按钮组 |
| `venue` | 页眉 | 期刊/会议信息 |

## 6. 自定义 Article 样式

创建 `custom.css` 调整 Article 外观：

```css
:root {
  /* 论文衬线字体 */
  --myst-font-body: 'Source Serif Pro', Georgia, serif;
  --myst-font-heading: 'Source Sans Pro', sans-serif;
  --myst-content-max-width: 42rem;
}

/* 摘要块样式 */
.abstract-block {
  font-style: italic;
  border-left: 3px solid var(--myst-color-primary);
  padding-left: 1rem;
}
```

## 7. 部署

```bash
myst build --html
# 输出在 _build/ 目录，可部署到任意静态托管服务
```

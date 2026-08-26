---
type: Example
title: 创建带数学公式的 MDX 页面
description: 完整示例：如何在 3Blue1Brown.com 项目中创建一个包含 LaTeX 数学公式的 MDX 课程页面，包括 frontmatter 配置、正文写作、数学公式语法、自定义组件使用、本地预览全流程。
tags: [3blue1brown, mdx, math, latex, example, lesson, content, mathjax]
generated: { by: "source-code-to-okf-wiki/e-phase", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: 3Blue1Brown.com 源码事实采集
  - id: concepts-03
    resource: /concepts/03-mdx-content-system.md
    title: MDX 内容系统与数学渲染
related:
  - /concepts/03-mdx-content-system.md
  - /concepts/06-build-and-deploy.md
---

# 创建带数学公式的 MDX 页面

本示例将完整演示如何在 `content/lessons/` 目录下创建一个新的 MDX 课程页面，重点展示 **LaTeX 数学公式** 的行内和块级写法，以及如何配置 frontmatter、使用自定义组件、预览最终效果。MDX 允许你在 Markdown 中直接嵌入 React 组件和 JSX 语法，是 3Blue1Brown.com 课程内容的主要载体（F-028、F-029、F-116）。

## 前置条件

开始之前，请确保你已经：

1. 克隆了 3Blue1Brown.com 仓库到本地
2. 安装了 Bun（或 npm/pnpm）作为包管理器
3. 运行了 `bun install` 安装所有依赖
4. 了解基本的 Markdown 和 React 语法

## 第一步：创建课程目录和文件

课程页面按照**年份组织**在 `app/pages/lessons/` 目录下，每个课程是一个独立文件夹，主内容文件固定命名为 `index.mdx`（F-029）。

假设我们要创建一个 2026 年的新课程「微积分入门：导数的直观理解」，首先创建目录和文件：

```bash
# 创建课程目录
mkdir -p app/pages/lessons/2026/derivatives-intuition

# 创建主 MDX 文件
touch app/pages/lessons/2026/derivatives-intuition/index.mdx
```

目录结构应如下所示：

```
app/pages/lessons/
└── 2026/
    └── derivatives-intuition/
        └── index.mdx    ← 我们的新页面
```

> 💡 **命名规范**：目录名使用 kebab-case（小写字母、数字、连字符），这将作为课程的 URL 路径（`/lessons/derivatives-intuition`）。

## 第二步：编写 YAML Frontmatter

每个 MDX 文件必须以 **YAML frontmatter** 开头，包含课程元数据（F-116）。Frontmatter 被三短划线 `---` 包裹，项目通过 `remark-frontmatter` 和 `remark-mdx-frontmatter` 插件解析（F-009、F-037）。

在 `index.mdx` 开头添加以下内容：

```mdx
---
title: 微积分入门：导数的直观理解
description: 通过几何直观和动画演示理解导数的本质——不是神秘的极限运算，而是测量"瞬时变化率"的工具。
date: 2026-08-26
chapter: 1
video: dQw4w9WgXcQ
source: _2026/derivatives_intuition.py
credits:
  - "Manim animations by Grant Sanderson"
  - "Narration by Grant Sanderson"
  - "Editing by Team 3Blue1Brown"
image: $lesson/thumbnail.jpg
---
```

### Frontmatter 字段详解

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `title` | string | ✅ | 课程标题，显示在页面顶部和 SEO 标签中 |
| `description` | string | ✅ | 课程简短描述，用于 SEO 和课程列表卡片 |
| `date` | string | ✅ | 发布日期，格式 `YYYY-MM-DD`，自动解析为 Date 对象（F-089） |
| `chapter` | number | ❌ | 章序号，用于系列课程的排序和导航 |
| `video` | string | ❌ | YouTube 视频 ID，存在时页面顶部显示 YouTube 播放器（F-111） |
| `source` | string | ❌ | GitHub 上 Manim 源码路径，链接到源码 |
| `credits` | string[] | ❌ | 鸣谢/制作人员名单，格式 `"角色 by 姓名"`（F-088） |
| `image` | string | ❌ | 封面图片路径；无 video 时显示，`$lesson/` 前缀构建时替换为 GCP CDN 路径（F-035） |

### 自动派生字段

以下字段**不需要手动填写**，构建时由 `textReplacePlugin` 自动派生（F-035）：

- `readable`：内容长度是否超过 500 字符（长篇课程标记）
- `interactive`：内容是否包含 `<Interactive` 标签（交互课程标记）

## 第三步：导入可选自定义组件

MDX 允许你在文件顶部 import React 组件，在正文中以 JSX 方式使用（F-117）。如果需要使用 Figure、Question、PiCreature 等自定义组件，在 frontmatter 之后添加导入：

```mdx
---
# ... frontmatter 内容 ...
---

import Figure from "~/components/Figure";
import PiCreature from "~/components/PiCreature";
import LessonLink from "~/components/LessonLink";
import Question from "~/components/Question";
import FreeResponse from "~/components/FreeResponse";
```

常用组件说明：

| 组件 | 用途 |
|------|------|
| `Figure` | 图片/视频展示，支持 Image/Video 切换标签页（F-119） |
| `PiCreature` | 3Blue1Brown 标志性的 π 生物角色，带不同表情（F-121） |
| `LessonLink` | 课程之间的链接组件，自动带导航样式 |
| `Question` | 选择题/互动问题组件 |
| `FreeResponse` | 自由回答问题组件 |

> 💡 **提示**：如果页面不需要这些组件，可以完全省略 import 部分，直接写纯 Markdown 内容。

## 第四步：编写 MDX 正文（含数学公式）

现在开始编写正文内容。课程内容按 `<section>` 标签分段，每个 section 对应页面中的一个视觉区块，配合 striped 背景交替效果（F-110、F-118）。

以下是包含数学公式的完整示例：

```mdx
<section>

## 什么是导数？

当我们谈论"导数"时，很多人第一反应是繁琐的极限公式和求导法则。但在几何直观上，导数的概念非常简单：

> **导数测量的是"瞬时变化率"**。

想象你正在开车：
- 车速表显示的 **速度**，就是位置对时间的导数
- 踩油门时的 **加速度**，就是速度对时间的导数

在图像上，函数 $f(x)$ 在某一点的导数 $f'(x)$，就是该点处切线的**斜率**。

</section>

<section>

## 斜率：从割线到切线

我们都学过，两点 $(x_1, y_1)$ 和 $(x_2, y_2)$ 之间直线的斜率是：

$$
m = \frac{y_2 - y_1}{x_2 - x_1} = \frac{\Delta y}{\Delta x}
$$

这是**割线**的斜率——连接曲线上两个点的直线。当我们让这两个点越来越接近，即 $\Delta x \to 0$ 时，割线就变成了**切线**，这个极限就是导数：

$$
f'(x) = \lim_{\Delta x \to 0} \frac{f(x + \Delta x) - f(x)}{\Delta x}
$$

<PiCreature emotion="thinking" />

不要被极限符号吓到——它只是在说"让两点无限靠近"。这不是某种神秘的魔法，而是一个非常自然的过程：我们用越来越精确的"平均变化率"，去逼近那一瞬间的"瞬时变化率"。

</section>

<section>

## 一个具体的例子：$f(x) = x^2$

让我们用一个最简单的非线性函数来手动计算导数：$f(x) = x^2$。

把 $f(x) = x^2$ 代入导数的极限定义：

$$
\begin{align*}
f'(x) &= \lim_{h \to 0} \frac{f(x + h) - f(x)}{h} \\
&= \lim_{h \to 0} \frac{(x + h)^2 - x^2}{h} \\
&= \lim_{h \to 0} \frac{x^2 + 2xh + h^2 - x^2}{h} \\
&= \lim_{h \to 0} \frac{2xh + h^2}{h} \\
&= \lim_{h \to 0} (2x + h) \\
&= 2x
\end{align*}
$$

所以 $f(x) = x^2$ 的导数是 $f'(x) = 2x$！这意味着：
- 在 $x = 1$ 处，切线斜率是 $2$
- 在 $x = 3$ 处，切线斜率是 $6$
- 在 $x = 0$ 处，切线斜率是 $0$（顶点处是水平的）

</section>

<section>

## 使用 Figure 组件展示动画

使用 `Figure` 组件可以展示静态图片和 MP4 动画，自动提供切换标签（F-119）：

<Figure
  image="$lesson/figures/tangent-line.png"
  video="$lesson/clips/tangent-slope.mp4"
  caption="当Δx→0时，割线逐渐变为切线，斜率趋近于导数值"
/>

注意路径中的 `$lesson/` 前缀——构建时会被自动替换为 GCP 存储桶的完整 URL（F-035），你不需要关心完整 CDN 路径。

</section>

<section>

## 幂法则：求导的捷径

手动用极限计算导数太麻烦了，数学家已经总结出了一系列"求导法则"。最简单也是最常用的是**幂法则**：

$$
\frac{d}{dx} x^n = n x^{n-1}
$$

例子：
- $\frac{d}{dx} x^3 = 3x^2$
- $\frac{d}{dx} x^1 = 1x^0 = 1$（直线 $y=x$ 斜率恒为1）
- $\frac{d}{dx} x^0 = \frac{d}{dx} 1 = 0$（常数函数斜率为0）
- $\frac{d}{dx} \sqrt{x} = \frac{d}{dx} x^{1/2} = \frac{1}{2}x^{-1/2} = \frac{1}{2\sqrt{x}}$

<PiCreature emotion="happy" />

看到了吗？求导不需要死记硬背极限公式，掌握几个法则就能快速计算！

</section>

<section>

## 小测验

<Question>
问题：$f(x) = x^3$ 在 $x = 2$ 处的导数值是多少？

A. $4$
B. $6$
C. $8$
D. $12$

<details>
<summary>查看答案</summary>

根据幂法则，$f'(x) = 3x^2$。代入 $x = 2$：$f'(2) = 3 \times 2^2 = 12$。所以答案是 **D**。

</details>
</Question>

</section>
```

## 第五步：数学公式语法详解

项目使用 **MathJax** 渲染 LaTeX 数学公式，通过 `remark-math` 插件在构建时解析，客户端使用 MathJax 转换为 SVG（F-009、F-055~F-059）。

### 行内公式（Inline Math）

使用单个美元符号 `$...$` 包裹公式，公式嵌入在段落文本中：

```mdx
函数 $f(x)$ 在 $x = a$ 处的导数记为 $f'(a)$ 或 $\frac{df}{dx}(a)$。
```

效果：函数 $f(x)$ 在 $x = a$ 处的导数记为 $f'(a)$ 或 $\frac{df}{dx}(a)$。

> ⚠️ **注意**：`$` 符号两侧不要有空格。`$ x^2 $` 可能无法正确解析，应该写 `$x^2$`。

### 块级公式（Display Math）

使用双美元符号 `$$...$$` 包裹公式，公式单独成块居中显示：

```mdx
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

效果：
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

块级公式内部可以使用 `\\` 换行，使用 `align*` 环境做多行对齐计算（如上例中的导数推导）。

### 常用 LaTeX 数学符号

| 语法 | 效果 | 说明 |
|------|------|------|
| `$x^2$` | $x^2$ | 上标 |
| `$x_1$` | $x_1$ | 下标 |
| `$\frac{a}{b}$` | $\frac{a}{b}$ | 分数 |
| `$\sqrt{x}$` | $\sqrt{x}$ | 平方根 |
| `$\lim_{x \to 0}$` | $\lim_{x \to 0}$ | 极限 |
| `$\sum_{i=1}^{n}$` | $\sum_{i=1}^{n}$ | 求和 |
| `$\int_{a}^{b}$` | $\int_{a}^{b}$ | 积分 |
| `$\alpha, \beta, \gamma$` | $\alpha, \beta, \gamma$ | 希腊字母 |
| `$\leq, \geq, \neq$` | $\leq, \geq, \neq$ | 不等号 |
| `$\times, \cdot$` | $\times, \cdot$ | 乘号 |
| `$\vec{v}$` | $\vec{v}$ | 向量 |
| `$\hat{x}$` | $\hat{x}$ | 单位向量/估计值 |

### 多行对齐公式

使用 `align*` 环境做多行公式对齐，`&` 标记对齐位置：

```mdx
$$
\begin{align*}
e^{i\theta} &= \cos\theta + i\sin\theta \\
e^{i\pi} &= \cos\pi + i\sin\pi \\
&= -1 + 0 \\
&= -1
\end{align*}
$$
```

效果：
$$
\begin{align*}
e^{i\theta} &= \cos\theta + i\sin\theta \\
e^{i\pi} &= \cos\pi + i\sin\pi \\
&= -1 + 0 \\
&= -1
\end{align*}
$$

### 自定义宏

项目预定义了 `\degree` 宏表示角度符号（F-058）：

```mdx
$90\degree$ 角是直角。
```

效果：$90\degree$ 角是直角。

如果需要其他宏，可以在 MathJax 配置中扩展。

## 第六步：路由自动收集

你**不需要手动配置路由**！React Router 的 `prerender` 函数使用 `import.meta.glob` 自动扫描 `app/pages/lessons/20[0-9][0-9]/**/index.mdx` 模式的所有文件（F-040、F-090）：

```typescript
// react-router.config.ts 自动收集路由（F-040）
const lessonModules = import.meta.glob(
  "./app/pages/lessons/20[0-9][0-9]/**/index.mdx",
  { eager: true, query: "frontmatter-only" }
);
```

这意味着：
1. 新建的 `app/pages/lessons/2026/derivatives-intuition/index.mdx` 会被自动发现
2. 路由 `/lessons/derivatives-intuition` 自动生成
3. 构建时自动预渲染为静态 HTML
4. 课程列表页自动包含新课程
5. 自动写入 `tests/routes.json` 供 E2E 测试使用

目录名就是 URL 的最后一段——`derivatives-intuition` → `/lessons/derivatives-intuition`。

## 第七步：本地预览

保存文件后，启动开发服务器预览效果：

```bash
# 使用 Bun（推荐）
bun run dev

# 或使用 npm
npm run dev
```

开发服务器会在 `http://localhost:31415` 启动，并自动打开浏览器。访问以下地址查看你的新课程：

```
http://localhost:31415/lessons/derivatives-intuition
```

### 开发模式特性

- **HMR 热更新**：修改 MDX 文件后保存，浏览器自动刷新，无需手动刷新
- **React Refresh**：组件状态在修改后保持
- **快速 Source Map**：调试时直接定位到 MDX 源文件行号
- **未构建优化**：开发模式不压缩代码，构建更快

如果遇到数学公式不渲染或样式异常，检查：
1. 浏览器控制台是否有 JavaScript 错误
2. `$` 符号是否紧贴公式内容（无空格）
3. 块级公式 `$$` 是否单独占行
4. 组件 import 路径是否正确（使用 `~/` 前缀）

## 运行说明

### 完整工作流命令

```bash
# 1. 安装依赖（首次）
bun install

# 2. 启动开发服务器
bun run dev

# 3. 创建课程目录和文件
mkdir -p app/pages/lessons/2026/my-new-lesson
# 编辑 app/pages/lessons/2026/my-new-lesson/index.mdx

# 4. 访问预览
# 打开浏览器访问 http://localhost:31415/lessons/my-new-lesson

# 5. 类型检查（可选，提交前运行）
bun run typecheck

# 6. 生产构建（验证静态生成）
bun run build

# 7. 预览生产构建
bun run preview
# 访问 http://localhost:31415 验证构建产物
```

### 生产构建验证

提交前建议运行生产构建确保没有问题：

```bash
# 构建
bun run build

# 预览构建产物
bun run preview
```

构建产物位于 `build/client/lessons/derivatives-intuition/index.html`，可以直接用浏览器打开或部署到静态服务器。

## 预期效果

完成以上步骤后，你的课程页面将具备以下特性：

### 页面结构

1. **顶部视频区域**：如果配置了 `video` 字段，显示 YouTube 播放器，带静态缩略图懒加载（点击后才加载真实播放器）
2. **标题和元数据**：课程标题、发布日期、制作人员
3. **目录导航（TOC）**：页面右侧（宽屏时）自动生成所有 h2/h3 标题的目录，滚动时高亮当前章节（F-082、F-083）
4. **Striped 背景**：奇数 section 交替浅灰色背景，视觉层次清晰（F-110）
5. **前后导航**：底部显示上一课/下一课卡片导航
6. **赞助者区域**：如有 patrons.txt 文件，显示赞助者感谢区

### 数学公式渲染

1. **行内公式**：如 $f'(x) = 2x$ 嵌入在文本中，与文字基线对齐
2. **块级公式**：如导数极限定义、积分公式单独成块，居中显示
3. **SVG 输出**：MathJax 将公式渲染为高质量 SVG，缩放无模糊（F-059）
4. **暗色模式适配**：公式颜色自动适配暗色主题
5. **TOC 过滤**：目录中的数学公式正确渲染，不影响导航（F-060）

### 组件效果

- **PiCreature**：显示对应表情的 π 生物 SVG，融入文本流
- **Figure**：显示图片，带播放按钮切换到视频动画
- **Question**：选择题折叠显示答案，点击展开

### 响应式设计

- **手机**：单列布局，TOC 隐藏，视频全宽
- **平板**：较宽阅读区域，TOC 仍然隐藏
- **桌面**：主内容 + 右侧 TOC 双栏布局
- **宽屏**：更宽内容区域，最大内容宽度 70rem

### 静态预渲染

- 页面 HTML 在构建时已经生成，查看源代码可以看到完整的内容和数学公式文本
- 首屏加载极快，SEO 友好（搜索引擎能抓取完整内容）
- 禁用 JavaScript 时内容仍然可阅读（仅交互功能失效）

## 常见问题排查

### 问题 1：数学公式显示为原始 `$...$` 文本

可能原因：
- `$` 与公式内容之间有空格（如 `$ x^2 $` → 改为 `$x^2$`）
- 公式内有未转义的特殊字符
- 检查浏览器控制台是否有 MathJax 错误

### 问题 2：组件导入报错 "Cannot find module"

解决方案：使用 `~/` 绝对路径前缀：
```mdx
import Figure from "~/components/Figure";  // ✅ 正确
import Figure from "../../../components/Figure";  // ❌ 避免
```

### 问题 3：课程不出现在列表页

检查：
1. 文件路径是否匹配 `app/pages/lessons/20[0-9][0-9]/**/index.mdx` 模式
2. frontmatter 的 `date` 字段格式是否为 `YYYY-MM-DD`
3. 重启开发服务器（新增文件有时需要重启）
4. 运行 `bun run typecheck` 查看是否有类型错误

### 问题 4：`$lesson/` 路径图片不显示

开发模式下 `$lesson/` 前缀由 `textReplacePlugin` 处理，确保：
1. 文件是 `.mdx` 扩展名（插件只处理 MDX 文件）
2. 图片文件实际存在于课程目录下的 `figures/` 子目录
3. 生产构建（`bun run build`）后路径才会替换为 GCP CDN 路径，开发模式可能显示为相对路径

## 完整最小示例

如果你只需要一个最简单的 MDX 页面（无自定义组件），以下是最小可运行示例：

```mdx
---
title: 我的第一节课程
description: 这是一个最小的 MDX 课程页面示例
date: 2026-08-26
---

# 我的第一节课程

欢迎来到我的第一节课！

这是行内公式：$E = mc^2$。

这是块级公式：

$$
e^{i\pi} + 1 = 0
$$

这里可以写任意 Markdown 内容，包括**粗体**、*斜体*、[链接](https://www.3blue1brown.com)、列表等。

## 第一小节

内容...

## 第二小节

更多内容...
```

将此内容保存为 `app/pages/lessons/2026/my-first-lesson/index.mdx`，访问 `http://localhost:31415/lessons/my-first-lesson` 即可看到效果。

## 相关概念

- [03 MDX 内容系统与数学渲染](/concepts/03-mdx-content-system.md) — MDX 插件链、frontmatter 解析、MathJax 渲染机制、课程数据加载
- [02 路由系统与页面组织](/concepts/02-routing-and-pages.md) — React Router 路由配置、动态路由、预渲染
- [04 核心组件与状态管理](/concepts/04-components-and-state.md) — PiCreature、Figure、TableOfContents、Heading 等组件详解
- [06 构建系统、包管理与静态部署](/concepts/06-build-and-deploy.md) — Vite 构建配置、插件链、SSG 预渲染

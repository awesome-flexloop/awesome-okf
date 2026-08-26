---
type: Example
title: checkpoint_paste 交互式开发流程
description: 从零开始演示checkpoint_paste完整工作流：写最小骨架→运行进入交互→逐段粘贴代码调试→embed()断点调试，掌握Manim动画快速迭代的核心开发范式，让视觉创意获得即时反馈。
tags: [workflow, checkpoint-paste, interactive, embed, development, sublime, manimgl, debugging, 3blue1brown]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: Videos 源码事实采集
  - id: concepts-04
    resource: /concepts/04-checkpoint-paste-workflow.md
    title: checkpoint_paste 交互式开发工作流
  - id: manim-examples-basic-shapes
    resource: /viz/3b1b/manim/examples/basic-shapes.md
    title: ManimGL 基础图形绘制示例
---

# checkpoint_paste 交互式开发流程

> ⚠️ **编辑器说明**：checkpoint_paste 最初是为 Sublime Text 设计的工作流（F-011、F-054），videos 仓库内置了 Sublime 插件提供一键粘贴快捷键。如果你使用 VS Code、PyCharm 或其他编辑器，**不需要专门的插件**——直接使用 `self.embed()` 进入 iPython 断点，手动复制粘贴代码即可获得完全相同的交互式开发体验。本文会同时演示两种方式。

传统动画开发流程是"写完整代码→运行→等渲染→看结果→关窗口→改代码→重新运行"，一个10秒的动画可能需要几十次迭代，每次等待几十秒到几分钟，创作心流被完全打断。checkpoint_paste 交互式开发把这个循环压缩到"写一小段→按键/粘贴→**即时**看效果"，反馈延迟从分钟级降到秒级。

本示例将从零开始，一步步带你完成一个简单动画的交互式开发全过程。

## 准备工作：理解核心概念

在开始之前，先理解交互式开发的三个核心工具：

| 工具 | 作用 | 使用场景 |
|------|------|---------|
| `manimgl -se <line>` | 命令行参数，跳过动画并在指定行 embed | 快速跳到某个状态开始调试 |
| `self.embed()` | 代码中断点，执行到这里进入 iPython | 明确知道要在哪停下调试 |
| `checkpoint_paste()` | iPython 中执行剪贴板代码，保留场景状态 | Sublime 插件自动调用，手动也可用 |
| `-p` 标志 | preview 低分辨率预览 | 开发时始终加 `-p` 加速反馈 |
| `-w` 标志 | write 写入视频文件 | 最终渲染成品时才用 |

## Step-by-Step 教程：做一个"勾股定理"小动画

我们将交互式开发一个展示勾股定理的简单动画：显示直角三角形→标注三边→显示公式 `a² + b² = c²`。

### Step 1：写最小 Scene 骨架，加 embed() 断点

首先，在编辑器中新建一个文件 `pythagoras.py`，只写最基础的结构和第一行代码，**故意不写完**，在你想开始调试的地方加上 `self.embed()`：

```python
from manimlib import *

class PythagorasTheorem(Scene):
    def construct(self):
        # 设置标题
        title = TexText("Pythagorean Theorem")
        title.scale(1.2)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # 🛑 在这里设断点——后面的还没写，我们边粘边写
        self.embed()
```

> 💡 **为什么先写这么少？** 因为交互式开发的核心是"一段一段地加"，而不是"写完再跑"。先写确定的开头，然后停下来交互地添加后面的元素。

### Step 2：启动 Manim 进入交互模式

打开终端，运行（注意加 `-p` 低分辨率预览）：

```bash
manimgl pythagoras.py PythagorasTheorem -p
```

你会看到：
1. Manim 打开预览窗口，播放标题写入动画
2. 标题停在屏幕上方后，**终端自动进入 iPython 交互环境**
3. 窗口保持打开，场景状态保留（title 还在屏幕上）

现在你已经进入"活的场景"了——接下来不需要关窗口，直接在编辑器里写代码粘贴过来就行。

### Step 3：交互式创建三角形

现在你想加一个直角三角形，但不确定：
- 三角形放多大合适？
- 放在屏幕什么位置？
- 用什么颜色？

**不要猜——直接在编辑器里写一小段试：**

```python
# 在编辑器里写这段，选中并复制
triangle = Polygon(
    ORIGIN,
    RIGHT * 3,
    UP * 2,
)
triangle.set_stroke(BLUE, width=4)
self.play(ShowCreation(triangle))
self.wait()
```

**操作：**
- 如果用 Sublime+插件：选中代码，按 `Ctrl+B`（ManimCheckpointPaste 快捷键）
- 如果用其他编辑器：复制这段代码，回到终端的 iPython 窗口，直接粘贴按回车

你会**立刻**看到窗口中三角形被画出来了。

**观察后调整**：嗯，这个三角形有点高，2个单位的高让它看起来有点"瘦"，改成 `UP * 1.8` 试试。另外颜色用 BLUE_C 比纯 BLUE 更柔和。

在编辑器里修改，复制粘贴（或按快捷键）：

```python
# 调整后
triangle = Polygon(
    ORIGIN,
    RIGHT * 3,
    UP * 1.8,
)
triangle.set_stroke(BLUE_C, width=4)
self.play(ShowCreation(triangle))
```

等等——你会发现屏幕上出现了**两个**三角形！因为场景状态是保留的，之前的三角形还在。这时候有两个选择：

1. **快速重来**：关闭窗口，重新运行 `manimgl pythagoras.py PythagorasTheorem -p`，再粘调整后的代码（因为开头只有标题，重跑很快）
2. **手动清理**：在 iPython 里输入 `self.remove(triangle)` 删掉旧的（但新的变量名和旧的冲突，新手建议直接重跑）

> 💡 **开发技巧**：早期迭代阶段，觉得效果不对直接关窗口重跑就行——因为开头代码很短，重跑一次只要1-2秒。等场景复杂了再用 `force_skipping()` 跳转（后面会讲）。

### Step 4：添加直角标记

三角形位置大小满意了，继续在编辑器里写下一段——添加直角的小方块标记：

```python
# 直角标记
right_angle = Square(side_length=0.3)
right_angle.set_stroke(WHITE, width=2)
right_angle.move_to(ORIGIN)
right_angle.shift(RIGHT * 0.15 + UP * 0.15)
self.play(ShowCreation(right_angle))
self.wait()
```

复制粘贴（或快捷键）。直角标记位置可能需要微调——`shift` 的数值改几次，每次粘一下看效果，直到标记正好在直角位置。

### Step 5：标注三边长度 a, b, c

继续添加边的标签。先写第一段试：

```python
# 边 a（底边）
a_label = Tex("a", color=YELLOW)
a_label.next_to(triangle, DOWN)
self.play(Write(a_label))
```

粘过来看看——位置对吗？如果太近或太远，调 `buff` 参数：

```python
a_label = Tex("a", color=YELLOW)
a_label.next_to(triangle, DOWN, buff=0.3)
self.play(Write(a_label))
```

满意后继续加另外两个标签：

```python
# 边 b（左边竖边）
b_label = Tex("b", color=RED)
b_label.next_to(triangle, LEFT, buff=0.3)
self.play(Write(b_label))

# 边 c（斜边）
c_label = Tex("c", color=GREEN)
# 斜边标签要放在斜边旁边，需要手动计算位置
c_label.move_to(triangle.get_center() + UR * 0.3)
self.play(Write(c_label))
self.wait()
```

每次粘一段，看效果，不满意就改了再粘。

### Step 6：添加公式

最后加勾股定理公式。先写：

```python
formula = Tex(R"a^2 + b^2 = c^2", t2c={
    "a": YELLOW,
    "b": RED,
    "c": GREEN,
})
formula.scale(1.5)
formula.to_edge(DOWN)
self.play(Write(formula))
self.wait(2)
```

用 `t2c`（tex_to_color_map）让公式中的 a, b, c 和边标签颜色一致（F-060）。位置用 `to_edge(DOWN)` 放在屏幕底部。如果觉得离三角形太远或太近，调 `shift` 或者不用 `to_edge` 直接 `next_to`。

### Step 7：把满意的代码粘回源文件

等每一段都调满意了，关掉 Manim 窗口（在 iPython 里按 `Ctrl+D` 两次退出，或直接关窗口）。现在把你试好的代码按顺序粘贴回 `construct()` 方法里，**替换掉 `self.embed()`**：

```python
from manimlib import *

class PythagorasTheorem(Scene):
    def construct(self):
        title = TexText("Pythagorean Theorem")
        title.scale(1.2)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # 三角形（已经调好的参数）
        triangle = Polygon(
            ORIGIN,
            RIGHT * 3,
            UP * 1.8,
        )
        triangle.set_stroke(BLUE_C, width=4)
        self.play(ShowCreation(triangle))

        # 直角标记
        right_angle = Square(side_length=0.3)
        right_angle.set_stroke(WHITE, width=2)
        right_angle.move_to(ORIGIN)
        right_angle.shift(RIGHT * 0.15 + UP * 0.15)
        self.play(ShowCreation(right_angle))

        # 边标签
        a_label = Tex("a", color=YELLOW)
        a_label.next_to(triangle, DOWN, buff=0.3)
        self.play(Write(a_label))

        b_label = Tex("b", color=RED)
        b_label.next_to(triangle, LEFT, buff=0.3)
        self.play(Write(b_label))

        c_label = Tex("c", color=GREEN)
        c_label.move_to(triangle.get_center() + UR * 0.3)
        self.play(Write(c_label))
        self.wait()

        # 公式
        formula = Tex(R"a^2 + b^2 = c^2", t2c={
            "a": YELLOW,
            "b": RED,
            "c": GREEN,
        })
        formula.scale(1.5)
        formula.to_edge(DOWN)
        self.play(Write(formula))
        self.wait(2)
```

### Step 8：完整预览

现在代码完整了，正常运行看完整效果：

```bash
manimgl pythagoras.py PythagorasTheorem -p
```

如果一切满意，就可以渲染最终版本：

```bash
manimgl pythagoras.py PythagorasTheorem -w --hd
```

## 进阶：用 -se 快速跳转到指定位置

当你的场景变复杂（比如有50秒动画，你在调第40秒的部分），每次重跑都等前面40秒播完就太浪费时间了。这时候用 `-se <line_number>` 命令行参数：

```bash
# 跳过所有动画，瞬间执行到第20行，然后进入embed
manimgl pythagoras.py PythagorasTheorem -se 20 -p
```

`-se` 是两个标志的组合：
- `-s` = skip_animations：跳过所有动画，瞬间执行（零运行时间）
- `-e <line>` = embed：在第 N 行进入 iPython 交互模式（F-055）

执行后：
1. Manim 瞬间"跑"完前20行（不播放动画，直接应用最终状态）
2. 窗口显示第20行执行完后的画面
3. 进入 iPython，你可以从这里开始粘贴调试后面的代码

这比加 `self.embed()` 更灵活——你不需要改代码就能在任意行进入交互模式。

## 进阶：force_skipping() 快速跳转

在老的 videos 仓库代码中你会经常看到 `force_skipping()` 成对出现（F-051），这是另一种跳过前面动画的方式，直接写在代码里：

```python
def long_scene(self):
    # 前面有100行动画...
    self.show_title()
    self.draw_triangle()
    self.show_labels()

    self.force_skipping()  # 🔴 从这里开始跳过

    # 这中间的50行动画会瞬间执行，不播放
    self.show_first_proof()
    self.show_second_proof()
    self.animate_formula()

    self.revert_to_original_skipping_status()  # 🟢 恢复播放

    # 🎯 你正在调试的部分——这里的动画正常播放
    self.play(circle.animate.set_fill(BLUE, 0.5))
    self.wait()
```

用法：
1. 把你正在调试的段落之前的代码用 `force_skipping()` 包起来
2. 每次重跑直接跳到你工作的位置
3. 调试完一段后，把这对标记往下移，继续调下一段
4. **最终录制成品前，记得删掉所有 force_skipping 调用**

## embed() 中的实用调试技巧

在 iPython 交互环境中，除了粘贴代码，还有几个非常实用的小技巧：

### 1. 查看当前场景有哪些 mobject

```python
# 在iPython中输入
self.mobjects
```

会列出当前场景上的所有 Mobject，帮你确认哪些东西已经加上了。

### 2. 手动移除某个 mobject

```python
# 移除之前加错的东西
self.remove(bad_mobject)
```

### 3. 直接修改属性看效果

```python
# 把三角形改成红色，立刻看到变化
triangle.set_color(RED)
self.wait()  # 刷新画面
```

### 4. 访问相机控制

```python
# 缩放视角
self.camera.frame.scale(0.8)
self.wait()
```

### 5. 退出交互继续执行

在 iPython 中按两次 `Ctrl+D`（或输入 `exit`），会退出 embed，继续执行后面的代码。

## 实用快捷键与命令速查

### 命令行常用组合

| 命令 | 用途 |
|------|------|
| `manimgl file.py SceneName -p` | 开发时最常用：低分辨率预览 |
| `manimgl file.py SceneName -se 42 -p` | 跳到第42行进入交互，低分辨率 |
| `manimgl file.py SceneName -w` | 渲染写入视频文件（默认4K） |
| `manimgl file.py SceneName -w --hd` | 渲染1080p视频 |
| `manimgl file.py SceneName -w -i` | 渲染GIF动图 |
| `manimgl file.py SceneName -l` | 渲染480p低分辨率，最快速度 |

### iPython 交互中的操作

| 操作 | 效果 |
|------|------|
| 粘贴代码 + 回车 | 执行粘贴的代码（手动版checkpoint_paste） |
| `checkpoint_paste()` | 执行剪贴板中的代码（需要Sublime插件配合） |
| `checkpoint_paste(skip=True)` | 跳过动画瞬间执行剪贴板代码 |
| `self.embed()` | 代码中设置断点，运行到这里进入交互 |
| `Ctrl+D` 两次 | 退出iPython，继续执行后面的代码 |
| `self.wait()` | 在交互中刷新画面，显示当前状态 |

### 预览窗口交互

| 操作 | 效果 |
|------|------|
| 鼠标左键拖拽 | 平移视角 |
| 滚轮 | 缩放 |
| 右键拖拽 | 旋转视角（3D场景） |
| `f` 键 | 切换全屏 |
| `r` 键 | 重置视角 |
| `q` 键 | 关闭窗口 |

## 与传统开发流程的对比

让我们用一个表格总结交互式开发相比传统流程的优势：

| 环节 | 传统"写完再跑" | checkpoint_paste 交互式 |
|------|---------------|------------------------|
| **第一次看到效果** | 写完整个场景 → 运行 → 等渲染（可能几分钟） | 写完第一段（3-5行）→ 运行 → 立刻看到 |
| **调整一个位置参数** | 改代码 → 关窗口 → 重运行 → 等渲染（几十秒） | 改参数 → 粘贴 → 1-2秒看到新效果 |
| **调整颜色** | 同上，等完整重跑 | 改颜色 → 粘贴 → 立刻看 |
| **场景状态** | 每次重跑从头开始 | 所有mobject都保留，不需要从头创建 |
| **创作心流** | 频繁被等待打断，忘记"感觉对不对" | 视觉思考连续，眼睛直接参与迭代 |
| **适合阶段** | 逻辑确定后的最终代码录制 | 视觉创意探索、参数微调、动画节奏调整 |

> 💡 **关键心态转变**：不要试图"一次性写对"。动画制作是视觉创作，90%的工作是"稍微往左一点"、"颜色再浅一点"、"动画慢0.2秒"这类微调。checkpoint_paste 就是为这种高频微调设计的——**让你的眼睛而不是大脑来判断效果**。

## 常见问题与注意事项

### Q: 我用 VS Code/PyCharm，没有 Sublime 插件怎么办？

A: 完全没问题。插件只是帮你省了"Ctrl+C → 切到终端 → Ctrl+V"的动作。手动复制粘贴效果完全一样。真正重要的是 `-se`/`embed()` + 保持场景运行这个**工作流理念**，而不是某个编辑器的快捷键。

### Q: 粘贴代码后出现两个相同的 mobject 怎么办？

A: 这是因为场景状态保留，你之前粘贴创建的 mobject 还在。解决方法：
1. 早期简单场景：直接关窗口重跑（反正很快）
2. 复杂场景：在 iPython 里 `self.remove(old_mobject)` 后再粘贴
3. 或者用 `checkpoint_paste(skip=True)` 先快速重建状态

### Q: 我能在 embed() 里定义新函数吗？

A: iPython 支持定义函数，但建议把可复用的函数写回源文件里，只在交互中做测试。

### Q: 最终代码里要保留 self.embed() 吗？

A: 不要。`self.embed()` 只是开发调试用的断点，最终渲染成品前记得删掉所有 `embed()` 调用，否则渲染到那里会停下等待输入。

## 运行说明

1. 将上述教程中的代码骨架保存为 `pythagoras.py`
2. 按 Step 2 启动交互模式：

```bash
manimgl pythagoras.py PythagorasTheorem -p
```

3. 按教程步骤逐段在编辑器中写代码、复制到 iPython 中执行
4. 满意后将代码粘贴回源文件，移除 `self.embed()`
5. 完整预览：

```bash
manimgl pythagoras.py PythagorasTheorem -p
```

## 预期效果

按照本教程完成交互式开发后，你将掌握：

1. **工作流层面**：不再"写完再跑"，而是习惯"一小段一粘贴"的快速迭代模式
2. **技能层面**：熟练使用 `-se`、`self.embed()`、`-p` 等交互式开发工具
3. **心态层面**：接受"视觉参数需要眼睛来调，无法预先想对"这个事实，不再纠结于第一次就写对参数

最终动画效果：
- 屏幕上方显示标题 "Pythagorean Theorem"
- 蓝色三角形被绘制出来，左下角有白色直角标记
- 三条边分别标注黄色的 a、红色的 b、绿色的 c
- 屏幕底部出现彩色公式 `a² + b² = c²`，字母颜色与边标签对应
- 所有元素位置协调，颜色搭配舒适——这些都是你交互式"调"出来的，而不是凭空猜的

## 相关概念

- [04 checkpoint_paste 交互式开发工作流](/concepts/04-checkpoint-paste-workflow.md) — checkpoint_paste三种模式、force_skipping跳转、Sublime集成、工作流原理
- [03 视频Scene代码结构与叙事模式](/concepts/03-video-structure-pattern.md) — construct()分段子方法、多继承组合、generate_target()动画模式
- [ManimGL：基础图形绘制](/viz/3b1b/manim/examples/basic-shapes.md) — Polygon、颜色、ShowCreation等基础API用法

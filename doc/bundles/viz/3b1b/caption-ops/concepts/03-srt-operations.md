---
type: Concept
title: SRT字幕操作
description: caption-ops 的 SRT 操作模块包含三个核心文件：srt_ops.py 负责 SRT 读写与智能分段、retime_srt.py 提供命令行时间偏移工具、sentence_timings.py 实现词级到句级时间映射的 Levenshtein 模糊对齐算法，是连接转录结果与最终可用字幕的关键桥梁。
tags: [caption-ops, srt, subtitles, timestamps, levenshtein, segmentation, alignment, fuzzy-matching]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: caption-ops 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: caption-ops 源码架构洞察
---

# SRT字幕操作

SRT（SubRip Subtitle）是视频字幕最通用的文本格式，几乎所有视频平台和播放器都支持。caption-ops 的 SRT 操作模块不是简单的 SRT 读写工具，而是包含一整套从词级时间戳到可读字幕的处理管线：词级→句级模糊对齐、标点优先智能分段、线性插值时间映射、时间轴偏移调整等，解决了自动转录字幕最常见的问题（分段不合理、时间不准、不同语言长度差异导致排版问题）。

本模块由三个核心文件组成，覆盖事实 F-042~F-054：
- `srt_ops.py`：SRT 格式化、读写、智能分段算法（F-042~F-047）
- `retime_srt.py`：独立命令行工具，SRT 时间戳整体偏移（F-048~F-049）
- `sentence_timings.py`：词级时间戳到句级时间的模糊对齐（F-050~F-054）

## SRT 格式基础

SRT 是一种简单的纯文本格式，结构如下：

```srt
1
00:00:00,000 --> 00:00:03,200
Today I want to talk about linear algebra,

2
00:00:03,200 --> 00:00:07,100
which is the branch of mathematics
concerning vectors and matrices.
```

每条字幕包含四个部分：
1. **序号**：从 1 开始递增的数字
2. **时间轴**：`开始时间 --> 结束时间`，格式为 `HH:MM:SS,mmm`（小时:分钟:秒,毫秒），毫秒用逗号分隔（不是点）
3. **字幕文本**：一行或多行文本，每行建议不超过一定字符数
4. **空行**：分隔不同字幕条目

SRT 文件使用 UTF-8 编码，这是多语言字幕正确显示的基础（F-046）。

## srt_ops.py 核心功能

`srt_ops.py` 是 SRT 操作的核心模块，基于 `pysrt` 库实现 SRT 文件读写，同时提供了时间格式化、智能分段等 caption-ops 特有的功能（F-042）。

### 时间格式化与解析

SRT 使用特殊的时间格式 `HH:MM:SS,mmm`，需要在秒数（浮点数）和这种格式之间互相转换。

#### format_time：秒数→SRT时间

`format_time(seconds)` 将浮点数秒数转换为 SRT 标准时间字符串（F-043）：

```python
from datetime import timedelta

def format_time(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

示例：
- `format_time(0.0)` → `"00:00:00,000"`
- `format_time(3.2)` → `"00:00:03,200"`
- `format_time(67.5)` → `"00:01:07,500"`
- `format_time(3661.123)` → `"01:01:01,123"`

#### unformat_time：SRT时间→秒数

`unformat_time(timestamp)` 反向解析，将 SRT 时间字符串转换为浮点数秒数，同时做格式校验（必须有 2 个冒号，最多 1 个逗号）（F-044）。

#### sub_rip_time_to_seconds：pysrt对象转换

`sub_rip_time_to_seconds(sub_rip_time)` 将 pysrt 库的 `SubRipTime` 对象转换为秒数，用于从现有 SRT 文件读取时间（F-045）。

### SRT 写入

`write_srt(segments, file_name)` 是基础的 SRT 写入函数，接收 `[(text, start_seconds, end_seconds), ...]` 格式的分段列表，通过 pysrt 创建 `SubRipItem` 并保存为 UTF-8 编码的 SRT 文件（F-046）：

```python
import pysrt

def write_srt(segments, file_name):
    subs = pysrt.SubRipFile()
    for i, (text, start, end) in enumerate(segments, start=1):
        sub = pysrt.SubRipItem(
            index=i,
            start=pysrt.SubRipTime(seconds=start),
            end=pysrt.SubRipTime(seconds=end),
            text=text
        )
        subs.append(sub)
    subs.save(file_name, encoding="utf-8")
```

这个函数直接按给定的分段写入，不做任何智能处理。真正的核心是下一节介绍的智能分段函数。

### 标点优先智能分段算法

`write_srt_from_sentences_and_time_ranges()` 是整个 SRT 模块最核心的函数，实现了 caption-ops 特有的智能分段逻辑（F-047，洞察 I-01）。

为什么需要智能分段？因为自然句子可能很长（尤其是德语、俄语等语言），直接把一整句作为一条字幕会导致：
- 一行文字太长，观众来不及读完
- 某些视频播放器自动换行位置不合理
- 翻译后句子长度变化，英文刚好的分段翻译到中文可能太长或太短

智能分段的目标是：在保证语义连贯的前提下，将长句切割为适合阅读的短分段，同时正确计算每个分段的时间戳。

#### 分段策略优先级

算法按以下优先级寻找切割点（F-047）：

1. **标点优先**：优先在句号、逗号、冒号、分号、中文标点等位置切割（F-006 `PUNCTUATION_PATTERN`）
2. **空格次之**：没有合适标点时，在单词之间的空格处切割
3. **硬切兜底**：对于中文/日文/韩文等没有空格的字符型语言，或连写的长单词，直接按字符数硬切
4. **字符数限制**：每个分段不超过 `max_chars_per_segment`（默认非中日韩 90 字符，中日韩 30 字符）

这种"标点优先"策略保证了切割后的字幕在语义上是完整的短语，不会在一个单词或一个意群中间断开。

#### 线性插值时间映射

切割句子文本后，需要计算每个子分段的开始和结束时间。这里不能简单平均分配时间，因为句子中不同部分的朗读速度是不同的。caption-ops 使用**线性插值（linear interpolation）**计算切割点时间（F-009、F-047）：

```python
from helpers import interpolate

# 假设原句从 start 到 end，长度为 total_chars 字符
# 切割点在字符位置 cut_pos，则该点时间为：
cut_time = interpolate(start, end, cut_pos / total_chars)
```

`interpolate(start, end, alpha)` 函数定义在 `helpers.py` 中（F-009）：

```python
def interpolate(start, end, alpha):
    return (1 - alpha) * start + alpha * end
```

其中 `alpha` 是 0~1 之间的比例因子：
- `alpha=0` → 句子开始时间
- `alpha=1` → 句子结束时间
- `alpha=0.5` → 句子中间时间

虽然朗读速度不是绝对均匀的，但线性插值对于字幕用途已经足够准确，且计算简单高效——这又是一个务实的工程选择。

#### 时间防重叠处理

分段完成后，算法还会对所有分段的 `starts` 和 `ends` 数组排序，防止出现时间重叠或顺序颠倒的情况（F-047）。

### 智能分段函数完整流程

`write_srt_from_sentences_and_time_ranges()` 的完整流程如下（F-047）：

```
输入：sentences（句子文本列表）、time_ranges（[(start, end), ...]）、max_chars_per_segment
输出：写入SRT文件

1. 初始化结果分段列表
2. 对每个句子 (sentence, (start, end))：
   a. 如果句子长度 ≤ max_chars_per_segment：直接作为一个分段
   b. 否则：
      i. 在句子中查找所有标点位置，按优先级排序
      ii. 查找所有空格位置作为备选
      iii. 从左到右，在不超过 max_chars_per_segment 的前提下，
           选择最靠右的合适切割点（标点 > 空格 > 硬切）
      iv. 对每个切割点使用线性插值计算时间
      v. 递归处理剩余部分直到句子结束
3. 收集所有分段，按开始时间排序
4. 检查并修复时间重叠
5. 调用 write_srt() 写入文件
```

#### 不同语言的字符数限制

中日韩（CJK）字符是方块字，每个字占据的视觉空间和阅读时间与拼音文字的字母不同。caption-ops 对不同语言使用不同的 `max_chars_per_segment`：
- 中文、日文、韩文：**30 字符/段**（每个字信息密度高）
- 英文、法文、德文等拼音文字：**90 字符/段**（F-039、F-047）

这是字幕制作的行业经验值，在屏幕上显示时既有足够信息量，又不会让观众来不及读完。

## retime_srt.py：时间轴调整命令行工具

`retime_srt.py` 是一个完全独立的命令行工具，只做一件事：**将整个 SRT 文件的时间戳向前或向后偏移指定秒数**（F-048、F-049）。

这是一个非常实用的小工具，典型使用场景：
- 下载的字幕时间轴整体偏早/偏晚几秒
- 视频开头剪掉了一段，需要把字幕整体后移
- 不同版本的视频（如剪辑版 vs 完整版）字幕时间需要整体调整
- 音画不同步时微调字幕时间

### 实现原理

时间偏移的核心逻辑很简单：解析每一行时间戳，加上或减去偏移秒数，然后格式化回去（F-048）：

```python
import re
from datetime import datetime

def parse_time(time_str):
    """解析 %H:%M:%S,%f 格式为 datetime 对象"""
    return datetime.strptime(time_str, "%H:%M:%S,%f")

def format_time(dt):
    """格式化为 SRT 时间字符串"""
    return dt.strftime("%H:%M:%S,%f")[:-3]  # 微秒取前3位作为毫秒

def shift_timestamps(line, seconds):
    """将时间戳行偏移指定秒数，禁止负时间"""
    time_pattern = r"(\d{2}:\d{2}:\d{2},\d{3})"
    times = re.findall(time_pattern, line)
    for t in times:
        original = parse_time(t)
        shifted = parse_time(t)
        shifted = shifted.replace(
            hour=shifted.hour,
            minute=shifted.minute,
            second=shifted.second
        )
        # 计算总秒数偏移
        total = (original - datetime(1900, 1, 1)).total_seconds() - seconds
        if total < 0:
            total = 0  # 禁止负时间
        # ... 重新格式化
    return line
```

注意一个细节：**禁止负时间戳**——如果偏移后时间小于 0，直接钳位到 0.0，避免生成无效的 SRT（F-048）。

### 命令行用法

`retime_srt.py` 使用 argparse 解析命令行参数，接受三个位置参数（F-049）：

```bash
# 用法：python retime_srt.py <输入文件> <输出文件> <偏移秒数>
# 将 input.srt 的时间轴整体回退（提前）2.5秒，保存为 output.srt
python retime_srt.py input.srt output.srt 2.5

# 注意：seconds 参数是"回退"秒数
# 如果要让字幕延后出现，使用负数？（看实际实现）
```

参数说明：
- `input_file`：原始 SRT 文件路径
- `output_file`：输出 SRT 文件路径
- `seconds`：偏移秒数（正浮点数），时间戳向前回退指定秒数

这个工具独立于 caption-ops 其他模块，不需要任何 API 密钥，也不依赖其他文件，可以单独复制出来使用——这是 Unix 哲学"每个工具做一件事"的典型体现（洞察 I-04）。

## sentence_timings.py：句子时间对齐

`sentence_timings.py` 实现了 caption-ops 最巧妙的算法之一：**基于 Levenshtein 编辑距离的模糊对齐，将词级时间戳映射到句级时间戳**（F-050~F-054，洞察 I-03）。

这是解决"Whisper 分段不对应自然句子"问题的关键。

### 为什么需要模糊对齐？

回顾转录模块：我们拿到的是词级时间戳——每个词的开始/结束时间（F-027）。要得到句子时间，直觉的做法是：
1. 把所有词拼接成完整文本
2. 按标点分割成句子
3. 在全文中查找句子的精确位置，映射回词索引
4. 取句子第一个词的开始时间和最后一个词的结束时间

但**精确字符串匹配在这里行不通**，因为（洞察 I-03）：
- Whisper 输出的词可能带有空格、标点附着问题（如 `"algebra,"` 带逗号）
- 按标点分割句子时，标点可能被分到前一句或后一句，导致不匹配
- 人工修正 `transcript.txt` 后，文本与原始词序列可能有微小差异
- 大小写、空格数量不一致

精确匹配会经常失败，而模糊匹配利用编辑距离可以容忍这些微小差异。

### Levenshtein 编辑距离

Levenshtein 距离（编辑距离）是衡量两个字符串差异的指标：将一个字符串变成另一个所需的最少单字符编辑（插入、删除、替换）次数。距离越小，两个字符串越相似。

`helpers.py` 中的 `nearest_string()` 函数基于 Levenshtein 距离查找最接近的匹配（F-012）：

```python
import Levenshtein

def nearest_string(src, trg_list):
    """返回目标列表中与 src 编辑距离最小的字符串和距离"""
    best_dist = float("inf")
    best_str = None
    for trg in trg_list:
        dist = Levenshtein.distance(src, trg)
        if dist < best_dist:
            best_dist = dist
            best_str = trg
    return best_str, best_dist
```

### 核心模糊对齐算法

`find_closest_aligning_substring_indices()` 是模糊对齐的核心实现（F-051，洞察 I-03）：

```python
def find_closest_aligning_substring_indices(
    full_text,
    sentences,
    max_shift=300,
    radius=20,
    sentence_end_bias=2
):
    """
    在 full_text 中滑动窗口查找 sentences 中每个句子的起止位置
    返回句子边界索引列表
    
    参数：
    - max_shift: 滑动窗口最大偏移字符数（默认300）
    - radius: 搜索半径（默认20）
    - sentence_end_bias: 句末标点位置的偏置加成（默认2）
    """
```

算法关键设计（洞察 I-03）：
1. **滑动窗口搜索**：不是在全文中盲目搜索，而是在上一个句子结束位置附近 `max_shift` 窗口内搜索，避免错位匹配
2. **句末标点偏置**：匹配到句末标点（`.!?。！？` 等）位置时，编辑距离额外减去 `sentence_end_bias`，利用"句末标点位置通常是准确的"这一先验知识，大幅提升对齐准确率
3. **搜索半径**：在预期位置前后 `radius` 字符范围内搜索，平衡准确率和性能

这三个参数的默认值（`max_shift=300`、`radius=20`、`sentence_end_bias=2`）是经过实践调优的，适用于绝大多数教育视频场景。

### 词级→句级时间映射完整流程

`get_sentence_timings()` 函数实现了从词级时间戳到句级时间的完整映射（F-052）：

```
输入：words_with_timings（[[word, start, end], ...]）、sentences（句子文本列表）
输出：句子时间范围列表 [(start, end), ...]

1. 构建词索引映射：
   a. 遍历所有词，累积字符长度，记录每个词在全文中的起始/结束字符位置
   b. 得到两个数组：word_starts（每个词第一个字符的位置）、word_ends（最后一个字符位置）

2. 拼接全文：将所有词用空格连接成 full_text

3. 模糊对齐句子边界：
   a. 调用 find_closest_aligning_substring_indices() 在 full_text 中
      查找每个句子的 start_idx 和 end_idx

4. 映射回词时间：
   a. 对句子开始位置 start_idx：在 word_starts 中找到第一个 >= start_idx 的词，
      取该词的 start 时间
   b. 对句子结束位置 end_idx：在 word_ends 中找到最后一个 <= end_idx 的词，
      取该词的 end 时间
   c. 如果找不到（极端情况），退化为最近的词时间

5. 返回 (sentences, time_ranges)
```

`get_sentences_with_timings()` 是一个便捷封装函数，自动完成"拼接单词→按标点分句→获取时间范围"的完整流程（F-053），一行代码调用即可从词级时间得到句级时间。

### 从现有 SRT 反推时间戳

`get_substring_timings_from_srt()` 函数支持从已有的 SRT 文件反推句子时间戳（F-054）。这在以下场景很有用：
- 你有一个社区贡献的旧 SRT，想基于它重新生成翻译
- 想从人工调整过时间轴的 SRT 恢复时间数据
- 合并多个 SRT 分段为完整句子时（`split_at_segments=False` 参数）

## 常见 SRT 操作

除了模块内置的功能，以下是字幕制作中常见的操作，结合 caption-ops 的工具可以方便实现。

### 合并 SRT 分段

如果你的 SRT 分段太碎（比如 Whisper 直接输出的），可以使用 `get_substring_timings_from_srt(srt_file, split_at_segments=False)` 按句末标点合并分段，再重新智能分段。

### 分割长 SRT

如果某些分段太长，直接调用 `write_srt_from_sentences_and_time_ranges()` 并设置更小的 `max_chars_per_segment` 重新分段即可。

### 时间轴整体偏移

使用 `retime_srt.py` 命令行工具，如前所述。

### 调整播放速度对应时间轴

如果你调整了视频播放速度（如 1.25 倍速），需要相应调整字幕时间轴。虽然 caption-ops 没有直接提供这个功能，但很容易实现：将所有时间戳乘以速度因子即可（1.25倍速 → 时间戳 × 0.8）。

### 双字幕合并

如果你想制作双语字幕（如中英对照），可以读取两个语言的 SRT，按时间轴对齐合并到同一行（如 `"中文句子\nEnglish sentence"`）。caption-ops 没有内置这个功能，但基于 pysrt 很容易实现。

## 命令行用法与 Python API 示例

### 示例 1：使用 retime_srt.py 调整时间轴

```bash
# 将字幕整体提前 1.5 秒
python retime_srt.py captions.srt captions_fixed.srt 1.5

# 批量调整多个文件
for f in *.srt; do
  python retime_srt.py "$f" "fixed_$f" 0.8
done
```

### 示例 2：从词级时间生成 SRT

```python
from helpers import json_load
from sentence_timings import get_sentences_with_timings
from srt_ops import write_srt_from_sentences_and_time_ranges

# 读取词级时间戳
words_with_timings = json_load("word_timings.json")

# 获取句子和时间范围
sentences, time_ranges = get_sentences_with_timings(words_with_timings)

# 生成智能分段的 SRT（英文每行最多 90 字符）
write_srt_from_sentences_and_time_ranges(
    sentences,
    time_ranges,
    "captions.srt",
    max_chars_per_segment=90
)

# 生成中文 SRT（每行最多 30 字符）
write_srt_from_sentences_and_time_ranges(
    chinese_sentences,
    time_ranges,  # 时间轴与英文相同！
    "chinese/captions.srt",
    max_chars_per_segment=30
)
```

注意一个重要细节：**所有语言的字幕共享同一个时间轴**——时间轴只基于英文语音计算，翻译后的文本复用相同的时间范围。这是因为时间轴对应语音的起止，与语言无关；翻译只是把同样时间段内的英文替换成其他语言。

### 示例 3：从现有 SRT 提取句子时间

```python
from sentence_timings import get_substring_timings_from_srt

# 从旧 SRT 文件读取句子和时间
sentences, time_ranges = get_substring_timings_from_srt(
    "old_community_captions.srt",
    split_at_segments=False  # 按句末标点合并分段
)

# 用新的翻译重新生成 SRT
write_srt_from_sentences_and_time_ranges(
    new_translations,
    time_ranges,
    "new_captions.srt",
    max_chars_per_segment=30
)
```

### 示例 4：自定义分段参数

```python
# 更短的分段（适合快速阅读或小屏幕）
write_srt_from_sentences_and_time_ranges(
    sentences, time_ranges, "short_lines.srt",
    max_chars_per_segment=60  # 英文每行 60 字符
)

# 更长的分段（适合大字幕或慢节奏视频）
write_srt_from_sentences_and_time_ranges(
    sentences, time_ranges, "long_lines.srt",
    max_chars_per_segment=120
)
```

## 相关概念

- [00 caption-ops 工具集总览](/concepts/00-caption-ops-overview.md)
- [01 音频转录模块](/concepts/01-transcription.md)
- [02 多语言翻译模块](/concepts/02-translation.md)
- [04 端到端字幕工作流](/concepts/04-pipeline-workflow.md)
- [CLI 脚本参考](/references/scripts-reference.md)

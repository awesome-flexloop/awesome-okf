---
type: Example
title: 带 Python 脚本的 Skill 示例
description: 以 daily-hot-news 为参考，演示如何创建一个集成 Python 脚本的脚本辅助型 Skill，包括脚本编写、SKILL.md 指令编排和命令行参数设计。
tags: [trae-skills, example, python-script, daily-hot-news, fetch_news]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 示例目标

参考 daily-hot-news 的模式，创建一个 `weather-report` 脚本辅助型技能，功能是获取指定城市的天气信息并生成格式化报告。

## 目录结构

```
skills/weather-report/
├── SKILL.md
└── resources/
    └── scripts/
        └── fetch_weather.py
```

## 步骤 1：编写 Python 脚本

创建 `resources/scripts/fetch_weather.py`：

```python
#!/usr/bin/env python3
"""天气数据获取脚本 - 仅使用 Python 标准库"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# 数据源配置（参考 daily-hot-news 的多层降级模式）
DATA_SOURCES = [
    {
        "name": "wttr.in",
        "url": "https://wttr.in/{city}?format=j1",
        "parser": "wttr"
    }
]

def fetch_weather(city: str) -> dict:
    """获取天气数据，支持数据源降级"""
    for source in DATA_SOURCES:
        try:
            url = source["url"].format(city=urllib.parse.quote(city))
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return parse_wttr(data, city)
        except Exception as e:
            print(f"[WARN] {source['name']} 请求失败: {e}", file=sys.stderr)
            continue
    return {"error": "所有数据源均不可用", "city": city}

def parse_wttr(data: dict, city: str) -> dict:
    """解析 wttr.in 返回的数据"""
    current = data.get("current_condition", [{}])[0]
    weather = data.get("weather", [{}])[0]
    return {
        "city": city,
        "temperature": current.get("temp_C", "N/A"),
        "feels_like": current.get("FeelsLikeC", "N/A"),
        "humidity": current.get("humidity", "N/A"),
        "weather_desc": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
        "wind_speed": current.get("windspeedKmph", "N/A"),
        "max_temp": weather.get("maxtempC", "N/A"),
        "min_temp": weather.get("mintempC", "N/A"),
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def format_markdown(result: dict) -> str:
    """格式化为 Markdown 报告"""
    if "error" in result:
        return f"# ⚠️ 天气获取失败\n\n{result['error']}"
    return f"""# 🌤️ {result['city']} 天气报告

> 更新时间：{result['fetch_time']}

| 指标 | 数值 |
|------|------|
| 天气 | {result['weather_desc']} |
| 当前温度 | {result['temperature']}°C |
| 体感温度 | {result['feels_like']}°C |
| 今日最高 | {result['max_temp']}°C |
| 今日最低 | {result['min_temp']}°C |
| 湿度 | {result['humidity']}% |
| 风速 | {result['wind_speed']} km/h |
"""

def main():
    parser = argparse.ArgumentParser(description="获取天气信息")
    parser.add_argument("city", help="城市名称，如 北京、Shanghai")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown",
                        help="输出格式（默认 markdown）")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    result = fetch_weather(args.city)
    output = json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" \
        else format_markdown(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已写入 {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
```

### 脚本设计要点（参考 daily-hot-news 模式）

1. **标准库优先**：使用 `urllib`、`json`、`argparse`，无需 pip install
2. **数据源降级**：`DATA_SOURCES` 列表支持多层降级容错
3. **命令行参数**：位置参数 `city` + 可选参数 `--format`、`--output`
4. **结构化输出**：JSON 用于程序处理，Markdown 用于直接展示
5. **默认值合理**：`--format` 默认 markdown，`--output` 默认 stdout

## 步骤 2：编写 SKILL.md

```markdown
---
name: weather-report
description: 查询城市天气信息并生成格式化天气报告。当用户问"天气""今天天气怎么样""XX市天气""气温"或需要获取天气数据时触发。支持中文城市名和英文城市名，输出 Markdown 格式天气报告。不适用于天气预报（仅当天）或历史天气查询。
---

# Weather Report

## Description

天气查询技能，获取指定城市的当前天气信息并生成格式化的 Markdown 报告。使用 wttr.in 作为数据源。

## Usage Scenario

**触发关键词：**
- "天气"、"今天天气怎么样"、"XX市天气"
- "气温"、"温度"、"湿度"
- "出门要不要带伞"

**不适用场景：**
- 未来多天天气预报（仅提供当天天气）
- 历史天气数据查询
- 空气质量（AQI）查询

## Instructions

1. **确认城市**：从用户输入中提取城市名称；如果未明确，询问用户要查询哪个城市
2. **执行脚本**：运行以下命令获取天气数据：
   ```bash
   python skills/weather-report/resources/scripts/fetch_weather.py "<城市名>"
   ```
3. **输出报告**：脚本直接输出 Markdown 格式的天气报告，直接呈现给用户即可
4. **异常处理**：如果脚本返回错误，告知用户天气服务暂时不可用，建议稍后重试

## Examples

用户输入："北京天气怎么样"
执行命令：`python skills/weather-report/resources/scripts/fetch_weather.py "北京"`
输出：Markdown 格式天气报告表格
```

## 步骤 3：本地测试

```bash
# 直接测试脚本
python skills/weather-report/resources/scripts/fetch_weather.py "北京"

# 测试 JSON 输出
python skills/weather-report/resources/scripts/fetch_weather.py "Shanghai" --format json

# 测试文件输出
python skills/weather-report/resources/scripts/fetch_weather.py "深圳" --output weather.md
```

## 步骤 4：安装并验证

```bash
# 安装到项目级
mkdir -p .trae/skills
cp -r skills/weather-report .trae/skills/
```

在 TRAE 中测试：
1. 新开会话
2. 说"北京天气怎么样"
3. 验证 Agent 执行脚本并返回天气报告
4. 说"帮我写个排序算法"（验证不会误触发）

## 与 daily-hot-news 的对比

| 设计要素 | daily-hot-news | weather-report（示例） |
|----------|---------------|----------------------|
| 脚本位置 | `resources/scripts/fetch_news.py` | `resources/scripts/fetch_weather.py` |
| 数据源数量 | 4 层降级 | 1 层（可扩展） |
| 输出格式 | Markdown 表格 + emoji | Markdown 表格 |
| 命令行参数 | --platforms/--top/--format/--output | city/--format/--output |
| 脚本依赖 | 标准库 | 标准库 |
| 报告生成 | 独立 generate_report.py | 脚本内置 format 函数 |

## 关键经验

1. **脚本入口明确**：SKILL.md 中给出可直接复制的完整命令
2. **参数有默认值**：减少 Agent 的决策负担
3. **错误处理**：脚本异常时 SKILL.md 指导如何反馈给用户
4. **标准库优先**：零依赖是最好的用户体验
5. **输出格式化在脚本中完成**：Agent 不需要做额外的数据转换

## 相关概念

- [脚本辅助型技能](/concepts/04-script-assisted-skills.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)
- [创建第一个 Skill](/examples/create-first-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)

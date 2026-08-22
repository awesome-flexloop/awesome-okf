---
type: Example
title: 变更日志生成
description: 使用github-activity生成Release Notes、配置Token、CI集成和自定义分类的完整示例
tags: [github, activity, changelog, example, release-notes, ci]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:12:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# 变更日志生成

## 基本Release Notes生成

### 为指定标签范围生成

```bash
# 假设你刚发布了v0.2.0，生成从v0.1.0到v0.2.0的changelog
github-activity executablebooks/jupyter-cache \
  --since v0.1.0 \
  --until v0.2.0 \
  --auth $GITHUB_TOKEN \
  --output CHANGELOG_v0.2.0.md
```

### 自动检测标签

在git仓库目录中，自动使用上一个标签到HEAD：

```bash
cd /path/to/your/repo
git tag v1.0.0
git push --tags

# 自动从最近的tag到HEAD
github-activity --auth $GITHUB_TOKEN --output CHANGELOG.md
```

## GitHub Actions自动生成Release Notes

```yaml
# .github/workflows/release.yml
name: Generate Changelog

on:
  release:
    types: [published]

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 获取完整历史以检测标签

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install github-activity
        run: pip install github-activity

      - name: Generate changelog
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # 获取上一个tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
          CURR_TAG=${GITHUB_REF#refs/tags/}

          if [ -n "$PREV_TAG" ]; then
            github-activity ${{ github.repository }} \
              --since $PREV_TAG \
              --until $CURR_TAG \
              --output release_notes.md
          else
            github-activity ${{ github.repository }} \
              --until $CURR_TAG \
              --output release_notes.md
          fi

      - name: Upload release notes
        uses: softprops/action-gh-release@v1
        with:
          body_path: release_notes.md
```

## 生成项目周报

```bash
#!/bin/bash
# weekly-report.sh
SINCE=$(date -d "7 days ago" +%Y-%m-%d)
UNTIL=$(date +%Y-%m-%d)
REPO="executablebooks/jupyter-cache"

echo "# Weekly Report ($SINCE to $UNTIL)" > weekly_report.md
echo "" >> weekly_report.md

github-activity $REPO \
  --since $SINCE \
  --until $UNTIL \
  --kind both \
  --auth $GITHUB_TOKEN \
  >> weekly_report.md
```

运行：

```bash
chmod +x weekly-report.sh
./weekly-report.sh
```

## Python API生成自定义格式

```python
"""生成自定义格式的变更日志"""
from github_activity import get_activity
import pandas as pd

# 获取活动数据
df = get_activity(
    "executablebooks/jupyter-cache",
    since="2024-01-01",
    auth="your_token"
)

# 按作者统计贡献
by_author = df.groupby("author").size().sort_values(ascending=False)
print("## 贡献者\n")
for author, count in by_author.items():
    print(f"- @{author}: {count} 个PR")

# 按分类统计
by_category = df.groupby("category").size()
print("\n## 分类统计\n")
for cat, count in by_category.items():
    print(f"- {cat}: {count}")

# 生成Markdown
from github_activity import generate_activity_markdown
md = generate_activity_markdown(df)
with open("CHANGELOG.md", "w") as f:
    f.write("# Changelog\n\n")
    f.write(md)
```

## 自定义分类配置

创建 `changelog_tags.json`：

```json
{
  "security": {
    "tags": ["security", "vulnerability"],
    "pre": ["SEC", "SECURITY"],
    "description": "🔒 Security Fixes"
  },
  "performance": {
    "tags": ["performance", "perf"],
    "pre": ["PERF"],
    "description": "⚡ Performance Improvements"
  },
  "feature": {
    "tags": ["feature", "new"],
    "pre": ["FEAT", "NEW"],
    "description": "✨ New Features"
  },
  "fix": {
    "tags": ["bug", "bugfix"],
    "pre": ["FIX", "BUG"],
    "description": "🐛 Bug Fixes"
  },
  "docs": {
    "tags": ["documentation", "docs"],
    "pre": ["DOC", "DOCS"],
    "description": "📝 Documentation"
  }
}
```

使用：

```bash
github-activity owner/repo \
  --tags changelog_tags.json \
  --output CHANGELOG.md \
  --auth $GITHUB_TOKEN
```

## 处理大仓库

对于活动频繁的大仓库：
- 使用 `--cache`（默认启用）避免重复请求
- 分批次生成（按月或按季度）
- 设置GITHUB_TOKEN提高速率限制
- 使用 `--kind pr` 只获取PR（通常changelog不需要Issue列表）

```bash
# 按月生成大仓库changelog
for month in 2024-01 2024-02 2024-03; do
  since="${month}-01"
  until=$(date -d "$month-01 +1 month" +%Y-%m-%d)
  github-activity large/repo --since $since --until $until \
    --output "changelog_${month}.md" --auth $GITHUB_TOKEN
done
```

## 相关概念

- [CLI命令详解](/concepts/02-cli-usage.md)
- [标签分类配置](/concepts/04-configuration.md)
- [快速开始](/concepts/01-getting-started.md)

---
title: 05 - API 响应耗时性能验证指南
icon: material/timer-outline
source: >
  本指南用于独立验证 P0-047 中知乎搜索 API "平均 600ms 延迟"的厂商自述数据。
  测试方案基于官方 API 文档 [F-107][F-108] 设计。
---

# API 响应耗时性能验证指南

> **目的**：独立实测知乎开放平台搜索 API 的实际响应耗时，验证产品页宣称的"平均 600ms 延迟"是否属实 [F-202] [P0-047]。
>
> **前置条件**：已获得知乎开放平台 API Key（邀测阶段），本地安装 Python 3.8+。
>
> **注意**：本测试会消耗 API 额度，请确保有足够额度。建议在非高峰时段测试。

## 测试设计

### 测试对象

| API | 端点 | 测试意义 |
|-----|------|---------|
| 知乎站内搜索 | `POST /api/v1/zhihu_search/query` | 验证站内搜索延迟 [F-107] |
| 全网搜索 | `POST /api/v1/global_search/query` | 验证全网搜索延迟 [F-108] |
| 热榜 | `POST /api/v1/hot_list/query` | 对比基准（轻量接口） [F-109] |

### 测试维度

- **平均延迟**：多次调用取平均值，与官方宣称的 600ms 对比
- **P50 / P95 / P99**：延迟分布，判断稳定性
- **首包 vs 全包**：区分连接时间和处理时间（使用流式接口时更重要）

### 测试用例设计

| 用例 | 查询内容 | 目的 |
|------|---------|------|
| 简单关键词 | "Python" | 常见短查询，基线性能 |
| 复杂长句 | "如何在 Windows 上配置 WSL2 和 Docker Desktop 的 GPU 加速" | 复杂中文查询，模拟真实场景 |
| 热门话题 | 热榜前 3 条的关键词 | 高热度内容，缓存命中场景 |
| 冷门关键词 | 随机字符串组合 | 缓存未命中场景，测试最坏情况 |

## 测试脚本

### 依赖安装

```bash
pip install requests numpy
```

### 测试脚本

```python
"""
知乎开放平台 API 响应耗时测试工具
用于验证 P0-047 中"平均 600ms 延迟"的厂商自述
"""

import time
import json
import statistics
import requests
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict

# === 配置区 ===
API_KEY = "你的APIKey"  # 或从环境变量读取
BASE_URL = "https://developer.zhihu.com"
TEST_ROUNDS = 10  # 每轮测试次数，建议 >= 10
WARMUP_ROUNDS = 2  # 预热次数（不计入统计）

# === 测试用例 ===
TEST_CASES = [
    {
        "name": "zhihu_search_简单关键词",
        "endpoint": "/api/v1/zhihu_search/query",
        "body": {"query": "Python", "page": 1, "page_size": 10}
    },
    {
        "name": "zhihu_search_复杂长句",
        "endpoint": "/api/v1/zhihu_search/query",
        "body": {
            "query": "如何在 Windows 上配置 WSL2 和 Docker Desktop 的 GPU 加速",
            "page": 1, "page_size": 10
        }
    },
    {
        "name": "global_search_简单关键词",
        "endpoint": "/api/v1/global_search/query",
        "body": {"query": "Python", "page": 1, "page_size": 10}
    },
    {
        "name": "hotlist_基准对比",
        "endpoint": "/api/v1/hot_list/query",
        "body": {"limit": 10}
    },
]


@dataclass
class LatencyResult:
    name: str
    latencies: List[float] = field(default_factory=list)

    @property
    def avg(self) -> float:
        return statistics.mean(self.latencies)

    @property
    def p50(self) -> float:
        return np.percentile(self.latencies, 50)

    @property
    def p95(self) -> float:
        return np.percentile(self.latencies, 95)

    @property
    def p99(self) -> float:
        return np.percentile(self.latencies, 99)

    @property
    def min(self) -> float:
        return min(self.latencies)

    @property
    def max(self) -> float:
        return max(self.latencies)


def call_api(endpoint: str, body: dict) -> float:
    """调用一次 API，返回耗时（毫秒）"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Request-Timestamp": str(int(time.time())),
        "Content-Type": "application/json"
    }
    start = time.perf_counter()
    resp = requests.post(url, json=body, headers=headers, timeout=30)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    resp.raise_for_status()
    return elapsed


def run_test(name: str, endpoint: str, body: dict) -> LatencyResult:
    """运行单个测试用例"""
    result = LatencyResult(name=name)

    # 预热
    print(f"  预热 {WARMUP_ROUNDS} 次...")
    for i in range(WARMUP_ROUNDS):
        try:
            call_api(endpoint, body)
        except Exception as e:
            print(f"  预热失败: {e}")
            return result

    # 正式测试
    print(f"  正式测试 {TEST_ROUNDS} 次...")
    for i in range(TEST_ROUNDS):
        try:
            latency = call_api(endpoint, body)
            result.latencies.append(latency)
            print(f"    第 {i+1:2d} 次: {latency:.0f} ms")
        except Exception as e:
            print(f"    第 {i+1:2d} 次: 失败 - {e}")
        time.sleep(0.5)  # 避免触发频率限制

    return result


def print_report(results: List[LatencyResult]):
    """打印测试报告"""
    print("\n" + "=" * 80)
    print("  知乎开放平台 API 响应耗时测试报告")
    print("=" * 80)

    header = f"{'测试用例':<30} {'Avg(ms)':>8} {'P50(ms)':>8} {'P95(ms)':>8} {'P99(ms)':>8} {'Min(ms)':>8} {'Max(ms)':>8}"
    print(header)
    print("-" * 80)

    for r in results:
        if not r.latencies:
            print(f"{r.name:<30}  无有效数据")
            continue
        verdict = "✅ 接近 600ms" if r.avg < 800 else "⚠️ 高于宣称值" if r.avg < 1500 else "❌ 远高于宣称值"
        print(f"{r.name:<30} {r.avg:>8.0f} {r.p50:>8.0f} {r.p95:>8.0f} {r.p99:>8.0f} {r.min:>8.0f} {r.max:>8.0f}  {verdict}")

    print("-" * 80)
    print("\n💡 解读说明：")
    print("  - 官方宣称平均延迟约 600ms [F-202]，但实测值受网络环境、查询复杂度、时段影响较大")
    print("  - 国内用户直连可能在 200~800ms 之间，海外用户可能更高")
    print("  - P95/P99 反映尾部延迟，比平均值更能体现真实体验")
    print("  - 热榜接口通常更快，可作为基准对比")
    print("\n📌 结果请自行与 P0-047 的核验结论对照参考")


def main():
    if not API_KEY or API_KEY == "你的APIKey":
        # 尝试从环境变量读取
        import os
        API_KEY = os.environ.get("ZHIHU_API_KEY", "")
        if not API_KEY:
            print("错误：请设置 API_KEY 或 ZHIHU_API_KEY 环境变量")
            return

    results = []
    for i, case in enumerate(TEST_CASES):
        print(f"\n[{i+1}/{len(TEST_CASES)}] 测试: {case['name']}")
        result = run_test(case["name"], case["endpoint"], case["body"])
        results.append(result)

    print_report(results)


if __name__ == "__main__":
    main()
```

## 使用方法

### 1. 准备 API Key

```bash
# Windows PowerShell
$env:ZHIHU_API_KEY = "你的Key"

# Linux/Mac
export ZHIHU_API_KEY="你的Key"
```

### 2. 运行测试

```bash
python api_latency_benchmark.py
```

### 3. 解读结果

| 平均延迟范围 | 评估 | 说明 |
|-------------|------|------|
| < 600ms | ✅ 优于宣称 | 网络条件好 + 查询简单 |
| 600 ~ 900ms | ⚠️ 接近宣称 | 基本符合，差异来自网络/服务器负载 |
| 900 ~ 1500ms | ⚠️ 高于宣称 | 可能受网络环境或复杂查询影响 |
| > 1500ms | ❌ 远高于宣称 | 需要排查网络或联系官方 |

## 注意事项

1. **额度消耗**：每次测试调用都会消耗对应 API 额度
2. **频率限制**：脚本内置 0.5s 间隔，避免触发频率限制
3. **网络因素**：延迟包含网络传输时间，与测试地点和网络质量强相关
4. **时段差异**：高峰期（工作日白天）可能比凌晨慢
5. **缓存效应**：重复查询同一关键词可能命中缓存，导致后续请求更快
6. **冷启动**：首次调用可能偏慢（连接建立/TLS握手），脚本已做预热处理

## 与 P0-047 的对应关系

本测试直接对应 [P0-047](../references/verification.md) 中标记为 ⚠️ 的性能数据部分：

- 可实测验证：**平均响应延迟 600ms**
- 无法独立核验：**百亿索引规模**、**分钟级实时索引频率**

> 📌 测试完成后，建议将实测结果记录到 verification.md 的 P0-047 备注中，更新核验结论。

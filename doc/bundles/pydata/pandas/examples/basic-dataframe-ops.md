---
okf_version: "0.2"
type: example
title: pandas 基础操作完整示例
description: 从创建 DataFrame、读写 CSV、选择过滤、分组聚合、合并连接到透视表与时间序列操作的完整可运行代码示例。
tags: [pandas, 示例, DataFrame, CSV, groupby, merge, pivot_table, 时间序列]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: dataframe-source
    resource: pandas/core/frame.py
    title: DataFrame 实现
  - id: series-source
    resource: pandas/core/series.py
    title: Series 实现
  - id: io-api
    resource: pandas/io/api.py
    title: IO API 导出
  - id: reshape-api
    resource: pandas/core/reshape/api.py
    title: 变形/合并 API
---

# pandas 基础操作完整示例

本文档提供 pandas 日常数据操作的完整代码示例，涵盖创建 DataFrame、读写数据、选择过滤、分组聚合、合并连接、透视表和时间序列操作。

## 前置条件

```python
import pandas as pd
import numpy as np
```

---

## 1. 创建 DataFrame 和 Series

### 1.1 从字典创建 DataFrame

```python
# 从字典创建（key 为列名，value 为列数据）
data = {
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "age": [25, 30, 35, 28, 32],
    "city": ["Beijing", "Shanghai", "Beijing", "Shenzhen", "Shanghai"],
    "salary": [12000, 18000, 22000, 15000, 20000],
}
df = pd.DataFrame(data)
print(df)
#       name  age      city  salary
# 0    Alice   25   Beijing   12000
# 1      Bob   30  Shanghai   18000
# 2  Charlie   35   Beijing   22000
# 3    Diana   28  Shenzhen   15000
# 4      Eve   32  Shanghai   20000
```

### 1.2 指定索引创建

```python
df2 = pd.DataFrame(
    data={"score": [92, 85, 78, 95, 88]},
    index=["Alice", "Bob", "Charlie", "Diana", "Eve"],
)
print(df2)
#          score
# Alice       92
# Bob         85
# Charlie     78
# Diana       95
# Eve         88
```

### 1.3 从 NumPy 数组创建

```python
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
df3 = pd.DataFrame(arr, columns=["A", "B", "C"], index=["x", "y", "z"])
print(df3)
#    A  B  C
# x  1  2  3
# y  4  5  6
# z  7  8  9
```

### 1.4 从列表创建 Series

```python
s = pd.Series([10, 20, 30, 40, 50], name="values")
print(s)
# 0    10
# 1    20
# 2    30
# 3    40
# 4    50
# Name: values, dtype: int64

# 带自定义索引的 Series
s2 = pd.Series(
    {"Alice": 92, "Bob": 85, "Charlie": 78},
    name="score",
)
print(s2)
```

### 1.5 使用 date_range 创建时间序列索引

```python
dates = pd.date_range("2024-01-01", periods=5, freq="D")
ts = pd.Series([100, 101, 102, 103, 104], index=dates)
print(ts)
# 2024-01-01    100
# 2024-01-02    101
# 2024-01-03    102
# 2024-01-04    103
# 2024-01-05    104
# Freq: D, dtype: int64
```

---

## 2. 读写数据

### 2.1 写入和读取 CSV

```python
# 写入 CSV
df.to_csv("employees.csv", index=False, encoding="utf-8")

# 读取 CSV
df_read = pd.read_csv("employees.csv")

# 读取 CSV 时指定参数
df_read = pd.read_csv(
    "employees.csv",
    dtype={"age": "Int64", "salary": "Float64"},  # 指定列类型
    parse_dates=["hire_date"],  # 解析日期列
    na_values=["N/A", "null"],  # 指定缺失值标记
)
```

### 2.2 读写 Excel

```python
# 需要安装 openpyxl
# df.to_excel("employees.xlsx", index=False, sheet_name="Sheet1")
# df_xl = pd.read_excel("employees.xlsx", sheet_name="Sheet1")
```

### 2.3 读写 JSON

```python
df.to_json("employees.json", orient="records", force_ascii=False, indent=2)
df_json = pd.read_json("employees.json")
```

### 2.4 读写 Parquet（列式存储，推荐大数据场景）

```python
# 需要 pyarrow 或 fastparquet
# df.to_parquet("employees.parquet", index=False)
# df_pq = pd.read_parquet("employees.parquet")
```

### 2.5 快速查看数据

```python
df.head(3)       # 前 3 行
df.tail(2)       # 后 2 行
df.sample(2)     # 随机 2 行
df.shape         # (行数, 列数)
df.dtypes        # 各列数据类型
df.info()        # 总体信息
df.describe()    # 数值列统计摘要
df.columns       # 列名 Index
df.index         # 行索引
```

---

## 3. 选择与过滤

### 3.1 列选择

```python
# 单列 → 返回 Series
df["name"]
df.name  # 仅当列名合法 Python 标识符时可用

# 多列 → 返回 DataFrame
df[["name", "salary"]]
```

### 3.2 行选择

```python
# 按标签（loc）
df.loc[0]           # 第一行，返回 Series
df.loc[0:2]         # 前 3 行（闭区间，包含 2）
df.loc[0, "name"]   # 第一行的 name 列

# 按位置（iloc）
df.iloc[0]          # 第一行
df.iloc[0:3, 1:3]   # 前 3 行，第 2-3 列
df.iloc[0, 0]       # 第一行第一列
```

### 3.3 布尔过滤

```python
# 单条件
df[df["age"] > 30]

# 多条件组合（使用 & | ~，注意括号）
df[(df["age"] > 28) & (df["city"] == "Beijing")]
df[df["city"].isin(["Beijing", "Shanghai"])]

# 字符串方法
df[df["name"].str.startswith("A")]
```

### 3.4 query 方法（类似 SQL 语法）

```python
df.query("age > 28 and city == 'Beijing'")
df.query("salary > @avg_salary")  # @ 引用 Python 变量
```

### 3.5 赋值/修改列

```python
# 添加新列
df["bonus"] = df["salary"] * 0.1
df["dept"] = "Tech"  # 标量广播

# 修改列
df.loc[df["age"] > 30, "salary"] = df["salary"] * 1.05  # 涨薪 5%

# 删除列
df = df.drop(columns=["bonus"])
# 或 df.drop(columns=["bonus"], inplace=True)
```

---

## 4. 分组聚合

### 4.1 单列分组聚合

```python
# 按城市分组，计算各统计量
df.groupby("city")["salary"].mean()
# city
# Beijing     17000.0
# Shanghai    19000.0
# Shenzhen    15000.0
# Name: salary, dtype: float64

# 多列统计
df.groupby("city")["salary"].agg(["mean", "sum", "count", "min", "max"])
```

### 4.2 多列分组

```python
df.groupby(["city", "dept"])["salary"].mean()
```

### 4.3 命名聚合（NamedAgg）

```python
result = df.groupby("city").agg(
    avg_salary=pd.NamedAgg(column="salary", aggfunc="mean"),
    max_age=pd.NamedAgg(column="age", aggfunc="max"),
    employee_count=pd.NamedAgg(column="name", aggfunc="count"),
)
print(result)
#           avg_salary  max_age  employee_count
# city
# Beijing      17000.0       35               2
# Shanghai     19000.0       32               2
# Shenzhen     15000.0       28               1
```

### 4.4 transform（组内转换）

```python
# 添加列：每个城市的平均薪资
df["city_avg_salary"] = df.groupby("city")["salary"].transform("mean")

# 组内标准化
df["salary_zscore"] = df.groupby("city")["salary"].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

### 4.5 filter（组级过滤）

```python
# 只保留人数 >= 2 的城市
df_big_cities = df.groupby("city").filter(lambda g: len(g) >= 2)
```

### 4.6 pivot_table（透视表）

```python
pivot = pd.pivot_table(
    df,
    values="salary",
    index="city",
    columns="dept",
    aggfunc="mean",
    fill_value=0,
    margins=True,  # 添加合计行/列
)
```

---

## 5. 合并与连接

### 5.1 merge（类 SQL JOIN）

```python
# 创建第二个 DataFrame
dept_info = pd.DataFrame({
    "city": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
    "region": ["North", "East", "South", "South"],
    "manager": ["Wang", "Li", "Zhang", "Chen"],
})

# 内连接（默认）
merged = pd.merge(df, dept_info, on="city", how="inner")

# 左连接
merged_left = pd.merge(df, dept_info, on="city", how="left")

# 右连接
merged_right = pd.merge(df, dept_info, on="city", how="right")

# 外连接
merged_outer = pd.merge(df, dept_info, on="city", how="outer")

# 列名不同时
# pd.merge(df1, df2, left_on="city", right_on="office_city")
```

### 5.2 concat（轴向拼接）

```python
df_a = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
df_b = pd.DataFrame({"x": [5, 6], "y": [7, 8]})

# 行拼接（纵向）
pd.concat([df_a, df_b], axis=0, ignore_index=True)

# 列拼接（横向）
pd.concat([df_a, df_b], axis=1)
```

### 5.3 join（基于索引的快捷合并）

```python
df2_indexed = df2.set_index("name")
df_joined = df.set_index("name").join(df2_indexed, how="left")
```

### 5.4 merge_asof（最近键合并，适合时间序列）

```python
trades = pd.DataFrame({
    "time": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:05"]),
    "price": [100, 101],
})
quotes = pd.DataFrame({
    "time": pd.to_datetime(["2024-01-01 09:59", "2024-01-01 10:02", "2024-01-01 10:06"]),
    "bid": [99, 100, 100],
})
# 每笔交易匹配最近的报价（不晚于交易时间）
pd.merge_asof(trades, quotes, on="time", direction="backward")
```

---

## 6. 数据清洗

### 6.1 缺失值处理

```python
df_missing = pd.DataFrame({
    "a": [1, np.nan, 3, None],
    "b": [np.nan, 2, np.nan, 4],
})

# 检测缺失值
df_missing.isna()
df_missing.isna().sum()

# 删除缺失值
df_missing.dropna()           # 删除含 NaN 的行
df_missing.dropna(axis=1)     # 删除含 NaN 的列
df_missing.dropna(thresh=2)   # 至少 2 个非 NaN 值才保留

# 填充缺失值
df_missing.fillna(0)                          # 填充为 0
df_missing.fillna(method="ffill")             # 前向填充
df_missing.fillna(df_missing.mean())          # 用均值填充
df_missing["a"] = df_missing["a"].fillna(df_missing["a"].median())  # 指定列
```

### 6.2 重复值处理

```python
df_dup = pd.DataFrame({"x": [1, 1, 2, 3], "y": [1, 1, 2, 3]})
df_dup.duplicated()        # 标记重复行
df_dup.drop_duplicates()   # 删除重复行
df_dup.drop_duplicates(subset=["x"], keep="last")  # 按 x 列去重
```

### 6.3 数据类型转换

```python
df["age"] = df["age"].astype("float64")
df["city"] = df["city"].astype("category")    # 转为分类类型节省内存
df["hire_date"] = pd.to_datetime(df["hire_date"])  # 转为日期类型
df["salary"] = pd.to_numeric(df["salary"], errors="coerce")  # 转为数值，错误转 NaN
```

### 6.4 替换值

```python
df["city"] = df["city"].replace({"Beijing": "BJ", "Shanghai": "SH"})
df.replace([np.inf, -np.inf], np.nan, inplace=True)  # 无穷大替换为 NaN
```

---

## 7. 排序与排名

### 7.1 排序

```python
# 按值排序
df.sort_values("salary", ascending=False)  # 按薪资降序
df.sort_values(["city", "salary"], ascending=[True, False])  # 多列排序

# 按索引排序
df.sort_index()
```

### 7.2 排名

```python
df["salary_rank"] = df["salary"].rank(ascending=False, method="min")
# method: 'average'(默认), 'min', 'max', 'first', 'dense'
```

---

## 8. 时间序列操作

### 8.1 创建时间序列 DataFrame

```python
dates = pd.date_range("2024-01-01", periods=100, freq="D")
ts_df = pd.DataFrame({
    "price": np.random.randn(100).cumsum() + 100,
    "volume": np.random.randint(1000, 10000, 100),
}, index=dates)
```

### 8.2 时间索引操作

```python
# 按日期范围切片
ts_df["2024-01"]           # 1 月所有数据
ts_df["2024-01-15":"2024-02-15"]  # 日期范围

# 时间属性访问
ts_df.index.year
ts_df.index.month
ts_df.index.dayofweek  # 0=Monday
ts_df.index.quarter
```

### 8.3 重采样（Resample）

```python
# 日频 → 周频
ts_df.resample("W").mean()

# 月频聚合
ts_df.resample("ME").agg({
    "price": "ohlc",  # 开高低收
    "volume": "sum",
})

# 滚动窗口
ts_df["price"].rolling(window=7).mean()    # 7 日移动平均
ts_df["price"].rolling(window=7, min_periods=3).std()  # 至少 3 个值

# 指数加权移动平均
ts_df["price"].ewm(span=12).mean()
```

### 8.4 时区处理

```python
# 指定时区
ts_utc = ts_df.tz_localize("UTC")

# 转换时区
ts_shanghai = ts_utc.tz_convert("Asia/Shanghai")
```

### 8.5 日期偏移（DateOffset）

```python
from pandas.tseries.offsets import Day, MonthEnd, BusinessDay

ts_df.index + Day(5)            # 加 5 天
ts_df.index + MonthEnd(1)       # 移到下月末
ts_df.index + BusinessDay(10)   # 加 10 个工作日
```

---

## 9. apply 与自定义函数

### 9.1 apply 按行/列应用函数

```python
# 按列应用（默认 axis=0）
df[["age", "salary"]].apply(lambda col: col.max() - col.min())

# 按行应用（axis=1）
df["age_salary_ratio"] = df.apply(
    lambda row: row["salary"] / row["age"], axis=1
)
```

### 9.2 map（Series 元素级映射）

```python
# 字典映射
city_map = {"Beijing": "BJ", "Shanghai": "SH", "Shenzhen": "SZ"}
df["city_code"] = df["city"].map(city_map)

# 函数映射
df["name_upper"] = df["name"].map(str.upper)
```

### 9.3 applymap（DataFrame 元素级，已弃用，用 map 替代）

```python
# pandas 2.1+ 推荐使用 DataFrame.map
# df_str = df[["name", "city"]].map(str.upper)
```

---

## 10. 常用统计与计算

```python
# 基本统计
df["salary"].mean()
df["salary"].median()
df["salary"].std()
df["salary"].var()
df["salary"].quantile(0.75)
df[["age", "salary"]].corr()  # 相关系数矩阵
df[["age", "salary"]].cov()   # 协方差矩阵

# 唯一值与计数
df["city"].unique()
df["city"].nunique()
df["city"].value_counts()

# 累计计算
df["salary"].cumsum()
df["salary"].cummax()
```

---

## 11. 链式调用风格（Method Chaining）

```python
result = (
    df
    .query("age >= 25")
    .assign(
        salary_k=lambda x: x["salary"] / 1000,
        age_group=lambda x: pd.cut(x["age"], bins=[0, 28, 32, 100],
                                   labels=["Junior", "Mid", "Senior"]),
    )
    .groupby(["city", "age_group"], observed=True)
    .agg(
        avg_salary_k=("salary_k", "mean"),
        count=("name", "count"),
    )
    .reset_index()
    .sort_values("avg_salary_k", ascending=False)
)
```

---

## 相关概念

- [pandas 简介](../concepts/00-introduction.md)
- [DataFrame 数据模型](../concepts/01-dataframe-model.md)
- [Series 与 Index](../concepts/02-series-index.md)
- [GroupBy 机制](../concepts/03-groupby-aggregation.md)
- [核心初始化源码分析](../references/core-init.md)

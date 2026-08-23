---
source: jupyter_scheduler/models.py
title: 数据模型源码解析
---

# 数据模型源码解析

> 信源路径：`jupyter_scheduler/models.py`（314行）

## 模型分类

### 枚举类型

**Status**（作业状态）：
- `CREATED` - 已创建
- `QUEUED` - 排队中
- `IN_PROGRESS` - 执行中
- `COMPLETED` - 已完成
- `FAILED` - 失败
- `STOPPING` - 停止中
- `STOPPED` - 已停止

**SortDirection**：`asc`、`desc`

**JobFeature**（功能特性标识）：
- job_name、parameters、output_formats、job_definition、idempotency_token、tags、email_notifications、timeout_seconds、retry_on_timeout、max_retries、min_retry_interval_millis、output_filename_template、stop_job、delete_job

### 核心模型

| 模型 | 用途 | orm_mode |
|-----|------|---------|
| CreateJob | 创建作业请求 | - |
| DescribeJob | 作业详情响应 | ✓ |
| UpdateJob | 更新作业请求 | - |
| CreateJobDefinition | 创建作业定义请求 | - |
| DescribeJobDefinition | 作业定义详情响应 | ✓ |
| UpdateJobDefinition | 更新作业定义请求 | - |
| ListJobsQuery | 查询作业列表参数 | - |
| ListJobsResponse | 作业列表响应 | - |
| ListJobDefinitionsQuery | 查询作业定义列表参数 | - |
| ListJobDefinitionsResponse | 作业定义列表响应 | - |
| CountJobsQuery | 统计作业参数 | - |
| CreateJobFromDefinition | 从定义创建作业请求 | - |
| JobFile | 作业文件描述 | - |
| OutputFormat | 输出格式描述 | - |
| RuntimeEnvironment | 运行时环境描述 | - |
| EmailNotifications | 邮件通知配置 | - |

## 关键模型字段

### CreateJob

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| input_uri | str | ✓ | 输入文件路径（相对root_dir） |
| input_filename | str | 自动 | 从input_uri提取（root_validator） |
| runtime_environment_name | str | ✓ | 运行时环境名称 |
| output_formats | List[str] | - | 输出格式列表 |
| idempotency_token | str | - | 幂等性令牌（防重复创建） |
| parameters | Dict[str,str] | - | Notebook参数 |
| tags | List[str] | - | 标签 |
| name | str | ✓ | 作业名称 |
| output_filename_template | str | 默认模板 | 输出文件名模板 |
| compute_type | str | - | 计算类型 |
| package_input_folder | bool | - | 是否打包输入文件夹 |
| backend_id | str | - | 后端ID |

### DescribeJob（继承CreateJob字段+额外字段）

额外字段：job_id、job_files、url、create_time、update_time、start_time、end_time、status、status_message、downloaded、packaged_files、backend_id。

### CreateJobDefinition（比CreateJob多schedule/timezone，无idempotency_token/job_definition_id）

### DescribeJobDefinition（额外字段：job_definition_id、active、url）

## 常量

- `OUTPUT_FILENAME_TEMPLATE = "{{input_filename}}-{{create_time}}"` - 默认输出文件名模板
- `DEFAULT_SORT = SortField(name="create_time", direction=SortDirection.desc)` - 默认按创建时间降序
- `DEFAULT_MAX_ITEMS = 1000` - 默认分页大小
- `Tags = List[str]` - 类型别名
- `EnvironmentParameterValues = Union[int, float, bool, str]` - 参数值类型

## pydantic v1 兼容层

`jupyter_scheduler/pydantic_v1/` 目录提供 pydantic v1/v2 兼容：
- 自动检测安装的pydantic版本
- v1从pydantic直接导出，v2从pydantic.v1导出
- 提供dataclasses兼容

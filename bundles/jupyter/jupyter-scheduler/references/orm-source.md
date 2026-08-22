---
source: jupyter_scheduler/orm.py
title: ORM 数据库层源码解析
---

# ORM 数据库层源码解析

> 信源路径：`jupyter_scheduler/orm.py`（165行）

## 核心组件

### Base

`Base = declarative_base()` - SQLAlchemy 2.0 声明式基类。

### 自定义类型

**JsonType**（TypeDecorator）：
- 底层存储：String
- Python对象 → JSON字符串（bind）
- JSON字符串 → Python对象（result）
- `cache_ok = True`

**EmailNotificationType**（TypeDecorator）：
- 底层存储：String
- EmailNotifications pydantic模型 → JSON字符串（bind）
- JSON字符串 → EmailNotifications.construct()（result）

### CommonColumns Mixin

Job和JobDefinition共用的列：

| 列名 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| runtime_environment_name | String(256) | NOT NULL | 运行时环境名称 |
| runtime_environment_parameters | JsonType(1024) | - | 环境参数 |
| compute_type | String(256) | - | 计算类型 |
| input_filename | String(256) | NOT NULL | 输入文件名 |
| output_formats | JsonType(512) | - | 输出格式列表 |
| name | String(256) | - | 作业名称 |
| tags | JsonType(1024) | - | 标签列表 |
| parameters | JsonType(1024) | - | 参数字典 |
| email_notifications | EmailNotificationType(1024) | - | 邮件通知配置 |
| timeout_seconds | Integer | 600 | 超时秒数 |
| retry_on_timeout | Boolean | False | 超时是否重试 |
| max_retries | Integer | 0 | 最大重试次数 |
| min_retry_interval_millis | Integer | 0 | 最小重试间隔 |
| output_filename_template | String(256) | - | 输出文件名模板 |
| update_time | Integer | get_utc_timestamp | 更新时间（onupdate自动刷新） |
| create_time | Integer | get_utc_timestamp | 创建时间 |
| package_input_folder | Boolean | - | 是否打包输入文件夹 |
| packaged_files | JsonType | [] | 打包的副作用文件列表 |

### Job 表（`__tablename__ = "jobs"`）

| 列名 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| job_id | String(128), PK | generate_uuid() | 作业ID（backend_id:uuid格式） |
| job_definition_id | String(36) | - | 关联的作业定义ID |
| status | String(64) | STOPPED | 作业状态 |
| status_message | String(1024) | - | 状态消息/错误信息 |
| start_time | Integer | - | 开始时间 |
| end_time | Integer | - | 结束时间 |
| url | String(256) | generate_jobs_url | 作业URL（`/jobs/{job_id}`） |
| pid | Integer | - | 子进程ID |
| idempotency_token | String(256) | - | 幂等性令牌 |
| backend_id | String(64) | - | 后端ID |

### JobDefinition 表（`__tablename__ = "job_definitions"`）

| 列名 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| job_definition_id | String(36), PK | generate_uuid() | 作业定义ID |
| schedule | String(256) | - | cron表达式 |
| timezone | String(36) | - | 时区 |
| url | String(256) | generate_job_definitions_url | URL（`/job_definitions/{id}`） |
| active | Boolean | True | 是否激活 |
| backend_id | String(64) | - | 后端ID |

### 辅助函数

**generate_uuid()**：返回 `str(uuid4())`

**generate_jobs_url(context)**：返回 `f"/jobs/{job_id}"`

**generate_job_definitions_url(context)**：返回 `f"/job_definitions/{job_definition_id}"`

## 数据库管理函数

### create_tables(db_url, drop_tables=False)

```
1. create_engine(db_url)
2. update_db_schema(engine, Base)  # 自动迁移
3. if drop_tables: Base.metadata.drop_all(engine)
4. Base.metadata.create_all(engine)
```

### update_db_schema(engine, Base) - 轻量级自动迁移

```
1. inspect(engine) 获取现有表结构
2. 对每个模型表：
   a. 若表不存在则跳过（create_all会创建）
   b. 对比现有列与模型列
   c. 缺少的列生成 ALTER TABLE ADD COLUMN ... NULL
3. 执行所有ALTER语句
```

**迁移约束**：新列必须nullable，迁移时默认值被忽略。这是因为SQLite的ALTER TABLE ADD COLUMN限制。

### create_session(db_url)

创建sessionmaker工厂（非session实例），echo=False。

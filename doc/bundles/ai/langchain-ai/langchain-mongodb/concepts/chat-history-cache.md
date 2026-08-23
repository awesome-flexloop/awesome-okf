---
type: concept
scope: langchain-mongodb
name: chat-history-cache
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: 缓存与聊天历史——MongoDBCache、MongoDBAtlasSemanticCache 和 MongoDBChatMessageHistory 的设计与使用
---

# 缓存与聊天历史

langchain-mongodb 提供两类会话状态持久化组件：LLM 响应缓存（精确缓存和语义缓存）和聊天消息历史。它们分别实现 LangChain 的 `BaseCache` 和 `BaseChatMessageHistory` 抽象。

## 精确缓存：MongoDBCache

`MongoDBCache` 实现基于 prompt + llm_string 精确匹配的 LLM 响应缓存。适用于相同查询频繁重复的场景（如开发调试、FAQ 系统）。

### 存储结构

每个缓存条目是一个独立文档：

```javascript
{
  "_id": ObjectId("..."),
  "prompt": "用户输入的完整 prompt",
  "llm": "gpt-4-temperature-0.0",   // LLM 标识字符串
  "return_val": "[{\"lc\": 1, \"type\": \"Constructor\", ...}]"  // 序列化的 Generation 列表
}
```

构造时自动在 `[prompt, llm]` 上创建复合索引，加速精确查找。

### 工作流程

```
LLM 调用请求 (prompt, llm_string)
        │
        ▼
┌───────────────────┐
│ collection.       │
│ find_one(         │
│   {prompt, llm}   │  ← 精确匹配
│ )                 │
└─────────┬─────────┘
          │
     ┌────┴────┐
     │ 命中？  │
     └────┬────┘
     是 │   │ 否
        │   └──→ 调用 LLM → update(prompt, llm, result)
        ▼
   返回反序列化结果
```

### 序列化机制

`_dumps_generations` 和 `_loads_generations` 处理 Generation 对象的序列化：

1. 每个 `Generation`（或其子类）通过 `langchain_core.load.dump.dumps` 序列化为 LangChain 标准 JSON 格式
2. 整个列表再通过 `json.dumps` 序列化为单个字符串
3. 反序列化时优先使用 `loads(..., allowed_objects="core")`，支持所有 Generation 子类
4. 兼容旧版格式：回退到直接 `Generation(**dict)` 构造
5. 对损坏数据返回 None 并记录 warning，不抛出异常（缓存失败不应导致请求失败）

### 选择性清除

`clear(**kwargs)` 支持通过关键字参数过滤删除：

```python
cache.clear(llm="gpt-4-temperature-0.0")  # 只清除特定模型的缓存
```

## 语义缓存：MongoDBAtlasSemanticCache

`MongoDBAtlasSemanticCache` 通过多继承同时实现 `BaseCache` 和复用 `MongoDBAtlasVectorSearch`，基于向量语义相似度匹配缓存条目。

### 多继承架构

```python
class MongoDBAtlasSemanticCache(BaseCache, MongoDBAtlasVectorSearch):
```

这种设计使得语义缓存天然具备 VectorStore 的全部能力：
- `lookup` 复用 `similarity_search_with_score`
- `update` 复用 `add_texts`
- 无需组合模式的委托样板代码

### 存储结构

```javascript
{
  "_id": ObjectId("..."),
  "text": "用户 prompt 文本",
  "embedding": [...],
  "llm_string": "gpt-4-temperature-0.0",
  "return_val": "[序列化的 Generation 列表]"
}
```

### lookup 流程

```
prompt + llm_string
        │
        ▼
similarity_search_with_score(
    prompt,
    k=1,
    pre_filter={"llm_string": {"$eq": llm_string}},  ← 同一模型内搜索
    post_filter_pipeline=[
        {"$match": {"score": {"$gte": score_threshold}}}  ← 可选阈值
    ]
)
        │
        ▼
   有结果？──是──→ 从 metadata 取 return_val → 反序列化返回
        │
        否
        ▼
      None（缓存未命中）
```

关键设计点：
- **llm_string 作为 pre_filter**：在向量搜索阶段过滤，只在同一 LLM 配置的缓存条目中做语义匹配，避免不同模型/参数的结果混用
- **score_threshold 作为 post_filter**：在向量搜索打分后过滤，低于阈值的结果视为未命中
- **top-1 语义匹配**：只取语义最接近的一条缓存

### 写入后一致性等待

语义缓存写入后，Atlas 索引需要时间才能查询到新写入的文档（近实时而非实时）。`wait_until_ready` 参数控制轮询等待：

```python
def is_indexed():
    return self.lookup(prompt, llm_string) == return_val

_wait_until(is_indexed, return_val, timeout=wait)
```

轮询间隔为 `min(timeout/100, 0.1)` 秒，直到查找结果与写入值一致或超时。

## 聊天历史：MongoDBChatMessageHistory

`MongoDBChatMessageHistory` 实现 LangChain 的 `BaseChatMessageHistory` 抽象，将会话消息持久化到 MongoDB。

### 一消息一文档模型

与将整个历史存储在单文档数组中的设计不同，该实现采用**每条消息独立文档**：

```javascript
// 消息 1
{
  "_id": ObjectId("..."),
  "SessionId": "user-123-conversation-456",
  "History": "{\"type\": \"human\", \"data\": {\"content\": \"你好\", ...}}"
}

// 消息 2
{
  "_id": ObjectId("..."),
  "SessionId": "user-123-conversation-456",
  "History": "{\"type\": \"ai\", \"data\": {\"content\": \"你好！有什么可以帮你的？\", ...}}"
}
```

字段名可自定义：
- `session_id_key`（默认 `"SessionId"`）：会话标识字段
- `history_key`（默认 `"History"`）：消息 JSON 字段

### 设计优势

1. **写入简单**：`add_message` 只需 `insert_one`，无需原子数组操作
2. **无文档大小限制**：超长会话不会触及 16MB BSON 限制
3. **天然支持历史窗口**：通过 `count_documents + skip` 实现"取最近 N 条"
4. **写入吞吐高**：多条消息可并行插入，无文档级锁竞争

### 消息序列化

每条消息通过 LangChain 的标准序列化工具处理：
- 写入：`message_to_dict(message)` → `json.dumps` → 存储为字符串
- 读取：`json.loads` → `messages_from_dict(items)` → 返回 `BaseMessage` 列表

这种 JSON 字符串存储方式而非 BSON 嵌套文档，保持了与 LangChain 消息格式的完全兼容。

### history_size：滑动窗口

`history_size` 参数限制检索的消息数量：

```python
history = MongoDBChatMessageHistory(
    connection_string="...",
    session_id="session-1",
    history_size=20,  # 只取最近 20 条消息
)
```

实现方式：
1. `count_documents` 查询会话总消息数
2. `skip_count = max(0, total - history_size)` 计算需要跳过的旧消息数
3. `find().skip(skip_count)` 获取最近的消息

注意：MongoDB 的 `skip` 在大偏移量时性能会下降，因此 `history_size` 应设为合理的小值（通常 10-50）。

### 连接管理

构造函数支持两种客户端传入方式：

```python
# 方式 1：连接字符串（内部创建 MongoClient）
history = MongoDBChatMessageHistory(
    connection_string="mongodb://localhost:27017/",
    session_id="session-1",
)

# 方式 2：传入已有的 MongoClient（推荐，复用连接池）
client = MongoClient("mongodb://localhost:27017/")
history = MongoDBChatMessageHistory(
    connection_string=None,
    session_id="session-1",
    client=client,
)
```

同时提供 `connection_string` 和 `client` 会抛出 `ValueError`。

### 索引

构造时 `create_index=True`（默认）自动在 `session_id_key` 上创建升序索引。这是查询性能的关键——所有消息检索都按 session_id 过滤。可通过 `index_kwargs` 传递额外索引选项（如 `unique=True`、`expireAfterSeconds` 等）。

## 三种组件对比

| 维度 | MongoDBCache | MongoDBAtlasSemanticCache | MongoDBChatMessageHistory |
|---|---|---|---|
| LangChain 抽象 | BaseCache | BaseCache | BaseChatMessageHistory |
| 匹配方式 | prompt + llm 精确匹配 | 向量语义相似度 | session_id 精确匹配 |
| 存储粒度 | 每个 (prompt, llm) 一条 | 每个 prompt 一条 | 每条消息一条 |
| 需要向量索引 | 否 | 是 | 否 |
| 需要 Atlas | 否（任何 MongoDB） | 是 | 否（任何 MongoDB） |
| 序列化 | dumps/loads Generation | dumps/loads Generation | message_to_dict/from_dict |
| 分数阈值 | 不适用 | score_threshold | 不适用 |
| 历史窗口 | 不适用 | 不适用 | history_size |

## 与其他存储组件的关系

除了缓存和聊天历史，langchain-mongodb 还提供：

- **MongoDBRecordManager**（`indexes.py`）：跟踪文档写入时间，配合 LangChain indexing API 实现增量更新
- **MongoDBDocStore**（`docstores.py`）：`BaseStore[str, Document]` 实现，用于父文档检索等场景的 KV 存储

这些组件共同构成完整的 RAG 状态管理层。详见 [API 参考](/ai/langchain-ai/langchain-mongodb/references/api)。

## 相关阅读

- [总览](/ai/langchain-ai/langchain-mongodb/concepts/overview)
- [向量存储架构](/ai/langchain-ai/langchain-mongodb/concepts/vector-store)
- [基础使用示例](/ai/langchain-ai/langchain-mongodb/examples/basic-usage)

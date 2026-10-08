---
okf_version: "0.2"
type: example
title: 添加知识库实现 RAG
description: 使用 KnowledgeBase 为 Agent 添加知识库能力，支持本地内存、Milvus、OpenSearch、VikingDB 等多种向量后端，通过 add_from_directory/add_from_text 导入文档，Agent 自动获得检索增强生成（RAG）能力
tags: [veadk-python, example, knowledge-base, rag, retrieval, vector-database, embeddings]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/knowledge-base.md
  - /concepts/agent-and-runner.md
sources:
  - id: veadk-python-self
    resource: /references/veadk-python-sources.md
    title: veadk-python 源码参考
---

# 添加知识库实现 RAG

## 场景说明

本示例演示如何使用 VeADK 的 `KnowledgeBase` 为 Agent 添加检索增强生成（RAG）能力。当 Agent 挂载 KnowledgeBase 后，VeADK 会自动为 Agent 添加一个检索工具，Agent 在回答问题前会先查询知识库，基于检索到的相关文档片段生成回答，从而将回答"接地"到你的私有数据上，而不是仅依赖模型的通用知识。KnowledgeBase 支持多种向量后端：本地内存（开发测试）、Milvus、OpenSearch、Redis、火山 VikingDB 等。

**前置条件**：
- Python ≥ 3.10
- 已安装 veadk-python 及其扩展依赖（`pip install "veadk-python[extensions]"`）
- 配置 Embedding 模型的 API Key（用于文档向量化）
- 理解 [知识库概念](../concepts/knowledge-base.md)

## 完整代码示例

```python
"""
add-knowledge-base.py
演示：为 Agent 添加 KnowledgeBase 实现 RAG（检索增强生成）
"""

import asyncio
import os
import tempfile
from pathlib import Path

from veadk import Agent, Runner
from veadk.knowledgebase import KnowledgeBase


# ── 步骤 1：准备示例文档 ──

def create_sample_docs(docs_dir: Path):
    """创建示例文档（模拟企业知识库文档）。"""
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 公司年假政策
    (docs_dir / "annual-leave-policy.md").write_text("""# 年假政策

## 年假天数
- 入职满1年不满5年：年假5天
- 入职满5年不满10年：年假10天
- 入职满10年及以上：年假15天

## 年假使用规则
1. 年假最小使用单位为0.5天
2. 年假需提前3个工作日申请
3. 年假可跨年度使用，但需在次年3月31日前休完
4. 离职时未休年假按日工资的300%补偿

## 申请流程
通过OA系统提交年假申请，经直属上级审批后生效。
紧急情况可先休假后补办手续，但需在休假当天通知主管。
""", encoding="utf-8")

    # 远程办公政策
    (docs_dir / "remote-work-policy.md").write_text("""# 远程办公政策

## 适用条件
- 入职满3个月的正式员工
- 岗位性质允许远程办公（如非前台、实验室等必须到岗岗位）
- 家中具备稳定网络和安静工作环境

## 远程办公天数
- 每周可申请1-2天远程办公
- 新人入职首月不安排远程办公
- 每月远程办公天数不超过8天

## 远程办公要求
1. 工作时间保持在线（飞书/企业微信）
2. 按时参加线上会议
3. 每日提交工作日报
4. 网络故障等突发情况需30分钟内通知主管

## 特殊情况
疫情、极端天气等特殊情况下，公司可统一安排全员远程办公。
""", encoding="utf-8")

    # 技术栈规范
    (docs_dir / "tech-stack.md").write_text("""# 技术栈规范

## 后端技术栈
- 主语言：Python 3.14（自由线程版本）
- Web框架：FastAPI
- 数据库：PostgreSQL 16 + Redis 7
- 消息队列：Apache Kafka
- ORM：SQLAlchemy 2.0

## 前端技术栈
- 框架：React 18 + TypeScript 5
- 构建工具：Vite 5
- UI组件库：Ant Design 5
- 状态管理：Zustand

## AI/ML技术栈
- Agent框架：VeADK
- 模型服务：火山方舟（Ark）
- 向量数据库：VikingDB
- 模型：Doubao-pro-32k

## 部署环境
- 容器：Docker + Kubernetes
- CI/CD：GitLab CI
- 云平台：火山引擎
- 监控：Prometheus + Grafana
""", encoding="utf-8")

    print(f"✅ 示例文档已创建: {docs_dir}")
    for f in docs_dir.iterdir():
        print(f"   - {f.name}")


# ── 步骤 2：创建知识库并导入文档 ──

def create_local_knowledgebase(index_name: str = "company_docs") -> KnowledgeBase:
    """
    创建本地内存知识库（开发测试用）。

    backend="local" 使用内存中的向量存储，
    程序退出后数据丢失，适合开发调试和示例演示。
    生产环境应使用 Milvus/VikingDB/OpenSearch 等持久化后端。
    """
    kb = KnowledgeBase(
        backend="local",            # 后端类型
        index=index_name,           # 索引名称（类似数据库表名）
        top_k=5,                    # 检索返回的最相关文档数量
        # backend_config={},        # 后端特定配置（如连接字符串）
    )
    return kb


def create_milvus_knowledgebase(index_name: str = "company_docs") -> KnowledgeBase:
    """
    创建 Milvus 向量数据库知识库（生产环境示例）。

    需要 Milvus 服务运行在 localhost:19530。
    """
    kb = KnowledgeBase(
        backend="milvus",
        index=index_name,
        top_k=5,
        backend_config={
            "host": "localhost",
            "port": 19530,
            "collection_name": index_name,
            "dimension": 1536,  # 向量维度（根据 embedding 模型调整）
        },
    )
    return kb


def create_viking_knowledgebase(index_name: str = "company_docs") -> KnowledgeBase:
    """
    创建火山 VikingDB 知识库（火山云环境）。
    """
    kb = KnowledgeBase(
        backend="viking",
        index=index_name,
        top_k=5,
        backend_config={
            "host": "api-vikingdb.volces.com",
            "region": "cn-beijing",
            "ak": os.getenv("VOLC_ACCESSKEY", ""),
            "sk": os.getenv("VOLC_SECRETKEY", ""),
            "collection_name": index_name,
        },
    )
    return kb


def populate_knowledgebase(kb: KnowledgeBase, docs_dir: Path):
    """向知识库导入文档。"""
    # 方式一：从目录批量导入（支持 .md/.txt/.pdf/.docx 等格式）
    success = kb.add_from_directory(str(docs_dir))
    if success:
        print(f"✅ 文档已从目录导入: {docs_dir}")
    else:
        print(f"❌ 目录导入失败")

    # 方式二：从文件列表导入
    # kb.add_from_files([str(docs_dir / "annual-leave-policy.md")])

    # 方式三：直接添加文本
    kb.add_from_text([
        "公司名称：火山智联科技有限公司",
        "成立时间：2020年3月",
        "CEO：张明华",
        "员工总数：约500人",
        "办公地址：北京市海淀区中关村软件园",
    ])
    print("✅ 附加文本知识已导入")


# ── 步骤 3：手动检索测试 ──

def test_search(kb: KnowledgeBase):
    """测试知识库检索（不通过 Agent，直接搜索）。"""
    print("\n=== 知识库检索测试 ===")

    queries = [
        "年假有多少天？",
        "远程办公怎么申请？",
        "公司用什么数据库？",
        "公司在哪里？",
    ]

    for query in queries:
        results = kb.search(query, top_k=2)
        print(f"\n🔍 查询: {query}")
        for i, entry in enumerate(results):
            content = entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
            score = getattr(entry, 'score', 'N/A')
            print(f"   [{i+1}] (score={score}) {content}")


# ── 步骤 4：创建挂载知识库的 Agent ──

def create_rag_agent(kb: KnowledgeBase) -> Agent:
    """
    创建挂载知识库的 RAG Agent。

    当 Agent 挂载 knowledgebase 参数后，VeADK 自动：
    1. 为 Agent 添加一个检索工具（如 knowledgebase_retrieval）
    2. 在系统指令中注入知识库使用指南
    3. Agent 在回答问题时会自动判断是否需要检索
    """
    agent = Agent(
        name="hr_assistant",
        description="公司HR助手，回答员工关于公司政策、福利、技术规范的问题",
        instruction=(
            "你是公司的HR智能助手。你必须严格依据知识库中的内容回答员工问题。"
            "回答规则："
            "1. 回答问题前，先使用知识库检索工具查找相关信息"
            "2. 只根据检索到的内容回答，不要编造信息"
            "3. 如果知识库中没有相关信息，明确告知用户'这个问题我暂时无法回答，建议咨询HR部门'"
            "4. 回答要简洁明了，分点列出关键信息"
            "5. 用中文回答"
        ),
        knowledgebase=kb,  # 挂载知识库 → 自动添加检索工具
    )
    return agent


# ── 步骤 5：RAG Agent 对话演示 ──

async def rag_demo(agent: Agent):
    """演示 RAG Agent 的对话效果。"""
    runner = Runner(
        agent=agent,
        app_name="kb_rag_demo",
    )

    questions = [
        "我入职3年了，年假有几天？",
        "我可以每周三都远程办公吗？",
        "公司后端用什么编程语言？",
        "公司的下午茶福利是什么？",  # 知识库中没有的信息
    ]

    session_id = "rag-demo-session"
    print("\n=== RAG Agent 对话演示 ===")

    for q in questions:
        print(f"\n👤 员工: {q}")
        answer = await runner.run(
            messages=q,
            session_id=session_id,
        )
        print(f"🤖 HR助手: {answer}")


# ── 主入口 ──

async def main():
    print("=== VeADK 知识库 RAG 示例 ===\n")

    # 准备临时文档目录
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = Path(tmpdir) / "company_docs"

        # 1. 创建示例文档
        create_sample_docs(docs_dir)

        # 2. 创建知识库（使用本地内存后端）
        kb = create_local_knowledgebase("company_docs")

        # 3. 导入文档
        populate_knowledgebase(kb, docs_dir)

        # 4. 直接检索测试
        test_search(kb)

        # 5. 创建 RAG Agent 并对话
        agent = create_rag_agent(kb)
        await rag_demo(agent)

        # 6. 释放资源
        kb.close()

    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    # 注意：使用 local 后端需要配置 embedding 模型
    # 可通过环境变量指定：
    #   export OPENAI_API_KEY=sk-xxx
    # 或使用火山方舟 embedding：
    #   export ARK_API_KEY=xxx
    #   并在 KnowledgeBase 中配置 embedding 模型
    asyncio.run(main())
```

## 逐步解释

### KnowledgeBase 架构

```
┌─────────────────────────────────────────────┐
│                  Agent                       │
│  自动获得 retrieval_tool                     │
│  → 判断是否需要检索 → 调用工具 → 基于结果回答  │
└──────────────────┬──────────────────────────┘
                   │ 检索调用
┌──────────────────▼──────────────────────────┐
│              KnowledgeBase                   │
│  - top_k 检索数量                            │
│  - add_from_directory/files/text()           │
│  - search(query) → List[KnowledgebaseEntry]  │
└──────────────────┬──────────────────────────┘
                   │ 委托
┌──────────────────▼──────────────────────────┐
│         BaseKnowledgebaseBackend             │
│  ┌──────────┐ ┌────────┐ ┌────────┐         │
│  │  local   │ │ milvus │ │ viking │  ...    │
│  │ (内存)   │ │        │ │(火山)  │         │
│  └──────────┘ └────────┘ └────────┘         │
│  Embedding → 向量存储 → 相似度检索           │
└─────────────────────────────────────────────┘
```

### 步骤 1：创建 KnowledgeBase

`KnowledgeBase` 是一个 Pydantic BaseModel，核心参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backend` | str/BaseKnowledgebaseBackend | `"local"` | 向量后端类型：local/milvus/opensearch/viking/redis/tos_vector/context_search/openviking |
| `index` | str | `""` | 索引名称（类似数据库表名），必须提供或通过 app_name 推导 |
| `top_k` | int | `10` | 默认检索返回的最相关文档数量 |
| `backend_config` | dict | `{}` | 后端特定配置（连接地址、认证信息等） |
| `name` | str | `"user_knowledgebase"` | 知识库名称 |
| `description` | str | 描述 | 知识库描述（供 Agent 理解） |
| `enable_profile` | bool | `False` | 是否启用分库（Profile）模式 |
| `query_with_user_profile` | bool | `False` | 是否结合用户画像检索（需 VikingDB） |

### 步骤 2：导入文档

三种导入方式：

| 方法 | 参数 | 说明 |
|------|------|------|
| `add_from_directory(directory)` | 目录路径 | 批量导入目录下所有支持的文件（.md/.txt/.pdf/.docx/.html 等） |
| `add_from_files(files)` | 文件路径列表 | 导入指定文件列表 |
| `add_from_text(text)` | str 或 str列表 | 直接导入纯文本内容 |

导入时自动执行：文档解析 → 分块（Chunking）→ Embedding 向量化 → 存入向量后端。

### 步骤 3：支持的后端

| 后端 | backend 值 | 适用场景 | 需要的 backend_config |
|------|-----------|---------|---------------------|
| 内存 | `"local"` | 开发测试、小数据量 | 无需（但需安装 extensions） |
| Milvus | `"milvus"` | 生产环境、自托管 | host, port, collection_name, dimension |
| OpenSearch | `"opensearch"` | AWS/生产环境 | hosts, index_name, ... |
| VikingDB | `"viking"` | 火山云环境 | host, region, ak, sk, collection_name |
| Redis | `"redis"` | 轻量生产 | host, port, index_name |
| TOS Vector | `"tos_vector"` | 火山 TOS | bucket, endpoint, ak, sk |
| Context Search | `"context_search"` | 火山语义搜索服务 | 服务特定配置 |
| OpenViking | `"openviking"` | 火山 OpenViking | 资源配置 |

### 步骤 4：挂载到 Agent

将 `knowledgebase=kb` 参数传给 Agent 构造函数后，VeADK 自动：
1. 创建检索工具（允许 Agent 按关键词搜索知识库）
2. 在 Agent 的工具列表中注册该工具
3. Agent 在 Think 阶段自主判断是否需要调用检索工具

### 步骤 5：RAG 对话流程

```
用户提问 → Agent 判断需要检索 → 调用 retrieval_tool(query)
         → KnowledgeBase.search(query) → 返回 top_k 相关片段
         → Agent 基于检索结果生成回答 → 返回给用户
```

关键设计：
- Agent 自主决定何时检索（不是每次都检索）
- 指令中需强调"先检索后回答"，避免 Agent 凭记忆回答
- 检索结果作为上下文注入 Agent 的消息流
- 检索不到时，Agent 应如实告知而非编造

### KnowledgebaseEntry

检索返回的条目对象：
- `content: str`：文档片段内容
- `score: float`：相似度分数（可选，取决于后端）
- `metadata: dict`：元数据（来源文件、页码等，可选）

## 输出结果

运行脚本后，预期输出类似：

```
=== VeADK 知识库 RAG 示例 ===

✅ 示例文档已创建: /tmp/xxx/company_docs
   - annual-leave-policy.md
   - remote-work-policy.md
   - tech-stack.md
✅ 文档已从目录导入: /tmp/xxx/company_docs
✅ 附加文本知识已导入

=== 知识库检索测试 ===

🔍 查询: 年假有多少天？
   [1] (score=0.89) # 年假政策\n\n## 年假天数\n- 入职满1年不满5年：年假5天...
   [2] (score=0.82) ## 年假使用规则\n1. 年假最小使用单位为0.5天...

🔍 查询: 远程办公怎么申请？
   [1] (score=0.87) # 远程办公政策\n\n## 适用条件\n- 入职满3个月...

=== RAG Agent 对话演示 ===

👤 员工: 我入职3年了，年假有几天？
🤖 HR助手: 根据公司年假政策，您入职满1年不满5年，年假为5天。
   年假使用规则：
   - 最小使用单位为0.5天
   - 需提前3个工作日申请
   - 可跨年度使用（次年3月31日前）

👤 员工: 公司的下午茶福利是什么？
🤖 HR助手: 这个问题我暂时无法回答，建议咨询HR部门。
```

## 注意事项

1. **必须安装 extensions 依赖**：向量存储和文档解析功能在扩展包中，需要 `pip install "veadk-python[extensions]"`。否则 local 后端会报 ImportError。

2. **Embedding 模型配置**：知识库需要 Embedding 模型将文本转为向量。确保配置了正确的 API Key 和 embedding 模型名称。环境变量 `OPENAI_API_KEY` 或 `ARK_API_KEY` 等需要正确设置。

3. **local 后端数据不持久**：`backend="local"` 使用内存存储，程序退出后数据丢失。仅用于开发测试，生产环境必须使用 Milvus/VikingDB 等持久化后端。

4. **文档分块策略**：文档导入时自动分块，默认分块大小适合通用场景。对于特殊文档（如代码、表格），可考虑预处理后用 `add_from_text()` 以自定义分块导入。

5. **top_k 调优**：`top_k` 控制检索返回的片段数。过小会遗漏信息，过大会引入噪声并增加 Token 消耗。建议从 3-5 开始调优。

6. **指令工程很重要**：Agent 的 instruction 必须明确要求"先检索后回答""未检索到则如实告知"，否则 Agent 可能跳过检索直接凭模型记忆回答，产生幻觉。

7. **文件格式支持**：`add_from_directory()` 支持的格式取决于安装的解析器。`.md`/`.txt` 原生支持，PDF/DOCX 需要额外依赖（如 `pypdf`、`python-docx`）。

8. **index 命名规范**：在持久化后端（如 Milvus）中，index/collection 名称是全局的。不同应用使用不同 index 名称，避免数据混淆。

9. **资源释放**：使用完毕后调用 `kb.close()` 释放后端连接。在 Web 服务等长驻进程中，通常只创建一个 KnowledgeBase 实例复用。

10. **Profile 分库**：多租户场景可启用 `enable_profile=True` 和 `query_with_user_profile=True`，结合用户画像实现个性化检索（需 VikingDB 后端支持）。

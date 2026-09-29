---
type: example
title: "使用 Modelfile 自定义模型"
bundle: /datawhale/handy-ollama
description: "从 GGUF 文件创建自定义模型，配置 SYSTEM 提示词和 PARAMETER 参数，构建专属角色模型"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C3
related:
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/concepts/ollama-architecture-installation
  - /datawhale/handy-ollama/references/chapter3-customization
tags: [modelfile, custom-model, gguf, system-prompt, parameters]
status: stable
---

# 使用 Modelfile 自定义模型

## 目标

掌握 Modelfile 的三种使用方式：从 GGUF 文件导入模型、基于已有模型定制角色、配置推理参数，创建一个专属的自定义模型。

## 场景一：从 GGUF 文件导入模型

GGUF 是 Ollama 原生支持的模型格式，适合从 HuggingFace 等平台下载社区量化模型。

### 步骤

1. **下载 GGUF 模型文件**

   从 HuggingFace 下载一个小型 GGUF 模型（如 Qwen2-0.5B 量化版，约几百 MB）：

   ```
   https://huggingface.co/RichardErkhov/Qwen_-_Qwen2-0.5B-gguf/resolve/main/Qwen2-0.5B.Q3_K_M.gguf
   ```

2. **创建 Modelfile**

   在 GGUF 文件所在目录创建名为 `Modelfile` 的文件：

   ```dockerfile
   FROM ./Qwen2-0.5B.Q3_K_M.gguf
   ```

3. **创建并运行模型**

   ```bash
   # 在 Modelfile 所在目录执行
   ollama create mymodel -f Modelfile
   ollama run mymodel
   ```

4. **验证**

   ```
   >>> 你好
   你好！有什么可以帮助你的吗？
   ```

## 场景二：基于已有模型定制角色

不重新下载权重，仅通过 SYSTEM 提示词改变模型行为，这是最常用的自定义方式。

### 步骤

1. **创建 Modelfile**

   ```dockerfile
   FROM llama3.1

   SYSTEM """
   你是一位名叫"小O"的AI助手，具有以下特点：
   1. 回答简洁明了，每次回复不超过3句话
   2. 擅长用生动的比喻解释技术概念
   3. 回答结尾会附上一个相关的趣味小知识
   """

   PARAMETER temperature 0.8
   PARAMETER top_p 0.9
   ```

2. **创建模型**

   ```bash
   ollama create xiao-o -f Modelfile
   ```

3. **运行并对比**

   ```bash
   ollama run xiao-o
   ```

   ```
   >>> 解释什么是递归
   递归就像两面相对的镜子——函数在镜子中调用自己，无限延伸直到遇到"基底情形"这面墙才停止。
   
   趣味小知识：世界上最短的递归程序是一行代码的死循环！
   ```

   对比原始模型 `ollama run llama3.1`，可明显看到 SYSTEM 提示词改变了回答风格。

## 场景三：配置推理参数

通过 `PARAMETER` 指令精细控制模型生成行为。

### 常用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | float | 0.8 | 温度越高输出越随机，越低越确定 |
| `top_p` | float | 0.9 | 核采样概率阈值 |
| `top_k` | int | 40 | Top-K 采样范围 |
| `num_ctx` | int | 2048 | 上下文窗口大小 |
| `num_predict` | int | 128 | 最大生成 token 数（-1 为无限） |
| `stop` | string | - | 停止序列（可多次设置） |
| `seed` | int | - | 随机种子，固定值可复现输出 |
| `repeat_penalty` | float | 1.1 | 重复惩罚系数 |

### 示例：精确型助手

```dockerfile
FROM llama3.1

SYSTEM "你是一个精确的技术助手，只回答有把握的内容，不确定时明确说明。"

PARAMETER temperature 0.1
PARAMETER top_p 0.5
PARAMETER num_ctx 4096
PARAMETER stop "###"
PARAMETER repeat_penalty 1.2
```

```bash
ollama create precise-assistant -f Modelfile
```

低 temperature + 低 top_p + 高 repeat_penalty 组合产生精确、少重复的技术回答。

### 示例：创意写作助手

```dockerfile
FROM llama3.1

SYSTEM "你是一位创意写作教练，擅长发散思维和头脑风暴。"

PARAMETER temperature 1.2
PARAMETER top_p 0.95
PARAMETER top_k 100
PARAMETER num_predict 512
```

高 temperature + 高 top_k 鼓励创意和多样性。

## 场景四：自定义提示词模板

对于特殊格式需求，可使用 `TEMPLATE` 指令定义完整的对话模板：

```dockerfile
FROM llama3.1

TEMPLATE """
{{- if .System }}<|system|>
{{ .System }}
{{- end }}
{{- range .Messages }}<|{{ .Role }}|>
{{ .Content }}
{{- end }}<|assistant|>
"""

SYSTEM "你是一个友好的助手。"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"
```

模板变量：
- `.System`：系统提示词
- `.Messages`：消息列表，每条含 `.Role` 和 `.Content`
- `.Prompt`：当前用户输入

## 管理自定义模型

```bash
# 列出所有模型（包括自定义的）
ollama list

# 查看自定义模型的详细配置
ollama show xiao-o

# 复制模型
ollama cp xiao-o xiao-o-backup

# 删除模型
ollama rm xiao-o-backup

# 修改 Modelfile 后重新创建（更新模型）
ollama create xiao-o -f Modelfile
```

## 验证结果

成功标志：

1. `ollama create` 命令成功完成，无报错
2. `ollama list` 中能看到自定义模型
3. `ollama run <自定义模型名>` 能进入对话，且回答风格符合 SYSTEM 设定
4. `ollama show <模型名>` 显示配置的 PARAMETER 值

## 最佳实践

1. **版本化 Modelfile**：将 Modelfile 纳入 Git 管理，模型配置可追溯、可复现
2. **从小模型开始**：调试 Modelfile 时使用 1B-3B 小模型，快速验证效果后再换到 7B+
3. **SYSTEM 提示词要具体**：明确的角色、约束和示例比模糊描述效果更好
4. **参数组合调优**：temperature 和 top_p 通常一起调整，不要同时设到极值
5. **使用 stop 序列**：正确设置 stop 序列可防止模型生成多余的对话轮次

## 延伸阅读

- Modelfile 完整指令和机制详解 → [模型管理与 Modelfile](../concepts/model-management-modelfile.md)
- Ollama 架构和 CLI 命令 → [Ollama 架构与安装](../concepts/ollama-architecture-installation.md)
- 构建更复杂的 RAG 应用 → [搭建本地 RAG 应用](local-rag-application.md)

---
type: spec
title: sphinx-proof 源码事实清单
description: sphinx-proof 源码事实清单
tags:
- sphinx-proof
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-proof-source
  resource: /references/proof-source.md
  title: sphinx-proof proof-source
---

# sphinx-proof 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 包名为 `sphinx-proof`，为 Sphinx 文档添加数学定理/证明环境
- F-002: 核心 Python 文件 4 个：`__init__.py`（207行）、`directive.py`（163行）、`domain.py`、`nodes.py`、`proof_type.py`（120行）
- F-003: 静态资源：`_static/proof.css`（标准主题）、`_static/minimal/proof.css`（简约主题）
- F-004: 消息目录名 `"proof"`，使用 `sphinx.locale.get_translation()` 加载翻译

## PROOF_TYPES 定理类型

- F-005: 共 15 种可编号定理类型，均继承 `ElementDirective`
- F-006: 类型列表：axiom（公理）、theorem（定理）、lemma（引理）、algorithm（算法）、definition（定义）、remark（备注）、conjecture（猜想）、corollary（推论）、criterion（准则）、example（示例）、property（性质）、observation（观察）、proposition（命题）、assumption（假设）、notation（记号）
- F-007: 每个类型在 `proof_type.py` 中定义独立类，仅设置 `name` 属性
- F-008: `PROOF_TYPES` 字典映射类型名→指令类

## ElementDirective（可编号元素指令）

- F-009: 所有定理类型共享 `ElementDirective` 基类，`has_content = True`
- F-010: `required_arguments = 0`，`optional_arguments = 1`（可选标题参数）
- F-011: option_spec：`label`（unchanged_required）、`class`（class_option）、`nonumber`（flag）
- F-012: `realtyp = self.name.split(":")[1]` 获取指令名（Sphinx domain 格式）
- F-013: `countertyp` 通过 `prf_realtyp_to_countertyp` 配置映射，默认每种类型独立计数
- F-014: CSS 类固定为 `["proof", realtyp]`，附加自定义 class
- F-015: label 未指定时自动生成：`{realtyp}-{serial_no}`
- F-016: 重复 label 输出红色警告
- F-017: 标题格式通过 `proof_title_format` 配置控制，默认为 `" (%t)"`（`%t` 替换为标题文本）
- F-018: `:nonumber:` 标志使用 `unenumerable_node`，否则使用对应类型的 enumerable node
- F-019: 节点属性：ids、classes、title、label、countertype、realtype
- F-020: 注册表 `env.proof_list[label]` 存储 docname、countertype、realtype、ids、label、prio、nonumber

## ProofDirective（证明指令）

- F-021: `name = "proof"`，`has_content = True`，无必填参数
- F-022: option_spec 仅有 `class`（class_option），无 label/nonumber 选项
- F-023: 使用 `nodes.admonition()` 创建 admonition 节点
- F-024: 第一行内容自动添加"Proof. "前缀：`self.content[0] = "{}. ".format(realtyp.title()) + self.content[0]`
- F-025: 返回 `proof_node` 节点，非 enumerable（无编号）

## 节点类型（nodes.py）

- F-026: `proof_node`：证明节点（admonition 类型），非编号
- F-027: `unenumerable_node`：无编号定理节点
- F-028: `NODE_TYPES` 字典：15种类型→动态生成的 enumerable 节点类
- F-029: 每种 enumerable 节点通过 `add_enumerable_node()` 注册，使用类型名作为 figtype

## 配置项

- F-030: `proof_minimal_theme`（bool，默认 False）：使用简约 CSS 主题
- F-031: `prf_realtyp_to_countertyp`（dict，默认 {}）：跨类型共享编号映射
- F-032: `proof_title_format`（str，默认 `" (%t)"`）：标题格式模板
- F-033: `proof_number_weight`（str，默认 ""）：编号字体粗细 CSS 值
- F-034: `proof_title_weight`（str，默认 ""）：标题字体粗细 CSS 值

## setup() 与事件

- F-035: `init_numfig()` 自动为所有 NODE_TYPES 设置 `numfig_format = {typ: typ + " %s"}`
- F-036: `check_config_values()` 验证配置类型，非法值输出警告并回退默认值
- F-037: `copy_asset_files()` 根据 `proof_minimal_theme` 选择 CSS 文件，支持运行时修改 CSS 字体粗细
- F-038: `purge_proofs()` 在 env-purge-doc 时清理注册表
- F-039: `merge_proofs()` 在 env-merge-info 时合并并行构建注册表
- F-040: `app.add_domain(ProofDomain)` 注册自定义域用于交叉引用
- F-041: CSS 通过字符串替换修改：读取 proof.css，替换 font-weight 值后写回输出目录
- F-042: 返回 `parallel_read_safe: True, parallel_write_safe: True`

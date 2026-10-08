---
type: reference
title: "EmotiVoice 信源登记（v0.3 @ 59f0f36）"
tags: [emotivoice, tts, source-registry, netease-youdao]
sources:
  - id: emotivoice-repo
    resource: vendor/netease-youdao/EmotiVoice/
    title: EmotiVoice 源码仓库（git submodule，固定基线 59f0f36，tag v0.3）
---

# EmotiVoice 信源登记

本文件登记 EmotiVoice 知识包（bundle）的上游信源与固定基线，供 [facts.md](facts.md)、[insights.md](insights.md) 及后续 concepts/、examples/ 文档的 `sources` 字段引用。

## 上游仓库

| 项 | 值 |
|---|---|
| 上游 URL | `git@github.com:netease-youdao/EmotiVoice.git`（GitHub 只读引用） |
| 本地信源路径 | `vendor/netease-youdao/EmotiVoice/`（SpecWeave vendor 子模块，第三方依赖，禁止本地修改） |
| 固定 tag | `v0.3`（tag commit：`0ade5e3df226b36da7ecb09485b303580395388c`） |
| Pin commit（子模块当前 HEAD） | `59f0f36de4db12825f4705dd4e0780d79dd6bb01` |
| 基线说明 | pin commit 为 tag v0.3 之后 17 个提交（`git describe` 输出 `v0.3-17-g59f0f36`），最近提交时间 2026-09-03，主题 "update"；事实采集与洞察均以此 pin commit 为准，而非 tag v0.3 本身 |
| 基线核验方式 | `git -C vendor/netease-youdao/EmotiVoice rev-parse HEAD`、`git -C vendor/netease-youdao/EmotiVoice rev-list -n 1 v0.3`、`git -C vendor/netease-youdao/EmotiVoice log -1` |
| 许可证 | Apache-2.0（见仓库根 `LICENSE`） |

> **信源稳定性声明**：信源位于 vendor/ 子模块（stable 类路径），非临时克隆；文档中所有信源引用仅指向 `vendor/netease-youdao/EmotiVoice/`，不含 `file:///` 绝对路径与临时目录段。若子模块升级，须重新采集事实并同步更新本登记与 facts.md 的基线字段。

## 关键信源文件清单

以下文件为 facts.md（F-ev-001~042）的事实来源，按功能分组：

### 入口、推理与服务化

- `README.md` —— 安装/推理命令、推理文本格式、ROADMAP（许可证与 style factors 声明）
- `inference_am_vocoder_joint.py` —— 联合推理主入口（F-ev-001）
- `inference_tts.py` —— 多进程推理、风格嵌入获取（F-ev-020、F-ev-021、F-ev-025）
- `openaiapi.py` —— FastAPI OpenAI 兼容服务（F-ev-012、F-ev-033~035）
- `demo_page.py` —— Streamlit 交互页（F-ev-036）

### 文本前端（中英双语 g2p）

- `frontend.py` —— `g2p_cn_en` 中英混合入口、命令行用法（F-ev-004、F-ev-005）
- `frontend_cn.py` —— 中文 jieba/pypinyin 管线、数字转中文、拼音切分（F-ev-006~009）
- `frontend_en.py` —— 英文 lexicon/g2p_en 管线（F-ev-010~012）
- `text/symbols.py`、`text/__init__.py`、`text/cleaners.py`、`text/cmudict.py`、`text/numbers.py` —— 符号表、序列化、清洗器与 ARPAbet（F-ev-013~017）
- `cn2an/` —— vendored cn2an（仅 `an2cn.py`、`conf.py`，F-ev-041）

### 模型与训练

- `models/prompt_tts_modified/jets.py` —— JETSGenerator 内嵌结构（F-ev-018、F-ev-019）
- `models/prompt_tts_modified/simbert.py` —— StyleEncoder 与分类头（F-ev-024）
- `models/prompt_tts_modified/prompt_dataset.py` —— 数据集、风格嵌入缓存、collate（F-ev-026）
- `models/hifigan/models.py`、`models/hifigan/get_vocoder.py` —— HiFiGAN 生成器/判别器与 vocoder 加载（F-ev-022、F-ev-023）
- `config/joint/config.py`、`config/joint/config.yaml` —— 超参与标签计数逻辑（F-ev-029、F-ev-030）
- `train_am_vocoder_joint.py` —— DDP 联合训练循环与损失组合（F-ev-031、F-ev-032）

### 数据与对齐

- `data/youdao/text/` —— 说话人/词表/情绪/标签文件与 voice wiki（F-ev-027、F-ev-028）
- `mfa/` —— MFA 对齐流水线 8 个 step 脚本（F-ev-037、F-ev-038）

### 依赖

- `requirements.txt`（13 项核心依赖，F-ev-039）、`requirements.openaiapi.txt`（5 项服务化依赖，F-ev-040）

## 相关说明

- 本登记与 facts.md 的 `sources` frontmatter 指向同一 vendor 子模块；facts.md 的 frontmatter 附完整文件级清单，两者互为冗余备份，冲突时以本文件（含 pin commit 与 tag 双基线）为准。
- 未覆盖/存疑项（见 facts.md「未覆盖/存疑项」）涉及的文件（`models/prompt_tts_modified/` 下 encoder/decoder/variance_adaptor 等、`models/hifigan/` 下 env/dataset/pretrained_discriminator 等）尚未细读，E 阶段如需引用须先回读源码补采事实。

---
type: Example
title: 用程序检查 Agent 的引用
sources:
  - {id: contract, resource: ../concepts/04-transcript-contract.md}
  - {id: analysis, resource: ../concepts/05-agent-analysis.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 用程序检查 Agent 的引用

输入是已按[片段契约](../concepts/04-transcript-contract.md)检查过的定稿记录，以及 Agent 返回的 `claims` 列表。输出是错误字符串数组；非空时拒绝接受本次结果。函数只验证引用身份和文本匹配，不验证论证逻辑，也不代替完整 JSON Schema 校验。

## 引用验证函数

```python
def check_claims(records, claims):
    errors = []
    allowed_kinds = {"quote", "paraphrase", "inference"}
    evidence = {}
    seen_ids = set()
    for record in records:
        segment_id = record["segment_id"]
        if segment_id in seen_ids:
            errors.append(f"multiple current records: {segment_id}")
        seen_ids.add(segment_id)
        if record["status"] != "final":
            continue
        key = (segment_id, record["revision"])
        evidence[key] = record
    for number, claim in enumerate(claims, 1):
        if claim.get("kind") not in allowed_kinds:
            errors.append(f"claim {number}: invalid kind")
        if not isinstance(claim.get("text"), str) or not claim["text"].strip():
            errors.append(f"claim {number}: empty text")
        refs = claim.get("evidence")
        if not isinstance(refs, list) or not refs:
            errors.append(f"claim {number}: missing evidence")
            continue
        for ref in refs:
            key = (ref.get("segment_id"), ref.get("revision"))
            record = evidence.get(key)
            if record is None:
                errors.append(f"claim {number}: unknown evidence {key}")
                continue
            quote = ref.get("quote")
            if not isinstance(quote, str) or not quote.strip() or quote not in record["text"]:
                errors.append(f"claim {number}: quote mismatch {key}")
    return errors
```

调用前由 schema 约束 `claims` 是对象数组、`evidence` 是对象数组、`revision` 是正整数；不要把任意恶意 JSON 直接交给这个教学函数。单会话调用，跨会话汇总时必须把 `session_id` 也纳入索引键。

## 正负样本

以下文字只是程序测试夹具，不来自直播，不构成调研证据或识别准确率数据。

```python
from copy import deepcopy

records = [{
    "segment_id": "fixture-s1",
    "revision": 1,
    "status": "final",
    "text": "先保存原音频，再检查转录。",
}]
valid = [{
    "kind": "paraphrase",
    "text": "建议先保留音频。",
    "evidence": [{
        "segment_id": "fixture-s1",
        "revision": 1,
        "quote": "先保存原音频",
    }],
}]
assert check_claims(records, valid) == []

unknown = deepcopy(valid)
unknown[0]["evidence"][0]["segment_id"] = "absent"
assert len(check_claims(records, unknown)) == 1

wrong_quote = deepcopy(valid)
wrong_quote[0]["evidence"][0]["quote"] = "可以删除原音频"
assert len(check_claims(records, wrong_quote)) == 1

wrong_revision = deepcopy(valid)
wrong_revision[0]["evidence"][0]["revision"] = 2
assert len(check_claims(records, wrong_revision)) == 1

uncommitted = deepcopy(records)
uncommitted[0]["status"] = "provisional"
assert len(check_claims(uncommitted, valid)) == 1
assert len(check_claims(records + records, valid)) == 1

missing = deepcopy(valid)
missing[0]["evidence"] = []
assert len(check_claims(records, missing)) == 1

empty_quote = deepcopy(valid)
empty_quote[0]["evidence"][0]["quote"] = ""
assert len(check_claims(records, empty_quote)) == 1

invalid_kind = deepcopy(valid)
invalid_kind[0]["kind"] = "proven-fact"
assert len(check_claims(records, invalid_kind)) == 1

revised = deepcopy(records)
revised[0]["revision"] = 2
assert len(check_claims(revised, valid)) == 1
assert check_claims(revised, wrong_revision) == []
assert len(check_claims(records + revised, valid)) == 1
revised[0]["status"] = "provisional"
assert len(check_claims(revised, wrong_revision)) == 1
assert len(check_claims(records + revised, valid)) == 1

unsupported = deepcopy(valid)
unsupported[0]["text"] = "原音频永远不用保存。"
assert check_claims(records, unsupported) == []
```

最后一个断言故意保留：引文真实且 ID 合法，结论仍然可能相反。它验证程序的能力边界，不能删掉后宣称实现了自动事实核验。

把以上两个代码块按顺序保存到本地 `test_evidence.py`，使用 Python 运行，正常完成应退出 0；断言不满足会非零退出。此命令仅自测，不会读取刚生成的转录和 Agent 结果。15 条断言包含旧版本失效、修订混入拒绝和语义错误可漏过的边界。实际执行记录见[验证记录](../references/verification.md)。

## 读取自己的转录与分析

将第一个函数代码块与下面代码按顺序保存成 `check_evidence.py`，不要混入上述自测数据。在独立环境安装 `jsonschema`（安装会联网；校验本身不联网）。首次分析只要求 Agent 输出 `{"claims": [...]}`，每项含 `text`、`kind` 和非空 `evidence`，可以把 `CLAIMS_SCHEMA` 作为本地 Ollama 的 `format` 值；本例不替你调用模型。

```python
import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

TEXT = {"type": "string", "minLength": 1}
REF_SCHEMA = {
    "type": "object",
    "required": ["segment_id", "revision", "quote"],
    "additionalProperties": False,
    "properties": {
        "segment_id": TEXT,
        "revision": {"type": "integer", "minimum": 1},
        "quote": TEXT,
    },
}
CLAIMS_SCHEMA = {
    "type": "object",
    "required": ["claims"],
    "additionalProperties": False,
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["text", "kind", "evidence"],
                "additionalProperties": False,
                "properties": {
                    "text": TEXT,
                    "kind": {"enum": ["quote", "paraphrase", "inference"]},
                    "evidence": {"type": "array", "minItems": 1, "items": REF_SCHEMA},
                },
            },
        },
    },
}
RECORD_PROPERTIES = {
    "schema_version": {"const": "1.0"},
    "session_id": TEXT,
    "segment_id": TEXT,
    "revision": {"type": "integer", "minimum": 1},
    "status": {"enum": ["provisional", "final"]},
    "media_id": TEXT,
    "audio_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "start_ms": {"type": "integer", "minimum": 0},
    "end_ms": {"type": "integer", "minimum": 1},
    "text": TEXT,
    "speaker": {"type": ["string", "null"]},
    "quality_flags": {"type": "array", "items": {"type": "string"}},
}
RECORD_SCHEMA = {
    "type": "object",
    "required": list(RECORD_PROPERTIES),
    "additionalProperties": False,
    "properties": RECORD_PROPERTIES,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", type=Path)
    parser.add_argument("analysis", type=Path)
    args = parser.parse_args()
    errors = []
    records = []
    try:
        transcript_bytes = args.transcript.read_bytes()
        for number, line in enumerate(transcript_bytes.decode("utf-8").splitlines(), 1):
            record = json.loads(line)
            Draft202012Validator(RECORD_SCHEMA).validate(record)
            if record["start_ms"] >= record["end_ms"]:
                errors.append(f"line {number}: invalid time range")
            records.append(record)
        result = json.loads(args.analysis.read_text(encoding="utf-8"))
        Draft202012Validator(CLAIMS_SCHEMA).validate(result)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"输入读取失败: {exc}\n")
    except ValidationError as exc:
        parser.exit(2, f"结构不符合 schema: {exc.message}\n")
    if not records:
        errors.append("empty transcript: no evidence to review")
    if len({record["session_id"] for record in records}) > 1:
        errors.append("mixed sessions")
    errors.extend(check_claims(records, result["claims"]))
    report = {
        "input_snapshot_sha256": hashlib.sha256(transcript_bytes).hexdigest(),
        "checked_claims": len(result["claims"]),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
python -m pip install jsonschema
python check_evidence.py "session-001/segments.jsonl" "claims.json"
```

`claims.json` 必须是纯 JSON，不带 Markdown 围栏。退出 0 表示结构与本次输入内的引用检查通过，1 表示引用或快照不合要求，2 表示文件或结构错误。空 claims 可以通过，但报告的 `checked_claims=0` 不能算完成分析；空转录拒绝分析，应先检查采集/静音问题。

宿主必须先验证结果绑定的输入快照与当前快照相同，再运行此命令；输出的 SHA-256 只标识本次实际读取文件，不能证明模型当时读取了它。每次仅传入单会话的当前快照，不把历史修订档案拼进来。脚本检查散列字段格式，不打开媒体核对实际散列，也不检查时间戳是否准确，更不验证结论是否被原话支持。这里只校验 claims；主题、行动与缺口的完整 schema 属于后续扩展。


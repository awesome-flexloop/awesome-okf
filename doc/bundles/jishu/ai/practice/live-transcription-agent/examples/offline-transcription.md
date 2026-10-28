---
type: Example
title: 已关闭 WAV 转为 Agent 可读 JSONL
sources:
  - {id: faster-whisper, resource: "https://github.com/SYSTRAN/faster-whisper"}
  - {id: contract, resource: ../concepts/04-transcript-contract.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 已关闭 WAV 转为 Agent 可读 JSONL

输入是有权处理、已停止写入的 16 kHz、16-bit、单声道 PCM WAV，以及已下载的 faster-whisper/CTranslate2 模型目录。输出是新目录中的 `segments.jsonl` 与 `manifest.json`。本示例不是直播监听器，不接 URL，不自动下载模型，也不执行 Agent 分析。

本例把输入 WAV 本身登记为证据媒体，时间零点是它的首个采样，只保证引用回到这个 WAV，不自动对齐原视频。视频与 WAV 的起点可能不同；原视频映射未知时记录 `null`，不能当成零。需要回查视频时，另行核对音轨首采样、容器 PTS、解码延迟及分段偏移，并保存映射与误差，见[时间轴契约](../concepts/04-transcript-contract.md)。

## 环境准备

代码使用 `hashlib.file_digest`，要求 Python 3.11 或更高版本。在独立虚拟环境安装适合当前 Python、操作系统与加速后端的 faster-whisper；具体 wheel 支持以当前发行版为准，不能把知识库自身的 Python 3.14 要求套到所有 ASR 依赖。

```bash
python -m venv .venv
```

激活方式：PowerShell 使用 `.venv/Scripts/Activate.ps1`；Linux/macOS shell 使用 `source .venv/bin/activate`。如 PowerShell 策略不允许激活，可直接调用 `.venv/Scripts/python.exe`，不要为本示例放宽系统执行策略。

```bash
python -m pip install faster-whisper
python -m pip freeze > requirements-lock.txt
```

安装与模型下载会联网，属于操作者自选步骤，本次调研没有执行。上游 [`download_model`](https://github.com/SYSTRAN/faster-whisper/blob/9e472ae9de8bb374552f531f752654554b76b2d6/faster_whisper/utils.py) 提供模型下载入口。先在其指向的模型仓库核对许可和完整提交号，将下面的 `MODEL_COMMIT` 换成该模型仓库的提交号（不是 faster-whisper 代码提交号），在新目录运行：

```bash
python -c "from faster_whisper.utils import download_model; print(download_model('small', output_dir='models/whisper-small-ct2', revision='MODEL_COMMIT'))"
```

模型仓库入口见 [Systran](https://huggingface.co/Systran)；`small` 指多语言模型，不是 `small.en`。下载完成后核对模型、配置、tokenizer 及上游提供的词表/预处理文件均已保存；不能把 OpenAI `.pt` 权重或 whisper.cpp 文件当作 CTranslate2 目录。下面的三个文件检查只拦截显然缺件，不构成完整性证明。长期复现应保存模型 revision、依赖锁定结果和模型文件摘要。

## 完整单文件示例

将以下代码保存为 `transcribe_local.py`。默认 CPU/int8；NVIDIA 选项只有在 CTranslate2 与 CUDA/cuDNN 版本配套时才使用。

```python
import argparse
import hashlib
import importlib.metadata
import json
import wave
from pathlib import Path

from faster_whisper import WhisperModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("media", type=Path)
    parser.add_argument("model", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--language", default="zh")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--compute-type", default="int8")
    args = parser.parse_args()
    if not args.media.is_file() or not args.model.is_dir():
        parser.error("media 必须是已关闭的 WAV，model 必须是已下载模型目录")
    for filename in ("model.bin", "config.json", "tokenizer.json"):
        if not (args.model / filename).is_file():
            parser.error(f"模型缺少 {filename}；拒绝不完整目录与 tokenizer 联网回退")
    try:
        with wave.open(str(args.media), "rb") as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 16000, "NONE"):
                parser.error("仅接受 16 kHz、16-bit、单声道 PCM WAV")
            audio_frames = audio.getnframes()
            if audio_frames == 0:
                parser.error("WAV 没有采样")
    except (wave.Error, EOFError) as exc:
        parser.error(f"无法读取 PCM WAV: {exc}")
    if args.output.exists():
        parser.error("output 必须不存在，避免覆盖之前的证据")
    with args.media.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    model = WhisperModel(
        str(args.model.resolve()),
        device=args.device,
        compute_type=args.compute_type,
        local_files_only=True,
    )
    segments, info = model.transcribe(
        str(args.media.resolve()),
        language=args.language,
        vad_filter=True,
        word_timestamps=True,
    )
    args.output.mkdir(parents=True, exist_ok=False)
    session_id = args.output.name
    media_id = digest[:16]
    part = args.output / "segments.jsonl.part"
    count = 0
    with part.open("x", encoding="utf-8", newline="\n") as stream:
        for number, segment in enumerate(segments):
            if not segment.text.strip():
                continue
            start = round(segment.start * 1000)
            end = round(segment.end * 1000)
            if not 0 <= start < end:
                raise ValueError(f"无效时间区间: {start}, {end}")
            record = {
                "schema_version": "1.0",
                "session_id": session_id,
                "segment_id": f"{media_id}-s{number:06d}",
                "revision": 1,
                "status": "final",
                "media_id": media_id,
                "audio_sha256": digest,
                "start_ms": start,
                "end_ms": end,
                "text": segment.text,
                "speaker": None,
                "quality_flags": ["needs_review"],
            }
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    manifest = {
        "schema_version": "1.0",
        "session_id": session_id,
        "media_id": media_id,
        "input_name": args.media.name,
        "input_sha256": digest,
        "timebase": "input-wav-first-sample",
        "sample_rate": 16000,
        "audio_frames": audio_frames,
        "source_media_mapping": None,
        "model_directory": args.model.name,
        "engine_version": importlib.metadata.version("faster-whisper"),
        "language": info.language,
        "duration_seconds": info.duration,
        "parameters": {
            "device": args.device,
            "compute_type": args.compute_type,
            "vad_filter": True,
            "word_timestamps": True,
        },
        "segments": count,
        "rights": "operator-must-record-separately",
    }
    with (args.output / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    part.rename(args.output / "segments.jsonl")
    print(f"完成: {count} 个片段；仍需人工抽检")


if __name__ == "__main__":
    main()
```

CPU 示例，替换为自己的文件和已下载模型路径：

```bash
python transcribe_local.py "part-0000.wav" "models/whisper-small-ct2" "session-001"
```

适配好 NVIDIA 环境后，可改用 `--device cuda --compute-type float16`。报错时先按上游兼容说明检查依赖，不直接把 CPU 参数照搬到 GPU。[ASR 选型](../concepts/03-local-asr.md)

## 如何判断结果

程序实际遍历 `segments` 生成器才会完成识别。成功目录应有合法 UTF-8 JSONL 和 manifest；失败保留 `.part`，不应消费。空白或静音输入可能产生零条片段，不能把零条一概判成失败，也不能把非空一概判成识别正确。

`final` 只表示这次离线运行已定稿，不表示人工核对过；`needs_review` 明确保留这一点。代码请求词级时间戳，但只导出片段级时间，词级列表没有持久化。多人说话没有自动分离，`speaker` 保持 `null`。

示例用输出目录名作为会话 ID，操作者应保证其唯一；仅在单会话范围内使用引用检查。没有复制或删除原始媒体，也没有把授权判定自动化。正式归档时，应将原媒体纳入受控目录，填写授权、采集缺口和模型版本证据。

本代码的语法检查与实际 ASR 运行是两项不同验证；本机没有安装该识别引擎和权重，也未提供获授权的音频样本，因此不宣称识别成功、准确率或速度。具体记录见[验证页](../references/verification.md)。

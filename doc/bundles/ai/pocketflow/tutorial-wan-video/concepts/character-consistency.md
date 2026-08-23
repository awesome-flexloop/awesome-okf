---
title: 角色一致性策略
type: concept
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/references/generate-image-node
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
---

# 角色一致性策略

AI 图像生成的核心挑战之一是**跨场景角色一致性**——同一角色在独立生成的多张图片中保持外观统一。Wan-Video Generator 采用三层递进的保障机制，结合文本描述、参考图像和链式引用，确保 Mia 和 Ding Ding Dog 在所有场景中看起来是同一个角色。

## 问题背景

项目使用 Wan 2.7 文生图模型逐场景独立生成图像。每次 API 调用是无状态的，模型不会自动记住之前生成的角色长什么样。如果不做特殊处理，同一角色在不同场景中可能出现：
- 颜色变化（毛色、衣服颜色不一致）
- 五官/比例变化（脸型、眼睛大小漂移）
- 配饰丢失（铃铛、眼镜、口袋等消失）
- 画风变化（不同场景艺术风格不统一）

## 三层保障机制

### 第一层：文本描述锚定

在每次图像生成的提示词中，嵌入完整的角色外观描述：

```python
CHARACTER_DESC = {
    "Ding Ding Dog": "A cute blue robotic puppy with big floppy dog ears, a short dog snout, round black nose, small wagging tail, stubby paws, and a golden bell on its red collar. Walks on two legs and has a magic pocket on its round belly. Friendly expression with tongue slightly out.",
    "Mia": "A cheerful girl with pigtails and round glasses.",
}
```

脚本生成阶段（GenerateScriptNode）强制要求 `image_prompt` 包含两个角色的描述：

```python
# 提示词规则
"For image_prompt: MUST start with '{IMAGE_STYLE}:' and include BOTH character descriptions 
 — both Mia and Ding Ding Dog should appear in the scene together"
```

图像生成阶段（GenerateImageNode）再次确保风格前缀：

```python
prompt = script["image_prompt"]
if not prompt.startswith(IMAGE_STYLE):
    prompt = f"{IMAGE_STYLE}: {prompt}"
```

全局风格常量统一画风：
```python
IMAGE_STYLE = "Japanese children anime cartoon style, clean line art, bright pastel colors, simple cute character design, wide 16:9 composition"
```

**作用**：文本层面锚定角色的关键视觉特征和整体画风，是一致性的基础层。

### 第二层：参考图像注入

每次图像生成请求都携带一张**角色设计参考图**（`assets/ref.png`），作为视觉基准：

```python
refs = [self._shared["ref_image"]]  # 始终包含角色参考图
result = generate_image(prompt, path, ref_image_paths=refs)
```

参考图通过 Data URI 编码后传入多模态 API：

```python
def image_to_data_uri(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"
```

API 调用时，参考图作为消息内容中的 image 部分传入：

```python
content = []
for ref_path in ref_image_paths:
    content.append({"image": image_to_data_uri(ref_path)})
content.append({"text": prompt})
```

同时在提示词中追加一致性指令：
```python
prompt += " IMPORTANT: Use the first reference image for character design consistency..."
```

**作用**：提供精确的视觉基准，模型直接参考图中的角色设计来生成新图像，比纯文本描述更可靠。

### 第三层：场景链式引用

在参考图之外，还将**上一张已生成的场景图**作为附加参考传入：

```python
refs = [self._shared["ref_image"]]
if self._shared["images"]:
    refs.append(self._shared["images"][-1])  # 链式引用上一张生成图
```

提示词中对应说明：
```python
"Use the second reference image (if present) for environment/color style continuity. 
 Keep characters identical across scenes. But change the camera ANGLE, character POSE, 
 and COMPOSITION — do NOT copy the same framing."
```

**作用**：
- 确保相邻场景的色彩、光照、环境风格连贯
- 角色外观从第一张开始"传递"，逐场景保持一致
- 同时明确要求改变构图、角度和姿势，避免画面重复

## 三层机制的协同

```
场景 1: [ref.png] → 图像 1
                        ↓
场景 2: [ref.png, 图像 1] → 图像 2
                              ↓
场景 3: [ref.png, 图像 2] → 图像 3
                                ↓
场景 4: [ref.png, 图像 3] → 图像 4
                                  ↓
                                ...
```

| 层级 | 机制 | 保障内容 | 可靠性 |
|------|------|---------|--------|
| 第一层 | 文本描述 | 角色特征 + 画风 | 基础（语言模糊性） |
| 第二层 | 参考图 | 精确角色设计 | 高（视觉直接参照） |
| 第三层 | 链式引用 | 场景间连贯性 | 高（时序一致性） |

三层叠加形成"文本锚定 + 视觉基准 + 时序传递"的完整一致性保障。

## 视觉多样性平衡

角色一致性不等于画面雷同。项目在提示词中刻意要求每个场景的视觉差异：

```
CRITICAL — EVERY SCENE MUST HAVE A DISTINCT VISUAL COMPOSITION:
- Different setting/location (bedroom, classroom, park, lab, kitchen, rooftop, etc.)
- Different camera angle (wide shot, close-up, over-the-shoulder, bird's-eye, low angle)
- Different character poses and actions (standing, sitting, pointing at board, holding gadget, jumping, etc.)
- Different props and visual aids relevant to the topic being discussed
```

动画提示词也强调动态性：
```python
"For animation_prompt: describe camera movement and character motion — make it dynamic."
```

**一致性 vs 多样性的平衡原则**：
- 角色外观（颜色、五官、服装、配饰）→ 必须一致
- 场景环境、镜头角度、角色姿势、道具 → 必须不同
- 整体画风（线条、色彩、比例）→ 统一风格

## 自定义角色参考

用户可以通过 `--ref-image` 参数替换默认参考图，使用自己的角色设计：

```bash
python main.py article.md --ref-image my_character.png
```

入口程序中的逻辑：
```python
ref_image = args.ref_image or os.path.join(os.path.dirname(__file__), "assets", "ref.png")
if not os.path.exists(ref_image):
    print(f"Reference image not found: {ref_image}")
    sys.exit(1)
```

要求参考图：
- 清晰展示角色正面/全身设计
- 简洁背景，避免干扰
- PNG 格式推荐
- 包含所有需要在视频中出现的角色

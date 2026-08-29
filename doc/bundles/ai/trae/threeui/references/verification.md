# P0 核验报告

> 核验日期：2026-08-28
> 核验方法：WebSearch 权威来源交叉验证
> 核验结果：**4✅ 3⚠️ 0❌**

## 核验结论总表

| 序号 | 声明项 | 结论 | 关键差异 |
|------|--------|------|----------|
| 1 | ThreeUI 项目存在性 | ✅ 通过 | Star 数已从 1000+ 涨至 4.1k |
| 2 | 164 个效果数据 | ✅ 通过 | README 逐字确认，141+23=164 |
| 3 | 10 个分类 | ⚠️ 部分通过 | 官网当前 9 个，"Sections"为空 |
| 4 | MCP 支持（含 4 工具） | ⚠️ 部分通过 | MCP Pro 确认，4 工具名未公开验证 |
| 5 | Meng To 身份 | ✅ 通过 | Design+Code 创始人，多源确认 |
| 6 | Canvas UI 参照 | ⚠️ 部分通过 | 项目存在性质吻合，作者为 DavidHDev |
| 7 | AI Coding 集成 | ✅ 通过 | 公告确认源码+Prompt 交 AI 修改 |

## 逐项详情

### 1. ThreeUI 项目存在性 ✅

- GitHub 仓库 https://github.com/MengTo/threeui 存在，MIT 许可证，基于 React + Three.js/WebGL
- 官网 https://threeui.com 可访问（/browse 和 /pricing 子路径确认）
- npm 包名 `@designcodeio/threeui`
- 博文发布时 Star 约 1000+，核验时已达约 4.1k（增长迅速，但博文数据在发布时准确）
- CLI：`npx @designcodeio/threeui-cli add <component>`

来源：GitHub README、threeui.com/browse、threeui.com/pricing、GitTimes 报道

### 2. 164 个效果数据 ✅

GitHub README "Included" 部分原文：

> - 50 Community parent components
> - 111 Community routes
> - 141 free variant records, plus 23 singleton components (164 browse results)

数学验证：141 + 23 = 164，数据完全吻合。无差异。

来源：https://github.com/MengTo/threeui/blob/main/README.md

### 3. 10 个分类 ⚠️

博文列出 10 个分类，官网 threeui.com/browse 当前导航显示 9 个：

1. Landing Pages ✅
2. Hero ✅
3. Three.js ✅
4. Backgrounds ✅
5. Buttons ✅
6. Text Animation ✅
7. UI Elements ✅
8. CSS ✅
9. Motion Design ✅

"Sections"分类访问 https://threeui.com/sections 返回 "No components match this category."。可能原因：计划中未上线、已移除或合并。官网显示总计 "Search 373 components"（含 Pro）。

**勘误处理**：在 concepts/01-component-catalog.md 中以 ⚠️ 标注此差异，F-041 记录。

### 4. MCP 支持 ⚠️

- **MCP 作为 Pro 功能已确认**：定价页 https://threeui.com/pricing 明确列出 "Pro MCP access to components, prompts, and source"
- Meng To 公告确认 "Pro comes with 50+ extra components, MCP, and skills"
- **4 个具体工具名称无法从公开来源独立验证**：多次精确搜索 search_catalog/get_catalog_item/get_item_source/get_item_prompt 均未返回 ThreeUI 相关结果。这些工具名可能仅在 Pro 认证后的 MCP 配置文档中披露
- 工具命名逻辑合理：定价页提到 "components, prompts, and source" 三类资源，与 4 个工具的功能划分大致对应

**勘误处理**：在 concepts/02-ai-coding-mcp.md 中以 ⚠️ 标注，F-042 记录。

### 5. Meng To 身份 ✅

- Dive.club 播客访谈："Meng To, Founder of Design+Code"
- DesignCode 官方课程页："Meng To is the author of Design+Code"
- Pragma Conference 演讲者页："Company: Design+Code"
- dev.to 文章："Meng To, the designer behind Design+Code"

无差异。Meng To 确认为 Design+Code 创始人，自学成才，20 余年经验，著书 35,000 读者。

### 6. Canvas UI 参照 ⚠️

- Canvas UI 项目确实存在：https://github.com/DavidHDev/canvas-ui ，官网 https://canvasui.dev/
- 核心理念吻合："Your DOM becomes a WebGL texture, shaders distort, dissolve, and refract your real page in real time, while everything stays fully interactive."
- 技术核心为实验性 html-in-canvas API，支持 React/Vue/Svelte/vanilla TS
- **差异说明**：Canvas UI 由 DavidHDev（react-bits 维护者）创建，并非 Meng To 项目。但博文仅作为行业参照提及（"一个叫 Canvas UI 的项目"），未误归属为 Meng To 作品
- 发布时间 2026-07-23，比 ThreeUI（~2026-08-22）早约一个月，博文用"前段时间"描述合理
- 发布时 24 组件，核验时 33 个

**勘误处理**：F-043 补充 Canvas UI 作者和技术细节，博文本身无误归属。

### 7. AI Coding 集成 ✅

- Meng To 公告原文："Copy the prompt or source, give it to your agent, then change the theme, lighting, motion or layout"
- 微博转载确认："附带 Prompt 或源码，组件自带配套 Skills"
- MengTo/Skills 生态文档证实 skills 文件夹可放入 Claude Code、Cursor、Codex、OpenCode、Kiro 等 agent
- 官网有 "Brand Orbs" 组件以 Claude Code/OpenAI/Codex/Cursor/Gemini 等品牌命名

博文虽未逐一列出三个品牌名，但工作流和生态兼容性已确认。

## 权威来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| ThreeUI GitHub | https://github.com/MengTo/threeui | 项目数据、README |
| ThreeUI 官网 | https://threeui.com/browse | 分类导航 |
| ThreeUI 定价 | https://threeui.com/pricing | MCP Pro 确认 |
| Meng To 公告 | https://blog.eond.com/community/492930 | AI Coding 工作流 |
| Dive.club 播客 | https://www.dive.club/deep-dives/meng-to | Meng To 身份 |
| Canvas UI GitHub | https://github.com/DavidHDev/canvas-ui | 参照项目核验 |
| Canvas UI 官网 | https://canvasui.dev/ | 参照项目核验 |
| CSSScript | https://www.cssscript.com/canvas-ui/ | Canvas UI 报道 |
| GitTimes | https://gittimes.com/editions/2026-08-22/ | ThreeUI 发布报道 |
| dev.to | https://dev.to/creeta/mengtoskills-... | Skills 生态分析 |

## 核验结论

博文整体事实准确性较高。7 项核验中 4 项完全通过，3 项部分通过但无完全失实项。部分通过项均为可解释的差异：

1. **分类数差异**：可能因官网在博文发布后调整分类，或 Sections 为计划中分类
2. **MCP 工具名**：Pro 功能文档非公开，博文可能来自测试资格或提前披露
3. **Canvas UI 补充**：博文未误归属，仅补充作者信息

9 条作者观点（📝）为合理的趋势判断和评价，未发现将观点包装为事实的情况。

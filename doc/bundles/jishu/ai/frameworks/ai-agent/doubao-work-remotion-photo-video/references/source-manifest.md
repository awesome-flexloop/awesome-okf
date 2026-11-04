---
type: Reference
title: 来源登记与采集边界
status: flagged
stale_after: 2026-12-04
generated: { by: "process:seven-concepts", at: "2026-11-04T10:31:25+08:00" }
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg
  - id: skills
    resource: https://www.remotion.dev/docs/ai/skills
---

# 来源登记与采集边界

## 主来源身份

| 字段 | 记录 |
| --- | --- |
| source_id | article |
| 标题 | 豆包工作+剪辑Skills！人人都是视频大师！ |
| 公众号 | 前端之神 |
| 作者 | 林三心不学挖掘机 |
| 页面日期 | 2026-10-30 08:35；页面未显示时区 |
| 归属信号 | 公众号名、作者、原创标识及广东地域标识 |
| 原始入口 | `https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg?from=industrynews&color_scheme=light#rd` |
| 规范 URL | `https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg` |
| 采集日期 | 2026-11-04 |
| 访问方式 | 浏览器只读访问，正文可匿名读取，无登录墙或验证码 |
| 信源距离 | 作者一手体验叙述，含推荐与福利推广；未取得赞助关系证据，不能视为官方产品契约 |
| 公开性 | Public；查询参数是来源与显示设置，非访问口令 |
| status | collected-partial：正文已读，部分图片和视频未核验 |

## 官方来源

以下资料支持 Remotion 通用能力，不证明豆包客户端与其集成已被本会话复现。所有访问日期为 2026-11-04。

| source_id | 来源 | 已取得内容 | 状态及定位 |
| --- | --- | --- | --- |
| skills | [Agent Skills](https://www.remotion.dev/docs/ai/skills) | 安装入口、技能职责和目录 | collected；Available skills；页面更新 2026-11-01 |
| coding | [Coding Agents](https://www.remotion.dev/docs/ai/coding-agents) | Node.js、编码 Agent、新项目与预览流程 | collected；Prerequisites/创建项目流程；页面更新 2026-11-01 |
| still | [静帧 CLI](https://www.remotion.dev/docs/cli/still) | still 命令、frame、props | collected；命令首段、`--frame`、`--props` |
| render | [渲染 CLI](https://www.remotion.dev/docs/cli/render) | render 命令、宽高、帧率及帧数 | collected；命令首段、`--width`/`--height`/`--fps`/`--duration` |
| license | [许可入口](https://www.remotion.dev/license) | 返回仓库 LICENSE.md 的免费资格和限制 | collected；Free License/Company License |
| company-license | [公司许可页](https://www.remotion.pro/license) | 免费资格、Creators/Automators 许可区分 | collected；Free License/License for Creators/Automators |
| doubao | [豆包下载页](https://www.doubao.com/download/desktop) | 官方搜索结果摘要提及新用户 30 天体验 | snippet-only；直接抓取仅得标题，未读完整规则 |

## 未采集项与停止条件

| 项目 | 可见证据 | 未取得内容 | 影响与允许的下一步 |
| --- | --- | --- | --- |
| 配图 | 共 12 张；第 1 张安装输入已读，替代文字均为“图片” | 第 2–12 张未可靠读取 | 不推测完整视频/补音乐提示词；下次正常浏览或用户提供截图再补 |
| 视频 | 首尾各一个 `00:30` 视频，作者称同一成片 | 未播放、未核对画质、声音与时长元数据 | 不标成片实测；取得可播放公开资源后再查 |
| 客户端与项目 | 正文说明本地执行 | 客户端版本、依赖锁、项目文件、原始照片 | 不提供“完全复现原作”保证 |
| 福利规则 | 作者叙述及官方搜索摘要 | 领取条件、签到额度、失效条件 | 不代领、不作永久免费承诺 |

配图采集连续出现浏览器超时，已停止重复请求；没有绕过访问控制。正文只保存原创摘要、必要短引文与定位，不镜像全文或原始 HTML。未取得的事实保持 `unverified`，检索无结果不能证明某能力不存在。

到 `stale_after` 前重新核对官方技能目录、许可与豆包入口；若配图和复现证据仍不可得，保留 flagged。事实与判断分界见[事实登记](article-source.md)和[核验台账](verification.md)。

## 后续复核约定

由下一次承接本包更新的维护者负责复核，期限为 2026-12-04 之前；本次没有安排自动任务，也没有指派具体人员。没有维护者接手时，不视为复核已安排或已完成。

| 对象 | 对应来源与事实 | 需记录的结果 |
| --- | --- | --- |
| 技能与项目流程 | skills、coding；F-023–F-027/F-036 | 观察日期、官方更新时间、技能集合及适用版本 |
| 静帧与渲染参数 | still、render；F-028–F-032 | 参数支持版本、Windows props 建议及变动范围 |
| 许可及福利 | license、company-license、doubao；F-022/F-033–F-035 | 条款版本、主体用途边界、完整规则是否取得 |
| 原作复现缺口 | article；F-010/F-011/F-017–F-020 | 是否取得对应历史时点的截图、项目或媒体证据 |

结果写入核验台账与日志，保留必要短摘录或官方修订标识。到期未完成时，本包按 `stale_after` 视为过期，不能仅顺延日期；旧 CLI 和权益信息须先复核再使用。历史观察只由对应历史时点的补证或勘误修订，当前产品更新另记新时点，不覆盖旧观察。

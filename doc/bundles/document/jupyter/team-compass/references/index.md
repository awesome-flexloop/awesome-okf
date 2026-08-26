# team-compass 信源索引

本目录登记 jupyter-server/team-compass 仓库中所有核心原始文档的路径和内容摘要，供概念文档通过 `sources` 字段引用。

| 信源文件 | 对应原始文档 | 内容 |
|---------|------------|------|
| [readme-source.md](readme-source.md) | README.md | 周会信息（时间/Zoom/HackMD）、扩展贡献指南 |
| [team-source.md](team-source.md) | docs/team.md, docs/team/contributors-jupyter-server.yaml | 成员列表、活跃/不活跃分类、SSC代表机制、YAML数据结构、当前成员名单 |
| [becoming-member-source.md](becoming-member-source.md) | docs/team/becoming-member.md | 新成员5步提名流程、活跃/不活跃状态定义、半年维护机制 |
| [decision-making-source.md](decision-making-source.md) | docs/team/decision-making.md | 共识优先投票兜底机制、团队规模无上限原则、Jupyter治理衔接 |
| [member-guide-source.md](member-guide-source.md) | docs/team/member-guide.md | 团队资源、沟通渠道策略、5项成员职责、PR合并5原则 |
| [conf-py-source.md](conf-py-source.md) | docs/conf.py, readthedocs.yml, docs/requirements.txt, .pre-commit-config.yaml | Sphinx配置、MyST Markdown支持、sphinx-book-theme、RTD构建配置 |
| [gen-contributors-source.md](gen-contributors-source.md) | docs/scripts/gen_contributors.py, docs/_static/custom.css | YAML→HTML贡献者表格自动生成脚本逻辑、CSS样式定义 |

```{toctree}
:hidden:
:maxdepth: 7

becoming-member-source
conf-py-source
decision-making-source
gen-contributors-source
member-guide-source
readme-source
team-source
```

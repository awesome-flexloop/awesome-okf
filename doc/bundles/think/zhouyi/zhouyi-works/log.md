# 更新日志

## 2026-08-31

- **创建**：初始化 zhouyi-works bundle，聚焦《周易》经传的权威原文与三线解读
- **结构**：concepts/（5 概念）、text/（经文全本 2 篇 + 十翼选读 3 篇 + 出土异文 1 篇）、examples/（2 精读）、commentaries/（4 解读）、references/（3 信源）
- **方法论文档**：facts.md（零推测事实）、insights.md（四元组洞察）、patterns.md（可复用模式）、usage.md（阅读指南）
- **信源策略**：经文以阮刻《十三经注疏·周易正义》为底本，ctext.org 与维基文库双源逐字核对；出土文献（马王堆帛书/上博楚简/阜阳汉简/王家台秦简《归藏》）存佚分层著录，释文溯源正式整理本；注本三线并收
- **方法论**：seven-concepts 场景4（知识沉淀），链路 R→I→E→V→C；经独立审查后原子提交
- **补记**：提交前门控（check-toctrees）发现 text/jing-shang.md、text/jing-xia.md、insights.md、patterns.md、usage.md 五件尚未生成；本次提交先移除其 toctree 占位并在正文标注"待补"，后续增量补齐。另：examples/qian-kun-jingdu.md 坤卦节、examples/key-gua-jingdu.md 复卦节亦待补全

---
type: Reference
title: 电子文本信源
description: 《黄帝内经》权威电子文本网站分级登记，含 URL、底本说明与弃用信源警告
tags: [reference, 黄帝内经, 电子文本, ctext, 古诗文网, 维基文库, 信源分级]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:00:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: ctext
    title: ctext.org 中国哲学书电子化计划
  - id: gushiwen
    title: 古诗文网 gushiwen.cn
---

# 电子文本信源

> 本 bundle 八篇精读原文全部逐字转录自下列一级电子信源，并标注底本。引用任何《内经》文字前，先在此确认信源级别。

## 一、一级信源（底本明确，可逐字引用）

| 信源 | URL | 底本与特点 |
|------|-----|-----------|
| ctext.org 中国哲学书电子化计划 | https://ctext.org/huangdi-neijing | 《素问》底本为《四部丛刊初编》景印《重广补注黄帝内经素问》，《灵枢》底本为《四部丛刊初编》景印《黄帝素问灵枢经》，繁体；附《太素》《注证发微》《素问集注》等平行注本对照 |
| ctext 单篇中文页规律 | `https://ctext.org/huangdi-neijing/<拼音slug>/zh` | 如上古天真论 `/shang-gu-tian-zhen-lun/zh`、生气通天论 `/sheng-qi-tong-tian-lun/zh`、九针十二原 `/jiu-zhen-shi-er-yuan/zh` |

## 二、二级信源（简体通行本，用于对读与白话环境）

| 信源 | URL 示例 | 说明 |
|------|----------|------|
| 古诗文网 | https://m.gushiwen.cn/guwen/bookv_4e24073702b0.aspx （至真要大论） | 简体原文+注释+译文；各篇 bookv id 不同，经站内检索"素问+篇名"可达；文字与梅花本系统偶有出入，引用时与 ctext 对读 |
| huangdineijing.org | https://huangdineijing.org/docs/su_wen/cang-qi-fa-shi-lun/ （藏气法时论） | 简体全文站，按篇组织 |
| cloudtcm.com | https://cloudtcm.com/shu/t1/757/239 （《素问悬解》卷十二） | 黄元御《素问悬解》全文，经注并列，保留清人注本异文（如"热因寒用，寒因热用"） |
| itcmc.org.cn | https://www.itcmc.org.cn/app/zygj/427/129.htm （《类经》论治类） | 张介宾《类经》全文，含王冰注与张氏注 |

## 三、三级信源（教学材料，用于理解而非引用）

| 信源 | 说明 |
|------|------|
| 王洪图内经讲课 PDF（zhongyijinnang.com 存档） | 教材讲义，病机十九条、治法群分段讲解，适合入门理解 |
| qihuang.vip《灵素节注类编》引文页 | 病机十九条转录（繁体），与 ctext 系统一致 |
| 丁香园 dxy.cn 病机十九条注释帖 | 医界讨论，含高世栻心/火改读说 |
| 北京中医药大学官网（bucm.edu.cn） | 翟双庆《研究内经三方法》，注本数量等学术事实 |
| 光明网文摘报 2019-11-30 | 《黄帝内经的神奇流传历程》，版本史通俗考证 |

## 四、弃用信源（明确警告）

| 信源 | 状态 |
|------|------|
| www.zysj.com.cn（中医世家旧域名） | **已被 SEO 垃圾内容占用**（2026-08 实测返回与中医典籍无关的垃圾页），禁止作为《内经》信源引用 |
| 各类"经典语录""人生智慧"聚合站 | 仅摘句、无篇名无版本，错字率高，禁止用于原文核对 |

## 五、抓取注意事项

- ctext.org 对自动抓取有频率限制：连续抓取约 6 个页面后返回"Access to ctext.org is unavailable from your current location……嚴禁使用自動下載軟体"提示页；遇此需冷却后重试，或改用二、三级信源交叉核对
- 维基文库（zh.wikisource.org）亦收《黄帝内经》，本次调研期间访问不稳定，未作为逐字引用源
- 凡简体网页文字与 ctext 繁体底本不一致处，以繁体底本为准，异文双录并注（见 facts.md F-111 等）
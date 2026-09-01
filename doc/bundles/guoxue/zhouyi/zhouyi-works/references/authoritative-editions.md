---
type: Reference
title: 权威底本与电子双源
description: 《周易》今本系统的权威纸质底本（阮刻十三经注疏、武英殿本、北大整理本）与双源电子文本（ctext.org、维基文库）登记
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T20:46:00+08:00" }
status: stable
stale_after: 2027-08-31
---

# 权威底本与电子双源

本 bundle 经文（六十四卦卦爻辞）与传文（《系辞》《说卦》《序卦》《杂卦》及乾坤《彖》《象》《文言》）的文字基准为传世今本系统，即以 [^ruan-ke-shisanjing] 阮元校刻《十三经注疏》本《周易正义》为底本，并以两个独立电子文本逐字核对。

## 一、纸质底本（今本系统）

| 信源 ID | 书目 | 说明 | resource |
|---------|------|------|----------|
| `ruan-ke-shisanjing` | （魏）王弼、（晋）韩康伯注，（唐）孔颖达等疏《周易正义》，载（清）阮元主持校刻《十三经注疏》 | 清代以后最通行的经疏合刊本；经文、王韩注、孔疏俱全。阮刻以元刻明修本（正德本）等为底本校勘，附《经典释文·周易音义》与阮元《十三经注疏校勘记》 | 中华书局1980年影印嘉庆江西南昌府学本（上下册）；北京大学出版社2000年简体横排点校本 |
| `wuying-dian` | 《武英殿十三经注疏》本《周易正义》 | 清乾隆武英殿刻本，ctext.org 电子文本标注的底本 | ctext 电子图书馆影印：https://ctext.org/library.pl?if=gb&res=77712 |
| `beida-zhengli` | 李学勤主编《周易正义》（《十三经注疏》整理本） | 现代标点整理本，以阮刻本为工作本，对经文、注、疏施加现代标点并出校 | 北京大学出版社，1999年 |
| `siku-zhouyi` | （宋）朱熹《周易本义》等，文渊阁《四库全书》本 | 宋以后通行的经传合编/分列系统参校 | ctext 电子图书馆影印：https://ctext.org/library.pl?if=gb&res=765 |

## 二、电子双源（逐字核对用）

| 信源 ID | 资源 | 底本声明 | 覆盖范围 | resource |
|---------|------|----------|----------|----------|
| `ctext-zhouyi` | 中国哲学书电子化计划（Chinese Text Project）《周易》 | 电子底本为《武英殿十三经注疏》本《周易正义》，并列阮刻《十三经注疏》本、《四部丛刊初编》本等影印 | 易经六十四卦（逐卦分页）、《彖传》《象传》《系辞》上下、《文言》《说卦》《序卦》《杂卦》 | https://ctext.org/book-of-changes/zh ；英文译本为理雅各（James Legge）1882/1899《Sacred Books of the East》 vol.16 |
| `wikisource-zhouyi` | 维基文库（Wikisource）《周易》 | 以传世《十三经注疏》系统经文为底，按卦、按传分页 | 六十四卦经文（逐卦分页，含《彖》《大象》《小象》《文言》对照栏）与《系辞上》《系辞下》《说卦》《序卦》《杂卦》《文言》专页 | https://zh.wikisource.org/wiki/周易 |

## 三、核对方法与一致性说明

- **文字基准**：经文、传文以 `ruan-ke-shisanjing`（阮刻本）为准；两个电子源同源于传世注疏系统，正文与阮刻高度一致。
- **核对方式**：本 bundle [text/](../text/index.md) 经文转录后，对《乾》《坤》《屯》《泰》《谦》《咸》《既济》《未济》等分层抽样卦及《系辞》上下、《说卦》《序卦》《杂卦》全篇，逐字比对 `ctext-zhouyi` 与 `wikisource-zhouyi`；比对记录见 [log.md](../log.md)。
- **异体字处理**：经文用传世规范字形（如"无妄"不作"旡妄"、"坤"不作"川"）；出土通假字（如帛书"键/川"）归入 [text/unearthed-variants.md](../text/unearthed-variants.md)，不窜入今本经文。
- **传文界线**：[text/jing-shang.md](../text/jing-shang.md)、[text/jing-xia.md](../text/jing-xia.md) 只录卦辞爻辞（经），不录《彖》《象》《文言》；《彖》《象》《文言》乾坤部分随 [examples/qian-kun-jingdu.md](../examples/qian-kun-jingdu.md) 完整呈现，其余各卦传文给出 `ctext-zhouyi`/`wikisource-zhouyi` 分页指引。

[^ruan-ke-shisanjing]: 阮元校刻《十三经注疏》本《周易正义》，清代以后通行底本，见 references/sources-cross-ref.md 的 `ruan-ke-shisanjing`（A 级）。

# Post-AME2020 Holdout Checksums

Generated for TASK-0196 on 2026-05-12. These checksums pin the source artifact used for row extraction and the committed dataset. Tests must not live-fetch these sources.

| Artifact | Scope | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| nst_publisher_html_2026_05_12 | Publisher HTML downloaded from http://www.nst.sinap.ac.cn/article/doi/10.1007/s41365-025-01821-1 | 260783274c0426f19799b52b24608fb38837ec63488462e28d33a4c5ce45af64 | 964379 |
| nst_embedded_jats_xml_2026_05_12 | `pageProps.xmlData` extracted from the NST publisher HTML and used for Table 2/Table 3 row extraction | 95fb495f0b05058552855ce31ec7bf0f0b17ad5f878f28010e4872402281eca0 | 345069 |
| post_ame2020_holdout_yaml | Committed dataset at `data/nuclear_masses/post_ame2020_holdout.yaml` | 47bfe520df8ca4a95c1614192c5da165782b2308ba58110e6832afb1b8151e49 | 252822 |
| chinaxiv_machine_translation_pdf_crosscheck | ChinaXiv English machine-translation PDF, downloaded for audit only; not used for row extraction because Table A1 superscripts disagree with NST JATS XML | 51ac0c15896a84a8f3c051097b324eec7c1d323bab0e8c4dc4da12dbf31a37fc | 180071 |

The canonical row source is the NST publisher JATS XML embedded in the publisher HTML. The ChinaXiv machine-translation PDF is retained only as a recorded audit attempt.

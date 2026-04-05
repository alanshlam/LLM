========================================================================================
 VIRUSTOTAL REPORT COMPARISON
 Hash: b12ba38dd1de68e22e910873be32aa13661f43fcc4ba3b1521695c107edd201e
 Date: 2026-04-01
========================================================================================

COMPARISON BETWEEN LOCAL REPORT AND VIRUSTOTAL API

--- Field Comparison ---
| Field              | Local Report                           | API Response                          | Status |
|--------------------|----------------------------------------|---------------------------------------|--------|
| SHA-256            | b12ba38dd1de68e22e910873be32aa13661f43fcc4ba3b1521695c107edd201e | Same | Match |
| File Name          | 20231211-081523_sftp__root__2037439001696860133_sshd | Same | Match |
| File Type          | ELF                                    | ELF                                   | Match |
| First Submitted    | 2023-09-19 21:53:27 UTC                | 2023-09-19 13:53:27 UTC               | 8h offset |
| Last Analyzed      | 2026-03-24 13:18:15 UTC                | 2026-03-24 05:18:15 UTC               | 8h offset |

--- Detection Summary Comparison ---
| Metric     | Local Report | API Response | Status |
|------------|--------------|--------------|--------|
| Malicious  | 35           | 35           | No change |
| Suspicious | 0            | 0            | No change |
| Undetected | 30           | 30           | No change |

--- Malicious Detections (35 vendors) ---  
[*] Lionic               : Trojan.Linux.Miner.4!c  
[*] Elastic              : Linux.Generic.Threat  
[*] MicroWorld-eScan     : Application.Generic.4495641  
[*] ClamAV               : Unix.Trojan.Miner-9993889-0  
[*] CTX                  : elf.trojan.generic  
[*] ALYac                : Application.Generic.4495641  
[*] Zillya               : Trojan.252279.Linux.1  
[*] huorong              : Trojan/Linux.Agent.ca  
[*] Symantec             : Trojan.Gen.NPE  
[*] ESET-NOD32           : Linux/CoinMiner.ABF trojan  
[*] Avast                : ELF:Agent-CXA [Trj]  
[*] Cynet                : Malicious (score: 99)  
[*] Kaspersky            : HEUR:Trojan.Linux.Miner.gen  
[*] BitDefender          : Application.Generic.4495641  
[*] Tencent              : Risktool.Linux.Miner.ck  
[*] Sophos               : Mal/Generic-S   
[*] F-Secure             : Exploit.EXP/ELF.Coinminer.A  
[*] DrWeb                : Linux.Siggen.8622  
[*] VIPRE                : Application.Generic.4495641  
[*] Emsisoft             : Application.Generic.4495641 (B)  
[*] Ikarus               : Trojan.Linux.Generic  
[*] GData                : Application.Generic.4495641  
[*] Jiangmin             : Trojan.Linux.dsm  
[*] Avira                : EXP/ELF.Coinminer.A   
[*] Antiy-AVL            : Trojan/Linux.Multiverze  
[*] Microsoft            : Trojan:Linux/Multiverze!rfn  
[*] Arcabit              : Application.Generic.D449919  
[*] Google               : Detected  
[*] AhnLab-V3            : CoinMiner/Linux.Agent.30304472  
[*] VBA32                : Trojan.Linux.Agent  
[*] Rising               : HackTool.NBMiner/Linux!1.E357 (CLASSIC)  
[*] SentinelOne          : Static AI - Malicious ELF  
[*] Fortinet             : Adware/Miner  
[*] AVG                  : ELF:Agent-CXA [Trj]  
[*] alibabacloud         : Miner:Linux/CoinMiner.JUO  

========================================================================================
 SUMMARY
========================================================================================

- All 35 malicious vendors match between local report and API
- No vendor detection changes
- No vendor additions or removals
- Local report timestamps are 8 hours ahead (timezone offset)
- Report is up-to-date as of 2026-03-24 05:18:15 UTC

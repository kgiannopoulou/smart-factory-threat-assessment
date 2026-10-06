# Smart Factory STRIDE Threat & Risk Assessment

A consulting-style cybersecurity assessment of a **fictional smart manufacturing plant**. I modelled the plant's IT, OT, IIoT and vendor connectivity, identified threats with **STRIDE**, scored them on a documented **5x5 risk model**, chained them into **attack scenarios**, mapped controls to **IEC 62443, NIST SP 800-82r3 and NIST CSF 2.0**, and produced a **prioritised 30/90/365-day remediation roadmap**.

> **The final deliverable:** [`report/smart-factory-security-assessment.pdf`](report/smart-factory-security-assessment.pdf) (26 pages including appendices)

![Factory architecture](diagrams/factory-architecture.png)

## Highlights

- **30 threats** across all six STRIDE categories, each tied to an asset, a numbered data flow (DF-01 to DF-20), a threat actor and an attack path
- **5 attack scenarios** mapped step-by-step to **MITRE ATT&CK for ICS**, with a detection opportunity and a chain-breaking control at each step
- **Risk profile:** 5 Critical / 18 High / 6 Medium / 1 Low before treatment, and **0 Critical / 3 High / 18 Medium / 9 Low** after the roadmap
- **17 controls** traced to the threats they mitigate and mapped to IEC 62443-3-3 SRs, SP 800-53 (800-82r3 OT overlay) and CSF 2.0
- **22 roadmap actions** with owner and effort. All eight 0-30 day actions are low-effort configuration changes that directly treat Critical risks
- Everything is generated from a **single source of truth** ([`tools/data.py`](tools/data.py)) with referential-integrity checks, so IDs and scores stay consistent across the PDF, Excel and Markdown

## The scenario

**Apex Manufacturing Ltd.** (fictional) makes robot-welded brake caliper brackets for two automotive OEMs. The plant runs 3 shifts and ships ~£180k of product per day. IATF 16949 traceability requirements make **quality escapes** as serious a concern as downtime.

| Zone | Purdue | Contents |
|---|---|---|
| Enterprise | L4-L5 | Workstations, Active Directory, ERP, email |
| Industrial DMZ | L3.5 | Historian replica, jump server, SSL VPN |
| OT Site Operations | L2-L3 | SCADA/HMI, engineering workstation, historian, OPC UA |
| Control | L1 | PLC-01 conveyor, PLC-02 robotic welding, PLC-03 packaging |
| Process & Safety | L0 | Sensors, actuators, hardwired safety |
| IIoT / Cloud | - | Vibration sensors, IIoT gateway with LTE uplink, SaaS analytics |
| Vendor | external | RoboServ Automation GmbH (remote PLC maintenance) |

Main findings, all architectural:

1. OT hosts are **joined to the corporate AD domain**, so domain compromise means OT compromise
2. The IT/OT firewall has a **leftover any-any rule** and direct RDP/SMB from IT
3. **Vendor VPN** uses one shared, password-only, always-on account. **Unapproved TeamViewer** found on the engineering workstation
4. The **IIoT gateway has its own LTE uplink**, which bypasses the IDMZ entirely
5. **No enforcement between L2-L3 and the PLCs**. Key switches are left in REMOTE and the only PLC program copies are on the EWS

## Top 5 risks

| # | ID | Risk | Score | After treatment |
|---|---|---|---|---|
| 1 | T-08 | Corporate AD compromise grants OT access | 20 🔴 Critical | 5 🟡 Medium |
| 2 | T-10 | Permissive IT/OT firewall rules bypass IDMZ | 20 🔴 Critical | 5 🟡 Medium |
| 3 | T-01 | Stolen vendor credentials used on VPN | 20 🔴 Critical | 10 🟠 High |
| 4 | T-17 | Ransomware encrypts SCADA/HMI | 20 🔴 Critical | 8 🟡 Medium |
| 5 | T-24 | Unapproved TeamViewer on engineering workstation | 20 🔴 Critical | 5 🟡 Medium |

Full list: [Top 10](risk-assessment/top-risks.md) · [risk matrix](risk-assessment/risk-matrix.png)

![Risk matrix](risk-assessment/risk-matrix.png)

## Repository structure

```
smart-factory-threat-assessment/
├── README.md
├── architecture/
│   ├── factory-architecture.md      company profile, process, architecture, key observations
│   ├── asset-inventory.md           23 assets, zones, indicative SL-T / SL-A
│   └── data-flows.md                DF-01..DF-20 and trust boundaries TB-1..TB-7
├── diagrams/
│   ├── factory-architecture.png
│   ├── network-zones.png            zones, conduits, enforcement state, bypass paths
│   ├── data-flow-diagram.png        Level-1 DFD
│   └── src/*.mmd                    Mermaid sources
├── threat-model/
│   ├── methodology.md               STRIDE-per-element, threat actors, limitations
│   ├── stride-analysis.xlsx         system model + full threat register (live formulas)
│   ├── stride-threat-register.md    the same register, readable on GitHub
│   └── attack-scenarios.md          AS-01..AS-05 with ATT&CK for ICS mapping
├── risk-assessment/
│   ├── risk-methodology.md          5x5 scales, thresholds, worked examples
│   ├── risk-register.xlsx           register, heat maps (COUNTIFS), top 10, mapping, roadmap
│   ├── top-risks.md
│   ├── risk-matrix.png
│   └── stride-distribution.png
├── controls/
│   ├── security-recommendations.md  control catalogue, focused mapping, residual risk
│   ├── framework-mapping.md         IEC 62443 / NIST SP 800-53 / CSF 2.0
│   └── remediation-roadmap.md       0-30 days / 30-90 days / 3-12 months
├── report/
│   └── smart-factory-security-assessment.pdf
└── tools/                           Python generators (single source of truth: data.py)
```

## Methodology in brief

1. **Model**: company, assets, zones and conduits (IEC 62443-3-2 style), DFD with numbered flows
2. **Identify**: STRIDE per element, focused on trust-boundary crossings
3. **Chain**: five attack scenarios mapped to MITRE ATT&CK for ICS
4. **Score**: Likelihood x Impact, documented thresholds (1-4 Low, 5-9 Medium, 10-16 High, 17-25 Critical). The impact scale covers production, financial, safety/quality and data
5. **Treat**: controls mapped to frameworks, sequenced by risk reduction per unit of effort, with residual risk documented and High residuals proposed for formal acceptance

The scales are this assessment's documented methodology, not a universal standard.

## Rebuilding

```bash
pip install -r requirements.txt
python tools/build_all.py        # Excel, Markdown tables, charts, PDF
# diagrams (Node.js):
npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/src/data-flow-diagram.mmd -o diagrams/data-flow-diagram.png -b white -s 2
```

## Related project

**[OT/ICS Cybersecurity Lab](https://github.com/kgiannopoulou/ot-ics-cybersecurity-lab)**. That project builds, attacks, monitors and defends an industrial environment hands-on. This one shows the assessment side: understanding business and operational risk, threat-modelling an architecture, and recommending prioritised security improvements.

## Disclaimer

Apex Manufacturing Ltd., RoboServ Automation GmbH and every system described here are **fictional**. No real organisation was assessed. Framework references are to IEC 62443, NIST SP 800-82 Rev. 3, NIST SP 800-53 Rev. 5, NIST CSF 2.0 and MITRE ATT&CK for ICS. They are used as mapping targets, not as claims of certification or compliance.

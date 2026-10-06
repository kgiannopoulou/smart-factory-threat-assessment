# Risk methodology

> These scales and thresholds are the **documented methodology for this assessment**. They follow common 5x5 practice but are not a universal standard. Financial bands are calibrated to Apex's ~£180k/day production value.

## Formula

```
Risk score = Likelihood (1-5) x Impact (1-5)        range 1-25
```

* **Current risk** is scored with the controls that exist today.
* **Residual risk** is scored assuming the recommended controls are implemented as described.
* Impact is rated on the **highest applicable dimension** (safety, production, financial, quality, data).

## Likelihood

| Score | Level | Criteria |
|---|---|---|
| 1 | Rare | Requires nation-state capability and insider access; no known precedent in the sector |
| 2 | Unlikely | Requires significant skill plus an existing foothold; strong compensating controls |
| 3 | Possible | Feasible for a motivated attacker with OT knowledge once inside; controls are partial |
| 4 | Likely | Technique is used routinely against similar manufacturers; weak controls; low skill |
| 5 | Almost certain | Trivial, directly exposed, or already observed at Apex |

Factors considered: exposure (Internet-facing vs. internal), attacker skill required, whether a prior foothold is needed, existing controls, and public reporting of the technique against manufacturing.

## Impact

| Score | Level | Production | Financial | Safety / quality | Data |
|---|---|---|---|---|---|
| 1 | Insignificant | None | < £10k | None | Internal only |
| 2 | Minor | < 4 h on one line | £10k-£50k | Quality issue caught internally | - |
| 3 | Moderate | 4-24 h on one line, or < 8 h plant-wide | £50k-£250k | - | Limited disclosure of sensitive data |
| 4 | Major | 1-3 days plant outage | £250k-£1M | Defective parts reach customer; equipment damage | Loss of traceability records |
| 5 | Severe | > 3 days outage | > £1M | Potential injury, product recall, loss of OEM contract | - |

## Thresholds

| Score | Rating | Expected response |
|---|---|---|
| 17-25 | 🔴 **Critical** | Senior-management attention; mitigate within 30 days |
| 10-16 | 🟠 **High** | Mitigation plan within 90 days |
| 5-9 | 🟡 **Medium** | Mitigate within 12 months or formally accept |
| 1-4 | 🟢 **Low** | Accept and monitor |

## Worked examples

| Threat | L | I | Score | Reasoning |
|---|---|---|---|---|
| T-01 Stolen vendor credentials on VPN | 4 | 5 | **20 Critical** | Password-only, shared, always-on, Internet-exposed (L4). Leads to PLC access, so a multi-day outage is plausible (I5) |
| T-05 Network flooding of PLCs | 3 | 4 | **12 High** | Flat network with no storm control (L3). Line stops for hours to a day (I4) |
| T-04 Historian replica data disclosure | 3 | 3 | **9 Medium** | All domain users can read it (L3). Commercially sensitive but not operational (I3) |
| T-14 Spoofed vibration sensors | 2 | 2 | **4 Low** | Needs physical proximity (L2). Analytics are advisory only (I2) |

## Ranking

Top-10 order: **score desc -> impact desc -> number of attack scenarios the threat participates in desc -> ID**. The scenario-count tie-breaker favours chokepoint threats whose mitigation breaks several attack paths.

## Residual risk

Most controls reduce **likelihood**. Some also reduce **impact**:

* **SC-08 backups** cut recovery time (T-27: I5 -> I3, T-17: I5 -> I4).
* **SC-11** makes the IIoT gateway read-only toward OT (T-13: I5 -> I3).

Three risks remain **High** after treatment (T-01, T-06, T-26). See the residual-risk discussion in [security-recommendations.md](../controls/security-recommendations.md#residual-risk).

Outputs: [risk-register.xlsx](risk-register.xlsx) · [risk-matrix.png](risk-matrix.png) · [top-risks.md](top-risks.md)

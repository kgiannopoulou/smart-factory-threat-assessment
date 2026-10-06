# Threat-modelling methodology

## Approach

1. **Model the system.** Build an [asset inventory](../architecture/asset-inventory.md), zones and trust boundaries ([network-zones.png](../diagrams/network-zones.png)), and a Level-1 **data flow diagram** ([data-flow-diagram.png](../diagrams/data-flow-diagram.png)) with numbered flows DF-01 to DF-20.
2. **Apply STRIDE per element.** Each DFD element type is checked against the STRIDE categories that normally apply to it (table below). The analysis focuses on **flows that cross trust boundaries**, because those are where an attacker moves from lower to higher trust.
3. **Record threats** in the [STRIDE threat register](stride-threat-register.md). Each threat has an asset, data flow, threat actor, attack path, existing controls, likelihood, impact, mitigation and residual risk.
4. **Chain threats into attack scenarios** ([attack-scenarios.md](attack-scenarios.md)). This tests whether individual threats combine into a realistic path to an operational consequence, and maps each step to MITRE ATT&CK for ICS.
5. **Score and prioritise** using the documented [5x5 risk methodology](../risk-assessment/risk-methodology.md).
6. **Recommend controls** and map them to IEC 62443, NIST SP 800-82r3 / 800-53 and NIST CSF 2.0, then sequence them into a [roadmap](../controls/remediation-roadmap.md).

This sequence follows the zone/conduit risk-assessment flow of IEC 62443-3-2 (identify the system under consideration, partition it into zones and conduits, assess risk, compare against target security levels, and document countermeasures). STRIDE is used as the threat-identification technique within that flow.

## STRIDE

| Category | Property violated | OT example in this assessment |
|---|---|---|
| **S**poofing | Authentication | Stolen vendor credentials used on the VPN (T-01) |
| **T**ampering | Integrity | Unauthorized PLC logic download (T-02) |
| **R**epudiation | Non-repudiation | Shared HMI account, so actions can't be attributed (T-03) |
| **I**nformation disclosure | Confidentiality | Cleartext Modbus reveals the process model (T-16) |
| **D**enial of service | Availability | Ransomware encrypts SCADA/HMI (T-17) |
| **E**levation of privilege | Authorization | Permissive IT/OT firewall lets the corporate LAN reach OT (T-10) |

In OT the priority order is usually **availability and integrity first, confidentiality last**. Tampering and DoS threats against Level 1-2 therefore score higher on impact than disclosure threats.

## STRIDE per element

| Element type | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| External entity (vendor, operator, cloud) | X | | X | | | |
| Process (HMI, EWS, PLC, jump server, gateway) | X | X | X | X | X | X |
| Data store (historian, replica) | | X | (logs) | X | X | |
| Data flow (Modbus, RDP, VPN, MQTT) | | X | | X | X | |

## Threat actors

| ID | Actor | Capability / motivation |
|---|---|---|
| TA-1 | Cybercriminal / ransomware affiliate | Financially motivated. Commodity tooling. Targets IT and accepts OT disruption as leverage |
| TA-2 | Initial access broker | Sells VPN and RDP credentials and footholds |
| TA-3 | State-sponsored group with ICS capability | Patient and well-resourced. Able to manipulate the process |
| TA-4 | Malicious insider | Has legitimate access and knows the process |
| TA-5 | Negligent insider or contractor | Brings in malware by accident (USB, unapproved tools) |
| TA-6 | Compromised third party / supply chain | Vendor or cloud provider used as a conduit |
| TA-7 | Opportunistic attacker / hacktivist | Scans for exposed devices and default credentials |

## Limitations

* This is a desk-based assessment of a **fictional** environment. No technical testing was done, so findings are based on stated configuration.
* Likelihood ratings are expert judgement informed by publicly reported OT incidents and threat reporting. They are not statistical frequencies.
* Hardwired safety circuits are assumed to be independent of the networked control system. If a networked safety PLC were present, several impact ratings would change.

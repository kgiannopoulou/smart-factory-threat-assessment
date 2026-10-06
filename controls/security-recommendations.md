# Security recommendations

The recommendations below turn the [threat register](../threat-model/stride-threat-register.md) and [risk assessment](../risk-assessment/top-risks.md) into prioritised actions. Each control is traced to the threats it mitigates and mapped to IEC 62443, NIST SP 800-82r3 / 800-53 and NIST CSF 2.0 ([full mapping](framework-mapping.md)). The actions are sequenced in a [30/90/365-day roadmap](remediation-roadmap.md).

## Guiding principles

1. **Fix the boundaries before buying tools.** Four of the five Critical risks come from architecture and identity decisions: a shared AD domain, permissive firewall rules, unmanaged remote access and an LTE bypass. None of them needs a new product to fix.
2. **Protect the paths to Level 1.** Every scenario that reaches a PLC goes through the engineering workstation, the jump server or a flat network. These are the chokepoints.
3. **Assume something will get through, and recover fast.** Offline backups and an OT incident-response plan reduce *impact* where prevention reduces only likelihood.
4. **Bring third parties inside the security model.** The vendor and the IIoT supplier both created paths that bypass Apex's controls.

## Control catalogue

| ID | Control | What "done" looks like | Mitigates |
|---|---|---|---|
| SC-01 | Secure vendor remote access | Named RoboServ accounts with MFA, disabled by default and enabled per approved ticket; VPN limited to vendor source IPs; TeamViewer removed | T-01, T-24, T-26 |
| SC-02 | IT/OT segmentation via the IDMZ | No direct Enterprise->OT rules; OT hosts in a separate OT identity domain; historian replication pushed from OT | T-07, T-08, T-10, T-17, T-18, T-24, T-29 |
| SC-03 | Control-zone conduit and switch hardening | Firewall between L2-L3 and L1 that allows only SCADA/OPC -> PLC Modbus and EWS -> PLC engineering traffic; port security; cabinets locked | T-02, T-05, T-15, T-16, T-20, T-21, T-22, T-30 |
| SC-04 | Privileged access management & least privilege | Domain Admins reduced to named people; operators not local admins; vault + just-in-time access for OT and vendor admins | T-01, T-06, T-07, T-08, T-12, T-29 |
| SC-05 | Hardened jump server | Off-domain, MFA, session recording, approved-target list, no clipboard/drive mapping by default | T-07, T-25 |
| SC-06 | EWS & HMI hardening | Application allowlisting, USB device control + scanning kiosk, no Internet egress | T-06, T-17, T-24, T-28 |
| SC-07 | PLC change management & integrity | Key switches in RUN; version-controlled projects; scheduled online-vs-golden compare | T-02, T-21, T-22, T-23 |
| SC-08 | OT backup & recovery | Offline/immutable copies of PLC, HMI and historian configuration and server images; quarterly restore test | T-17, T-18, T-27 |
| SC-09 | Centralised security logging | OT log collector in the IDMZ -> SIEM; named HMI logins | T-03, T-04, T-19, T-23, T-25 |
| SC-10 | OT network monitoring (passive IDS) | Alerts on program download, mode change, new Modbus writer, new device | T-02, T-05, T-15, T-16, T-22, T-26, T-30 |
| SC-11 | IIoT gateway security architecture | LTE bypass removed; data via an IDMZ broker; gateway read-only toward OT; signed firmware | T-11, T-12, T-13, T-14 |
| SC-12 | Enterprise phishing & endpoint defence | DMARC enforcement, sandboxing, EDR, phishing simulation | T-09 |
| SC-13 | OT asset inventory & vulnerability management | Inventory with firmware versions; 14-day patch SLA for Internet-facing devices | T-06, T-11, T-21, T-26 |
| SC-14 | OT incident response & manual operations | OT playbooks, authority to isolate IT/OT, manual-mode procedures, annual tabletop | T-17, T-28 |
| SC-15 | Application-level access control | Role-based HMI accounts; OPC UA SignAndEncrypt + user auth; historian roles | T-03, T-04, T-19, T-20 |
| SC-16 | Supplier security requirements | IEC 62443-2-4 aligned clauses in RoboServ and IIoT/cloud contracts | T-01, T-12, T-13 |
| SC-17 | Network resilience for control traffic | Storm control, QoS, PLC comms watchdogs | T-05 |

## Focused framework mapping (top controls)

| Control | IEC 62443-3-3 | NIST SP 800-53 (800-82r3 overlay) | NIST CSF 2.0 |
|---|---|---|---|
| SC-01 Secure vendor remote access | SR 1.1 RE2 (MFA for untrusted networks), SR 1.13 (access via untrusted networks) | AC-17, IA-2(1), IA-2(2), PS-7 | PR.AA-03, GV.SC |
| SC-02 IT/OT segmentation | SR 5.1 (network segmentation), SR 5.2 (zone boundary protection) | SC-7, AC-4 | PR.IR-01 |
| SC-03 Control-zone conduit | SR 5.1, SR 5.2, SR 7.7 (least functionality) | SC-7, CM-7, PE-3 | PR.IR-01 |
| SC-04 PAM & least privilege | SR 1.3 (account mgmt), SR 1.5 (authenticator mgmt), SR 2.1 (authorization enforcement) | AC-2, AC-6, IA-5 | PR.AA-01, PR.AA-05 |
| SC-07 PLC change management | SR 3.4 (software & information integrity) | CM-3, CM-5, SI-7 | PR.PS-01 |
| SC-08 Backup & recovery | SR 7.3 (backup), SR 7.4 (recovery & reconstitution) | CP-9, CP-10 | PR.DS-11, RC.RP |
| SC-10 OT monitoring | SR 6.2 (continuous monitoring) | SI-4 | DE.CM-01 |
| SC-16 Supplier requirements | IEC 62443-2-4 | SA-9, SR-6 | GV.SC-05 |

## Prioritised roadmap (summary)

| Horizon | Theme | Actions | Risks most reduced |
|---|---|---|---|
| **0-30 days** | Close the open doors | MFA + named vendor accounts (R-01); remove TeamViewer (R-02); patch & restrict VPN (R-03); remove any-any and direct IT->OT rules (R-04); privileged-account review (R-05); offline PLC/HMI backups (R-06); lock down IIoT gateway management (R-07); PLC keys to RUN (R-08) | T-01, T-24, T-10, T-27, T-11, T-02 |
| **30-90 days** | Rebuild the boundaries | Separate OT identity domain (R-09); L2-L3/L1 conduit firewall (R-10); hardened jump server (R-11); EWS/HMI hardening (R-12); central logging + named HMI accounts (R-13); IIoT via IDMZ + OPC UA security (R-14); historian push-only (R-15); phishing/EDR (R-16) | T-08, T-07, T-15, T-06, T-03, T-29 |
| **3-12 months** | Detect, govern, sustain | OT monitoring (R-17); formal PLC change management (R-18); PAM (R-19); OT IR playbooks + tabletop (R-20); supplier contracts (R-21); OT vulnerability management + restore tests (R-22) | T-22, T-23, T-26, T-17 |

All eight 0-30 day actions are **Low-effort configuration changes**. They directly treat three of the five Critical risks (T-01, T-24, T-10) and cut the recovery-time impact of a fourth (T-17), all before any capital spend. T-08 (AD compromise), and with it the root cause of T-17, needs the OT domain separation in R-09.

Full detail with owners and effort: [remediation-roadmap.md](remediation-roadmap.md).

## Residual risk

After all recommended controls, the profile moves from **5 Critical / 18 High / 6 Medium / 1 Low** to **0 Critical / 3 High / 18 Medium / 9 Low**.

Three risks stay **High** and should be formally accepted by the Plant Manager with compensating monitoring:

| Threat | Residual | Why it stays High | Compensating measures |
|---|---|---|---|
| T-01 Stolen vendor credentials | 2 x 5 = 10 | Remote vendor support is a business requirement. MFA can still be phished or its prompts approved by mistake | Phishing-resistant MFA (FIDO2) for vendors as a next step; session recording; OT IDS alerting on vendor sessions |
| T-06 EWS privilege escalation | 2 x 5 = 10 | The EWS has to be able to program PLCs. That capability cannot be removed, only controlled | Allowlisting, golden-copy compare, EWS powered off or network-disconnected when not in use |
| T-26 VPN appliance exploitation | 2 x 5 = 10 | Edge-device zero-days are outside Apex's control | 14-day patch SLA, exposure restricted to vendor IPs, consider a vendor-access broker with no inbound listener |

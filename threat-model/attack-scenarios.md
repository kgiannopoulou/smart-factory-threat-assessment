# Attack scenarios

The five scenarios below chain individual STRIDE threats into end-to-end paths. Each path leads to an operational consequence. They are written for risk communication and defensive planning: each step names the **threat ID**, the **MITRE ATT&CK for ICS** technique where one applies, the **detection opportunity**, and the **control that breaks the chain**.

| ID | Scenario | Actor | Entry point | Consequence | STRIDE |
|---|---|---|---|---|---|
| AS-01 | Compromised vendor remote access -> PLC manipulation | TA-2 / TA-1 | Vendor VPN | Line stop, equipment damage | S, E, T, D, R |
| AS-02 | Corporate workstation -> AD compromise -> IT/OT pivot | TA-1 / TA-3 | Phishing email | Unauthorized commands to PLCs | S, E, T, I |
| AS-03 | Compromised engineering workstation -> covert PLC logic change | TA-3 / TA-4 | USB media / insider | Quality escape, recall | T, E, R, D |
| AS-04 | IIoT gateway compromise -> OT intrusion | TA-7 / TA-6 | LTE-connected gateway | OT foothold outside all IT controls | E, T, S, I, D |
| AS-05 | Ransomware -> historian/HMI outage -> production stop | TA-1 | Phishing email | Multi-day plant outage, loss of traceability | S, E, D |

---

## AS-01 - Compromised vendor remote access -> PLC manipulation

**Threat actor:** initial access broker selling to a ransomware affiliate (TA-2 -> TA-1)
**Entry point:** RoboServ SSL VPN account · **Target:** PLC-01 / PLC-02 · **Impact:** production shutdown, possible equipment damage
**STRIDE:** Spoofing + Elevation of privilege + Tampering + Denial of service + Repudiation

```
Vendor engineer phished / credentials sold          T-01  (S)
        |
SSL VPN login as shared 'roboserv' account          T-01  (S)   - or edge appliance exploited, T-26 (E)
        |
RDP to jump server -> RDP to engineering WS          T-07  (E)   - or TeamViewer straight to EWS, T-24 (S)
        |
Local admin on EWS, PLC engineering software         T-06  (E)
        |
Program download / STOP command to PLC               T-02  (T), T-21 (D)
        |
Line stop; no record of who changed what             T-23, T-25 (R)
```

| Step | ATT&CK for ICS | Detection opportunity | Control that breaks the chain |
|---|---|---|---|
| VPN login with valid credentials | T0822 External Remote Services, T0859 Valid Accounts | VPN login outside an approved ticket window, or from an unusual geography | **SC-01** MFA + named accounts disabled by default |
| Edge appliance exploitation (alternative) | T0819 Exploit Public-Facing Application | Appliance integrity check, unexpected admin sessions | **SC-13** patch SLA, **SC-01** source-IP restriction |
| TeamViewer path (alternative) | T0822 External Remote Services | Outbound remote-tool traffic from OT | **SC-01** removal, **SC-02** egress deny |
| RDP through jump server | T0886 Remote Services | Session recording, logon to EWS from an unexpected source | **SC-05** hardened jump server |
| PLC download / mode change | T0843 Program Download, T0858 Change Operating Mode, T0816 Device Restart/Shutdown | OT IDS alert on program download or STOP outside a change window | **SC-07** key switch in RUN, **SC-10** OT monitoring |
| Consequence | T0813 Denial of Control, T0828 Loss of Productivity and Revenue | - | **SC-08** golden-copy restore |

**Why it matters:** third-party remote access is one of the most common ways into OT environments. At Apex it ranks among the top risks (T-01 Critical, T-24 Critical). Turning on MFA and disabling the vendor account by default are the cheapest high-value actions in the whole roadmap (R-01, R-02).

---

## AS-02 - Corporate workstation -> AD compromise -> IT/OT pivot

**Threat actor:** TA-1 or TA-3 · **Entry point:** phishing email to an office user · **Target:** SCADA/HMI and PLCs
**STRIDE:** Spoofing + Elevation of privilege + Tampering + Information disclosure

```
Phishing email -> malware on office workstation       T-09  (S)
        |
Credential theft / AD privilege escalation            T-08  (S)
        |
Domain credentials accepted by OT hosts (same domain)  T-08  (S)
        |
Direct RDP/SMB through permissive IT/OT rules          T-10  (E)   or via jump server, T-07 (E)
        |
Passive capture of Modbus traffic -> process map       T-16  (I)
        |
Unauthenticated Modbus writes to PLCs                  T-15  (T)
```

| Step | ATT&CK for ICS | Detection opportunity | Control that breaks the chain |
|---|---|---|---|
| Phishing | T0865 Spearphishing Attachment | Email sandbox verdicts, EDR | **SC-12** |
| Valid domain accounts into OT | T0859 Valid Accounts | Logon by corporate admin accounts to OT hosts | **SC-02** separate OT identity domain, **SC-04** tiering |
| IT/OT lateral movement | T0886 Remote Services | Firewall logs: Enterprise -> OT sessions that bypass the IDMZ | **SC-02** deny-by-default IT/OT firewall |
| Reconnaissance | T0842 Network Sniffing, T0861 Point & Tag Identification | New host talking Modbus | **SC-10** |
| Unauthorized commands | T0855 Unauthorized Command Message, T0831 Manipulation of Control | Modbus writes from a source other than the SCADA server | **SC-03** conduit allowlist |

**Why it matters:** this chain uses **no OT-specific exploit**. It works only because of identity and segmentation design decisions (O-1, O-2, O-3). Fixing the identity boundary (R-09) removes the single shared dependency behind T-07, T-08 and T-17.

---

## AS-03 - Compromised engineering workstation -> covert PLC logic change

**Threat actor:** state-sponsored group (TA-3) or malicious insider (TA-4) · **Entry point:** removable media or legitimate engineer access · **Target:** PLC-02 robotic welding cell
**STRIDE:** Tampering + Elevation of privilege + Repudiation + Denial of service

```
Infected USB used to transfer project files            T-28  (T)
        |
Malware runs with local admin on EWS                   T-06  (E)
        |
Modified weld parameters downloaded to PLC-02          T-02, T-22  (T)
        |
Parts pass visual inspection but are under-welded      T-22  (T)
        |
No versioning: change can't be attributed or detected  T-23  (R)
        |
Only copy of the good program is on the infected EWS   T-27  (D)
```

| Step | ATT&CK for ICS | Detection opportunity | Control that breaks the chain |
|---|---|---|---|
| Removable media | T0847 Replication Through Removable Media | USB device-control logs | **SC-06** USB control + scanning kiosk |
| Code execution on EWS | T0863 User Execution | Application allowlisting block events | **SC-06** allowlisting, **SC-04** no local admin |
| Logic / parameter change | T0889 Modify Program, T0836 Modify Parameter | Online-vs-golden program compare, OT IDS download alert | **SC-07** change management + integrity checks |
| Consequence | T0879 Damage to Property, T0828 Loss of Productivity and Revenue | End-of-line testing (1 in 200 sampled) | **SC-07**, **SC-08** golden copies |

**Why it matters:** this is the **quality-escape** scenario that is specific to automotive. The plant keeps running, so no one notices until parts fail in service. That leads to an OEM recall and possible loss of the contract. The impact is Severe (5) even though no line stops.

---

## AS-04 - IIoT gateway compromise -> OT intrusion

**Threat actor:** opportunistic attacker scanning for exposed devices (TA-7), or compromise of the IIoT supplier (TA-6) · **Entry point:** gateway web admin over the LTE link · **Target:** OPC UA server and PLCs
**STRIDE:** Elevation of privilege + Tampering + Spoofing + Information disclosure + Denial of service

```
Gateway admin interface reachable over LTE with default credentials   T-11  (E)
   or malicious firmware pushed from compromised cloud platform        T-13  (T)
        |
Gateway is dual-homed: attacker now inside OT, outside every IT control
        |
Anonymous OPC UA access: browse / write tags                         T-20  (S)
        |
Network discovery, traffic capture                                   T-16  (I)
        |
Modbus writes or flooding of the PLC network                         T-15  (T), T-05  (D)
```

| Step | ATT&CK for ICS | Detection opportunity | Control that breaks the chain |
|---|---|---|---|
| Internet-exposed device | T0883 Internet Accessible Device, T0812 Default Credentials | External exposure scan of the LTE IP | **SC-11** disable inbound management, change credentials |
| Supply-chain update | T0862 Supply Chain Compromise | Firmware hash vs. vendor-published value | **SC-11** signed firmware, **SC-16** supplier clauses |
| OPC UA abuse | T0859 Valid Accounts (anonymous), T0861 Point & Tag Identification | OPC UA sessions from unexpected clients | **SC-15** SignAndEncrypt + user auth |
| Network effects | T0855 Unauthorized Command Message, T0814 Denial of Service | OT IDS | **SC-03**, **SC-10**, **SC-17** |

**Why it matters:** smart-factory projects often add connectivity **outside** the security architecture. The fix is architectural rather than a product purchase. Route the gateway through the IDMZ and make it read-only toward OT (R-07, R-14). After that, a compromised cloud can no longer reach the PLCs, and T-13's impact drops from 5 to 3.

---

## AS-05 - Ransomware -> historian/HMI outage -> production stop

**Threat actor:** ransomware affiliate (TA-1) · **Entry point:** phishing · **Target:** IT and OT Windows estate
**STRIDE:** Spoofing + Elevation of privilege + Denial of service

```
Phishing -> foothold -> domain admin                  T-09, T-08  (S)
        |
Ransomware deployed by GPO / SMB to all domain hosts, including OT (same domain)
        |                                             T-10, T-29  (E)
SCADA servers, HMIs and historian encrypted           T-17, T-18  (D)
        |
Operators lose view; plant stops as a precaution
        |
No offline PLC/HMI backups -> recovery takes days to weeks   T-27  (D)
```

| Step | ATT&CK (ICS / Enterprise) | Detection opportunity | Control that breaks the chain |
|---|---|---|---|
| Domain-wide deployment | T0859 Valid Accounts; Enterprise T1484 Domain Policy Modification | New GPO / mass service creation | **SC-02** separate OT domain, **SC-04** |
| Encryption of OT hosts | Enterprise T1486 Data Encrypted for Impact; ICS T0815 Denial of View, T0809 Data Destruction | EDR / canary files on OT servers | **SC-06**, **SC-14** isolate IT/OT decision |
| Consequence | T0826 Loss of Availability, T0828 Loss of Productivity and Revenue | - | **SC-08** offline backups + tested restore |

**Why it matters:** in publicly reported manufacturing ransomware incidents, production often stops **even when the PLCs are untouched**. The cause is loss of visibility or of business systems, or a precautionary shutdown. Apex's risk comes mostly from **recovery time**, which is why offline backups (R-06) appear in the first 30 days.

---

## Cross-scenario view

| Threat | AS-01 | AS-02 | AS-03 | AS-04 | AS-05 |
|---|:-:|:-:|:-:|:-:|:-:|
| T-08 AD compromise grants OT access | | X | | | X |
| T-10 Permissive IT/OT firewall | | X | | | X |
| T-06 EWS privilege escalation | X | | X | | |
| T-02 Unauthorized PLC logic modification | X | | X | | |
| T-15 Unauthenticated Modbus writes | | X | | X | |
| T-27 No usable PLC/HMI backup | | | X | | X |

The threats that appear in several scenarios are the **chokepoints**. Fixing them breaks more than one path, so the [Top 10 ranking](../risk-assessment/top-risks.md) uses scenario count as its tie-breaker.

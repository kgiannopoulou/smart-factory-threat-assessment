"""
Single source of truth for the Apex Manufacturing threat & risk assessment.

Every register (xlsx), generated markdown table, diagram and the PDF report is
built from the structures in this file, so IDs and scores stay consistent across
deliverables. Edit here, then run `python tools/build_all.py`.

Apex Manufacturing Ltd. is a FICTIONAL company. Any resemblance to a real
organisation is coincidental.
"""

COMPANY = {
    "name": "Apex Manufacturing Ltd.",
    "site": "Plant 1 (single-site automotive components plant)",
    "product": "Machined and robot-welded brake caliper brackets and suspension mounts for two automotive OEMs",
    "employees": "~450 (320 office/IT users, 130 shop-floor)",
    "shifts": "3 shifts, 24x5 production",
    "production_value": "~£180,000 of finished goods per production day",
    "quality_regime": "IATF 16949 - weld and torque records must be retained for part traceability",
}

ASSESSMENT = {
    "title": "Smart Factory Cybersecurity Threat & Risk Assessment",
    "client": COMPANY["name"],
    "version": "1.0",
    "date": "October 2026",
    "author": "K. Giannopoulou",
    "classification": "Confidential - fictional case study for portfolio use",
}

# --------------------------------------------------------------------------- #
# Zones (IEC 62443-3-2 style) and trust boundaries
# --------------------------------------------------------------------------- #
# sl_t = indicative target security level, sl_a = indicative achieved level
# observed during the assessment. Indicative only - not a formal 62443-3-2 SL
# determination.
ZONES = [
    {"id": "Z0", "name": "Internet", "purdue": "-", "sl_t": "-", "sl_a": "-",
     "desc": "Untrusted public networks; vendor and attacker origin."},
    {"id": "Z1", "name": "Enterprise", "purdue": "L4-L5", "sl_t": "IT baseline", "sl_a": "-",
     "desc": "Corporate LAN: workstations, Active Directory, ERP, email."},
    {"id": "Z2", "name": "Industrial DMZ", "purdue": "L3.5", "sl_t": "SL 2", "sl_a": "SL 1",
     "desc": "Brokering zone between IT and OT: historian replica, jump server, remote-access gateway."},
    {"id": "Z3", "name": "OT Site Operations", "purdue": "L2-L3", "sl_t": "SL 2", "sl_a": "SL 1",
     "desc": "SCADA/HMI, engineering workstation, historian, OPC UA server."},
    {"id": "Z4", "name": "Control", "purdue": "L1", "sl_t": "SL 2", "sl_a": "SL 0-1",
     "desc": "PLC-01 conveyor, PLC-02 robotic welding cell, PLC-03 packaging."},
    {"id": "Z5", "name": "Physical Process & Safety", "purdue": "L0", "sl_t": "n/a (hardwired)", "sl_a": "-",
     "desc": "Sensors, drives, actuators; hardwired safety circuits (e-stops, light curtains, safety relays)."},
    {"id": "Z6", "name": "IIoT / Cloud", "purdue": "outside model", "sl_t": "SL 2", "sl_a": "SL 0-1",
     "desc": "Wireless vibration sensors, IIoT gateway with LTE uplink, SaaS analytics platform."},
    {"id": "Z7", "name": "Third-party Vendor", "purdue": "external", "sl_t": "contractual", "sl_a": "-",
     "desc": "RoboServ Automation GmbH (fictional) - remote PLC and robot-cell maintenance."},
]

TRUST_BOUNDARIES = [
    {"id": "TB-1", "between": "Internet (Z0) <-> Enterprise (Z1)",
     "enforced_by": "Perimeter firewall", "state": "Enforced",
     "observation": "Standard IT perimeter; email and web filtering in place."},
    {"id": "TB-2", "between": "Enterprise (Z1) <-> Industrial DMZ (Z2)",
     "enforced_by": "IT/OT firewall (IT-facing leg)", "state": "Partially enforced",
     "observation": "Three-legged firewall managed by IT. Rule base contains 'temporary' any-any rule from 2024 robot-cell project and direct RDP/SMB from the IT admin subnet."},
    {"id": "TB-3", "between": "Industrial DMZ (Z2) <-> OT Site Operations (Z3)",
     "enforced_by": "IT/OT firewall (OT-facing leg)", "state": "Partially enforced",
     "observation": "Historian replication is bidirectional SQL; AD authentication traffic passes from OT hosts straight to corporate domain controllers, bypassing the DMZ."},
    {"id": "TB-4", "between": "OT Site Operations (Z3) <-> Control (Z4)",
     "enforced_by": "None (routed on OT core switch, no ACLs)", "state": "Not enforced",
     "observation": "Any OT host can reach any PLC on any port. PLCs are left in REMOTE key position."},
    {"id": "TB-5", "between": "Control (Z4) <-> Physical Process & Safety (Z5)",
     "enforced_by": "Hardwired I/O; independent hardwired safety circuits", "state": "Physically enforced",
     "observation": "Safety functions (e-stop, light curtains, door interlocks) are hardwired and not programmable from the network - assumed independent of PLC logic."},
    {"id": "TB-6", "between": "OT (Z3) <-> IIoT / Cloud (Z6)",
     "enforced_by": "None by Apex (LTE router supplied by IIoT vendor)", "state": "Not enforced",
     "observation": "IIoT gateway is dual-homed: OT network + its own LTE uplink to the Internet. This path bypasses the IDMZ entirely."},
    {"id": "TB-7", "between": "Vendor (Z7) <-> Apex (Z2/Z3)",
     "enforced_by": "SSL VPN + contract", "state": "Weak",
     "observation": "Single shared vendor VPN account, password-only, always enabled. TeamViewer found installed on the engineering workstation as an 'emergency' path."},
]

# --------------------------------------------------------------------------- #
# Asset inventory
# --------------------------------------------------------------------------- #
ASSETS = [
    {"id": "A-01", "name": "Perimeter firewall", "zone": "Z1", "purdue": "L5", "criticality": "High",
     "function": "Internet edge filtering for corporate network",
     "concern": "Misconfiguration exposes internal services"},
    {"id": "A-02", "name": "Employee workstations (~320)", "zone": "Z1", "purdue": "L4", "criticality": "Medium",
     "function": "Office productivity, ERP and email clients",
     "concern": "Phishing / malware foothold"},
    {"id": "A-03", "name": "Active Directory (apex.local)", "zone": "Z1", "purdue": "L4", "criticality": "Critical",
     "function": "Identity and authentication for IT and (currently) OT hosts",
     "concern": "Credential compromise grants OT access"},
    {"id": "A-04", "name": "ERP system", "zone": "Z1", "purdue": "L4", "criticality": "High",
     "function": "Orders, production planning, shipping",
     "concern": "Ransomware stops order-to-ship process"},
    {"id": "A-05", "name": "Email service (cloud-hosted)", "zone": "Z1", "purdue": "L4", "criticality": "Medium",
     "function": "Corporate email",
     "concern": "Phishing delivery vector"},
    {"id": "A-06", "name": "IT/OT firewall (three-legged)", "zone": "Z2", "purdue": "L3.5", "criticality": "Critical",
     "function": "Separates Enterprise, IDMZ and OT",
     "concern": "Permissive rules defeat segmentation"},
    {"id": "A-07", "name": "Historian replica", "zone": "Z2", "purdue": "L3.5", "criticality": "High",
     "function": "Read-only copy of process data for business users",
     "concern": "Pivot into OT via replication; data disclosure"},
    {"id": "A-08", "name": "Jump server", "zone": "Z2", "purdue": "L3.5", "criticality": "High",
     "function": "Brokered RDP from IT / vendor into OT",
     "concern": "Pivot point into OT"},
    {"id": "A-09", "name": "Remote-access gateway (SSL VPN)", "zone": "Z2", "purdue": "L3.5", "criticality": "Critical",
     "function": "Internet-facing VPN for vendor remote support",
     "concern": "Internet-exposed edge device; credential attacks"},
    {"id": "A-10", "name": "SCADA server / HMI (2 operator stations)", "zone": "Z3", "purdue": "L2", "criticality": "Critical",
     "function": "Operator supervision and control of all three lines",
     "concern": "Manipulated commands; loss of view"},
    {"id": "A-11", "name": "Engineering workstation (EWS)", "zone": "Z3", "purdue": "L2", "criticality": "Critical",
     "function": "PLC/robot programming; holds only copies of PLC projects",
     "concern": "Malware / credential theft -> PLC logic changes"},
    {"id": "A-12", "name": "Process historian", "zone": "Z3", "purdue": "L3", "criticality": "High",
     "function": "Stores process and quality (weld/torque) records",
     "concern": "Integrity of traceability data; availability"},
    {"id": "A-13", "name": "OPC UA server", "zone": "Z3", "purdue": "L3", "criticality": "High",
     "function": "Aggregates PLC tags for historian and IIoT gateway",
     "concern": "Unauthorized access; tag writes"},
    {"id": "A-14", "name": "PLC-01 Conveyor", "zone": "Z4", "purdue": "L1", "criticality": "Critical",
     "function": "Controls material flow between machining and welding",
     "concern": "Unauthorized logic changes / stop commands"},
    {"id": "A-15", "name": "PLC-02 Robotic welding cell", "zone": "Z4", "purdue": "L1", "criticality": "Critical",
     "function": "Sequences robot arm and weld controller",
     "concern": "Parameter tampering -> defective welds, equipment damage"},
    {"id": "A-16", "name": "PLC-03 Packaging", "zone": "Z4", "purdue": "L1", "criticality": "High",
     "function": "Packing, labelling and palletising",
     "concern": "Disruption of shipping; labelling errors"},
    {"id": "A-17", "name": "Field devices (sensors, drives, actuators)", "zone": "Z5", "purdue": "L0", "criticality": "High",
     "function": "Physical sensing and actuation",
     "concern": "Driven to unsafe/undesired states by PLC"},
    {"id": "A-18", "name": "Hardwired safety circuits", "zone": "Z5", "purdue": "L0", "criticality": "Critical",
     "function": "E-stops, light curtains, door interlocks, safety relays",
     "concern": "Out of cyber scope - not networked (assumption)"},
    {"id": "A-19", "name": "IIoT gateway + LTE router", "zone": "Z6", "purdue": "-", "criticality": "High",
     "function": "Collects vibration and OPC UA data, ships to cloud",
     "concern": "Uncontrolled OT/Internet bridge"},
    {"id": "A-20", "name": "Wireless vibration sensors (24)", "zone": "Z6", "purdue": "L0", "criticality": "Low",
     "function": "Condition monitoring on spindles and conveyor motors",
     "concern": "Spoofed readings"},
    {"id": "A-21", "name": "Cloud analytics platform (SaaS)", "zone": "Z6", "purdue": "-", "criticality": "Medium",
     "function": "Predictive maintenance dashboards",
     "concern": "Data exposure; malicious updates to gateway"},
    {"id": "A-22", "name": "Vendor remote support (RoboServ)", "zone": "Z7", "purdue": "-", "criticality": "High",
     "function": "External engineers maintaining PLCs and robot cell",
     "concern": "Third-party credential compromise"},
    {"id": "A-23", "name": "OT network switches", "zone": "Z3", "purdue": "L2", "criticality": "High",
     "function": "OT core and cell access switching",
     "concern": "Flat network; open ports in control cabinets"},
]

# --------------------------------------------------------------------------- #
# Data flows (DFD)
# --------------------------------------------------------------------------- #
DATA_FLOWS = [
    {"id": "DF-01", "src": "Operator", "dst": "SCADA/HMI", "proto": "Local console (keyboard/touch)", "tb": "-",
     "desc": "Operator commands, setpoints, alarm acknowledgement"},
    {"id": "DF-02", "src": "SCADA/HMI", "dst": "PLC-01/02/03", "proto": "Modbus/TCP 502 (read/write)", "tb": "TB-4",
     "desc": "Supervisory reads and writes of coils/registers"},
    {"id": "DF-03", "src": "Engineering WS", "dst": "PLC-01/02/03", "proto": "PLC engineering protocol (vendor proprietary)", "tb": "TB-4",
     "desc": "Program download/upload, online edits, mode changes"},
    {"id": "DF-04", "src": "PLC-01/02/03", "dst": "Field devices", "proto": "Hardwired I/O, 4-20 mA, fieldbus", "tb": "TB-5",
     "desc": "Sensor inputs and actuator outputs"},
    {"id": "DF-05", "src": "PLC-01/02/03", "dst": "OPC UA server", "proto": "Modbus/TCP 502 (polled)", "tb": "TB-4",
     "desc": "Tag values for aggregation"},
    {"id": "DF-06", "src": "OPC UA server", "dst": "Historian", "proto": "OPC UA 4840 (SecurityMode None)", "tb": "-",
     "desc": "Process and quality data for storage"},
    {"id": "DF-07", "src": "Historian", "dst": "Historian replica", "proto": "SQL replication 1433 (bidirectional)", "tb": "TB-3",
     "desc": "Replication of process data to the IDMZ"},
    {"id": "DF-08", "src": "Business users / ERP", "dst": "Historian replica", "proto": "HTTPS reports, SQL", "tb": "TB-2",
     "desc": "OEE, quality and production reports"},
    {"id": "DF-09", "src": "Vendor engineer", "dst": "Remote-access gateway", "proto": "SSL VPN over Internet", "tb": "TB-7 / TB-1",
     "desc": "Vendor remote session establishment"},
    {"id": "DF-10", "src": "Remote-access gateway", "dst": "Jump server", "proto": "RDP 3389", "tb": "-",
     "desc": "Vendor session brokered to jump server"},
    {"id": "DF-11", "src": "Jump server", "dst": "Engineering WS", "proto": "RDP 3389", "tb": "TB-3",
     "desc": "Second-hop RDP into OT"},
    {"id": "DF-12", "src": "IT administrator", "dst": "Jump server", "proto": "RDP 3389", "tb": "TB-2",
     "desc": "IT administration of OT Windows hosts"},
    {"id": "DF-13", "src": "OT Windows hosts", "dst": "Active Directory", "proto": "Kerberos, LDAP, SMB (direct)", "tb": "TB-3 + TB-2 (bypasses IDMZ)",
     "desc": "OT hosts are joined to the corporate domain"},
    {"id": "DF-14", "src": "OPC UA server", "dst": "IIoT gateway", "proto": "OPC UA 4840 subscription", "tb": "TB-6",
     "desc": "Selected tags forwarded for analytics"},
    {"id": "DF-15", "src": "Vibration sensors", "dst": "IIoT gateway", "proto": "Proprietary 2.4 GHz wireless", "tb": "TB-6",
     "desc": "Condition-monitoring measurements"},
    {"id": "DF-16", "src": "IIoT gateway", "dst": "Cloud analytics", "proto": "MQTT/TLS 8883 over LTE", "tb": "TB-6",
     "desc": "Telemetry upload, bypassing the IDMZ"},
    {"id": "DF-17", "src": "Cloud analytics", "dst": "IIoT gateway", "proto": "HTTPS (device management)", "tb": "TB-6",
     "desc": "Remote configuration and firmware updates"},
    {"id": "DF-18", "src": "Internet", "dst": "Email / workstations", "proto": "SMTP, HTTPS", "tb": "TB-1",
     "desc": "Inbound email and web browsing"},
    {"id": "DF-19", "src": "Contractor USB media", "dst": "Engineering WS / HMI", "proto": "Removable media", "tb": "Physical",
     "desc": "Ad-hoc transfer of project files and drivers"},
    {"id": "DF-20", "src": "Internet (TeamViewer)", "dst": "Engineering WS", "proto": "TeamViewer (outbound-initiated)", "tb": "Bypasses TB-1..TB-3",
     "desc": "Unapproved vendor 'emergency' remote access discovered during assessment"},
]

# --------------------------------------------------------------------------- #
# Threat actors
# --------------------------------------------------------------------------- #
ACTORS = {
    "TA-1": "Cybercriminal / ransomware affiliate",
    "TA-2": "Initial access broker",
    "TA-3": "State-sponsored group with ICS capability",
    "TA-4": "Malicious insider",
    "TA-5": "Negligent insider or contractor",
    "TA-6": "Compromised third party / supply chain",
    "TA-7": "Opportunistic attacker / hacktivist",
}

# --------------------------------------------------------------------------- #
# Security controls (recommendations) and framework mapping
# --------------------------------------------------------------------------- #
# iec  = IEC 62443-3-3 system requirements (SR) unless another part is named
# nist = NIST SP 800-53 Rev. 5 controls as tailored by the NIST SP 800-82 Rev. 3 OT overlay
# csf  = NIST Cybersecurity Framework 2.0 categories / subcategories
CONTROLS = [
    {"id": "SC-01", "name": "Secure vendor remote access",
     "desc": "Named per-engineer vendor accounts, MFA on the VPN, accounts disabled by default and enabled per approved ticket, source-IP restriction, removal of unapproved remote tools (TeamViewer).",
     "iec": "SR 1.1 RE2, SR 1.13, SR 2.6", "nist": "AC-17, IA-2(1), IA-2(2), PS-7", "csf": "PR.AA-03, GV.SC"},
    {"id": "SC-02", "name": "IT/OT segmentation via the IDMZ",
     "desc": "Deny-by-default IT/OT firewall; no direct Enterprise->OT traffic; OT hosts moved to a separate OT identity domain; OT-initiated historian push only.",
     "iec": "SR 5.1, SR 5.2", "nist": "SC-7, AC-4", "csf": "PR.IR-01"},
    {"id": "SC-03", "name": "Control-zone conduit and switch hardening",
     "desc": "Firewall between Site Operations and Control zone with protocol allowlist (SCADA/OPC -> PLC Modbus; EWS -> PLC engineering protocol only), switch port security, unused ports disabled, cabinets locked.",
     "iec": "SR 5.1, SR 5.2, SR 7.7", "nist": "SC-7, CM-7, PE-3", "csf": "PR.IR-01, PR.AA-06"},
    {"id": "SC-04", "name": "Privileged access management & least privilege",
     "desc": "Remove shared/excess admin accounts, no local admin for operators, credential vaulting and just-in-time elevation for OT and vendor admins, password rotation for service accounts.",
     "iec": "SR 1.3, SR 1.5, SR 2.1", "nist": "AC-2, AC-6, IA-5", "csf": "PR.AA-01, PR.AA-05"},
    {"id": "SC-05", "name": "Hardened jump server",
     "desc": "Jump server off the corporate domain, MFA, session recording, clipboard/drive mapping disabled by default, can only reach approved OT targets.",
     "iec": "SR 1.13, SR 2.8, SR 5.2", "nist": "AC-17, AU-14, SC-7", "csf": "PR.AA-03, PR.PS-04"},
    {"id": "SC-06", "name": "Engineering workstation & HMI hardening",
     "desc": "Application allowlisting, USB device control with a scanning kiosk, no Internet egress, OS patching in maintenance windows, unnecessary services removed.",
     "iec": "SR 3.2, SR 2.3, SR 7.7", "nist": "CM-7(5), SI-3, MP-7", "csf": "PR.PS-05, PR.PS-01"},
    {"id": "SC-07", "name": "PLC change management & integrity",
     "desc": "PLC key switches in RUN, REMOTE/PROG only during approved change windows; version-controlled PLC projects; scheduled online-vs-golden program compare.",
     "iec": "SR 3.4, SR 2.8, SR 1.1", "nist": "CM-3, CM-5, SI-7", "csf": "PR.PS-01, DE.CM-09"},
    {"id": "SC-08", "name": "OT backup & recovery",
     "desc": "Offline/immutable backups of PLC programs, HMI/SCADA projects, historian configuration and OT server images; quarterly restore tests.",
     "iec": "SR 7.3, SR 7.4", "nist": "CP-9, CP-10", "csf": "PR.DS-11, RC.RP"},
    {"id": "SC-09", "name": "Centralised security logging",
     "desc": "OT log collector in the IDMZ forwarding Windows, firewall, VPN, jump server and HMI audit logs to the SIEM; named HMI user logins.",
     "iec": "SR 2.8, SR 2.12, SR 6.1", "nist": "AU-2, AU-6, AU-12", "csf": "PR.PS-04, DE.AE"},
    {"id": "SC-10", "name": "OT network monitoring (passive IDS)",
     "desc": "Passive OT-aware monitoring on SPAN ports in Z3/Z4 with protocol decoding (Modbus, engineering protocol), alerting on program downloads, mode changes and new hosts.",
     "iec": "SR 6.2", "nist": "SI-4", "csf": "DE.CM-01"},
    {"id": "SC-11", "name": "IIoT gateway security architecture",
     "desc": "Remove LTE bypass; route gateway via IDMZ broker; gateway read-only toward OT; certificate-based device identity; signed firmware; inbound management disabled; default credentials removed.",
     "iec": "SR 5.2, SR 1.2, SR 3.1, SR 3.4", "nist": "SC-7, IA-3, SC-8, SI-7", "csf": "PR.IR-01, PR.DS-02"},
    {"id": "SC-12", "name": "Enterprise phishing & endpoint defence",
     "desc": "Email authentication (SPF/DKIM/DMARC) and sandboxing, EDR on corporate endpoints, awareness training with phishing simulation.",
     "iec": "n/a (Enterprise zone)", "nist": "SI-3, SI-8, AT-2", "csf": "PR.AT-01, DE.CM-09"},
    {"id": "SC-13", "name": "OT asset inventory & vulnerability management",
     "desc": "Maintained inventory of OT assets/firmware; risk-based patching with a 14-day SLA for Internet-facing devices; vendor advisory subscriptions.",
     "iec": "SR 7.8, IEC 62443-2-3", "nist": "CM-8, RA-5, SI-2", "csf": "ID.AM-01, ID.RA-01"},
    {"id": "SC-14", "name": "OT incident response & manual operations",
     "desc": "OT-specific IR playbooks (ransomware, PLC manipulation), decision authority for isolating IT/OT, manual-operation procedures, annual tabletop exercise.",
     "iec": "IEC 62443-2-1 (incident handling)", "nist": "IR-4, IR-8, CP-2", "csf": "RS.MA, RC.RP"},
    {"id": "SC-15", "name": "Application-level access control (HMI, OPC UA, historian)",
     "desc": "Named role-based HMI accounts, OPC UA SecurityMode SignAndEncrypt with user authentication and no anonymous access, write access removed where not needed, historian replica access by role.",
     "iec": "SR 1.1, SR 2.1, SR 3.1, SR 4.1", "nist": "AC-3, AC-6, SC-8", "csf": "PR.AA-05, PR.DS-02"},
    {"id": "SC-16", "name": "Supplier security requirements",
     "desc": "IEC 62443-2-4 aligned security clauses for RoboServ and the IIoT/cloud provider: named accounts, MFA, breach notification, secure update process, annual review.",
     "iec": "IEC 62443-2-4", "nist": "SA-9, SR-6", "csf": "GV.SC-05"},
    {"id": "SC-17", "name": "Network resilience for control traffic",
     "desc": "Broadcast/storm control and rate limiting on OT switches, QoS for control traffic, PLC communication watchdogs with fail-safe behaviour.",
     "iec": "SR 7.1, SR 7.2", "nist": "SC-5", "csf": "PR.IR-03"},
]

# --------------------------------------------------------------------------- #
# STRIDE threat register
# --------------------------------------------------------------------------- #
# L/I = current likelihood/impact (with existing controls)
# rL/rI = residual likelihood/impact after the recommended controls
THREATS = [
    {"id": "T-01", "title": "Stolen vendor credentials used on VPN", "stride": "S",
     "assets": ["A-09", "A-22"], "flows": ["DF-09"],
     "desc": "An attacker who phishes or buys RoboServ credentials logs in to the SSL VPN as the shared 'roboserv' account and is indistinguishable from the vendor.",
     "actor": "TA-2, TA-1", "path": "Vendor phishing / credential marketplace -> SSL VPN -> jump server",
     "existing": "Password-only VPN; single shared vendor account; account always enabled",
     "L": 4, "I": 5, "controls": ["SC-01", "SC-04", "SC-16"], "rL": 2, "rI": 5},
    {"id": "T-02", "title": "Unauthorized PLC logic modification", "stride": "T",
     "assets": ["A-11", "A-14", "A-15", "A-16"], "flows": ["DF-03"],
     "desc": "Any host that reaches a PLC on its engineering port can download modified logic, because PLCs are in REMOTE mode and the protocol has no authentication.",
     "actor": "TA-1, TA-3, TA-4", "path": "Compromised EWS or any OT host -> engineering protocol -> PLC",
     "existing": "Vendor engineering software requires a project password (offline only)",
     "L": 3, "I": 5, "controls": ["SC-07", "SC-03", "SC-10"], "rL": 1, "rI": 5},
    {"id": "T-03", "title": "Operator actions cannot be attributed", "stride": "R",
     "assets": ["A-10"], "flows": ["DF-01"],
     "desc": "All operators share one HMI login; setpoint changes and alarm acknowledgements cannot be tied to an individual during incident or quality investigations.",
     "actor": "TA-4, TA-5", "path": "Shared 'operator' account on HMI",
     "existing": "HMI event log stored locally, overwritten after 7 days",
     "L": 4, "I": 3, "controls": ["SC-15", "SC-09"], "rL": 2, "rI": 3},
    {"id": "T-04", "title": "Unauthorized access to production data", "stride": "I",
     "assets": ["A-07"], "flows": ["DF-08"],
     "desc": "All 'Domain Users' can read the historian replica, exposing recipes, cycle times and OEM quality data to any compromised corporate account.",
     "actor": "TA-1, TA-4", "path": "Corporate account -> historian replica web/SQL",
     "existing": "Domain authentication only; no role-based restriction",
     "L": 3, "I": 3, "controls": ["SC-15", "SC-09"], "rL": 2, "rI": 3},
    {"id": "T-05", "title": "Network flooding disrupts PLC communications", "stride": "D",
     "assets": ["A-14", "A-15", "A-16", "A-23"], "flows": ["DF-02", "DF-05"],
     "desc": "Broadcast storms, aggressive scanning or worm traffic on the flat OT network exhaust PLC network stacks, causing communication time-outs and line stops.",
     "actor": "TA-1, TA-5", "path": "Any device on OT/Control network -> flood / scan",
     "existing": "None; no storm control, flat network",
     "L": 3, "I": 4, "controls": ["SC-03", "SC-17", "SC-10"], "rL": 2, "rI": 4},
    {"id": "T-06", "title": "Malware gains admin rights on engineering workstation", "stride": "E",
     "assets": ["A-11"], "flows": ["DF-03", "DF-11"],
     "desc": "Engineers are local administrators on an unpatched Windows EWS; malware arriving via RDP session, USB or TeamViewer obtains full control of the PLC programming environment.",
     "actor": "TA-1, TA-3", "path": "RDP / USB / TeamViewer -> EWS local admin -> PLC tooling",
     "existing": "Signature AV with outdated definitions",
     "L": 3, "I": 5, "controls": ["SC-06", "SC-04", "SC-13"], "rL": 2, "rI": 5},
    {"id": "T-07", "title": "Jump server used as pivot into OT", "stride": "E",
     "assets": ["A-08"], "flows": ["DF-10", "DF-11", "DF-12"],
     "desc": "The jump server is joined to the corporate domain and accepts RDP from the IT admin subnet; compromised IT admin credentials give an attacker a direct route into OT.",
     "actor": "TA-1, TA-3", "path": "Corporate admin credentials -> jump server -> EWS / SCADA",
     "existing": "Single-factor RDP; no session recording",
     "L": 3, "I": 5, "controls": ["SC-05", "SC-02", "SC-04"], "rL": 1, "rI": 5},
    {"id": "T-08", "title": "Corporate AD compromise grants OT access", "stride": "S",
     "assets": ["A-03", "A-10", "A-11", "A-12"], "flows": ["DF-13"],
     "desc": "OT servers and workstations are joined to apex.local. Stolen or forged domain credentials (pass-the-hash, Kerberoasting, golden ticket) authenticate to every OT Windows host.",
     "actor": "TA-1, TA-3", "path": "Phished user -> AD privilege escalation -> Kerberos/SMB to OT hosts",
     "existing": "14 Domain Admin accounts incl. 3 service accounts; no tiering",
     "L": 4, "I": 5, "controls": ["SC-02", "SC-04"], "rL": 1, "rI": 5},
    {"id": "T-09", "title": "Phishing email establishes enterprise foothold", "stride": "S",
     "assets": ["A-02", "A-05"], "flows": ["DF-18"],
     "desc": "A spoofed supplier or OEM email delivers a malicious attachment or credential-harvesting link to an office user.",
     "actor": "TA-1, TA-2", "path": "Email -> user execution -> workstation",
     "existing": "Cloud email filtering; annual awareness training",
     "L": 5, "I": 3, "controls": ["SC-12"], "rL": 3, "rI": 3},
    {"id": "T-10", "title": "Permissive IT/OT firewall rules bypass IDMZ", "stride": "E",
     "assets": ["A-06"], "flows": ["DF-12", "DF-13"],
     "desc": "A 'temporary' any-any rule and direct RDP/SMB from the IT admin subnet let an attacker on the corporate LAN reach OT hosts without passing through the IDMZ.",
     "actor": "TA-1, TA-3", "path": "Corporate LAN -> IT/OT firewall -> OT hosts",
     "existing": "Firewall exists but rule base not reviewed since 2023",
     "L": 4, "I": 5, "controls": ["SC-02"], "rL": 1, "rI": 5},
    {"id": "T-11", "title": "IIoT gateway LTE link bypasses IDMZ", "stride": "E",
     "assets": ["A-19"], "flows": ["DF-14", "DF-16"],
     "desc": "The dual-homed IIoT gateway exposes a web admin interface with default credentials over its LTE link; compromise gives an Internet-to-OT path outside every Apex control.",
     "actor": "TA-7, TA-1", "path": "Internet -> LTE router -> gateway web admin -> OT network",
     "existing": "None owned by Apex; router managed by IIoT supplier",
     "L": 3, "I": 5, "controls": ["SC-11", "SC-13"], "rL": 1, "rI": 5},
    {"id": "T-12", "title": "Production data exposed via cloud platform", "stride": "I",
     "assets": ["A-21"], "flows": ["DF-16"],
     "desc": "Cloud tenant misconfiguration or a compromised (single-factor) cloud console account exposes machine and production data to unauthorized parties.",
     "actor": "TA-1, TA-6", "path": "Cloud console credentials / misconfiguration -> tenant data",
     "existing": "Provider-managed platform; console login password-only",
     "L": 3, "I": 3, "controls": ["SC-16", "SC-04", "SC-11"], "rL": 2, "rI": 3},
    {"id": "T-13", "title": "Malicious firmware/config pushed from cloud", "stride": "T",
     "assets": ["A-19", "A-21"], "flows": ["DF-17"],
     "desc": "A compromised cloud management plane pushes malicious firmware or configuration to the gateway, turning it into an attacker-controlled device inside OT.",
     "actor": "TA-6, TA-3", "path": "Supplier compromise -> device management -> gateway -> OT",
     "existing": "Firmware signing status unknown",
     "L": 2, "I": 5, "controls": ["SC-11", "SC-16"], "rL": 1, "rI": 3},
    {"id": "T-14", "title": "Spoofed wireless sensor readings", "stride": "S",
     "assets": ["A-20", "A-19"], "flows": ["DF-15"],
     "desc": "A rogue transmitter near the plant injects false vibration readings, triggering unnecessary maintenance or masking a real bearing failure.",
     "actor": "TA-7, TA-4", "path": "Physical proximity -> 2.4 GHz -> gateway",
     "existing": "Proprietary pairing; analytics are advisory only",
     "L": 2, "I": 2, "controls": ["SC-11"], "rL": 1, "rI": 2},
    {"id": "T-15", "title": "Unauthenticated Modbus write commands", "stride": "T",
     "assets": ["A-10", "A-14", "A-15", "A-16"], "flows": ["DF-02"],
     "desc": "Modbus/TCP has no authentication; any OT host can write coils and holding registers (start/stop, conveyor speed, robot program select).",
     "actor": "TA-1, TA-3, TA-4", "path": "Any OT host -> Modbus/TCP 502 -> PLC",
     "existing": "None",
     "L": 3, "I": 5, "controls": ["SC-03", "SC-10"], "rL": 1, "rI": 5},
    {"id": "T-16", "title": "Sniffing of cleartext control traffic", "stride": "I",
     "assets": ["A-23"], "flows": ["DF-02", "DF-03", "DF-05"],
     "desc": "Cleartext Modbus and engineering traffic reveal tag maps, logic and process behaviour, giving an attacker the reconnaissance needed for targeted manipulation.",
     "actor": "TA-3", "path": "Foothold on OT network -> passive capture",
     "existing": "None",
     "L": 3, "I": 2, "controls": ["SC-03", "SC-10"], "rL": 2, "rI": 2},
    {"id": "T-17", "title": "Ransomware encrypts SCADA/HMI", "stride": "D",
     "assets": ["A-10", "A-04"], "flows": ["DF-01", "DF-02"],
     "desc": "Ransomware spreading from IT through domain trust and open SMB encrypts SCADA servers and HMIs; operators lose view and the plant stops production.",
     "actor": "TA-1", "path": "Enterprise foothold -> AD -> SMB/RDP into OT -> encryption",
     "existing": "AV on servers; no tested OT recovery plan",
     "L": 4, "I": 5, "controls": ["SC-02", "SC-06", "SC-08", "SC-14"], "rL": 2, "rI": 4},
    {"id": "T-18", "title": "Loss of historian quality records", "stride": "D",
     "assets": ["A-12", "A-07"], "flows": ["DF-06", "DF-07"],
     "desc": "Historian encryption or deletion destroys weld and torque records required for IATF 16949 traceability, breaching OEM contractual obligations.",
     "actor": "TA-1", "path": "Ransomware / destructive malware -> historian",
     "existing": "Nightly backup to a share on the same server",
     "L": 3, "I": 4, "controls": ["SC-08", "SC-02"], "rL": 2, "rI": 3},
    {"id": "T-19", "title": "Tampering with historian quality data", "stride": "T",
     "assets": ["A-12"], "flows": ["DF-06"],
     "desc": "An insider with historian admin rights alters recorded weld/torque values to hide out-of-tolerance parts.",
     "actor": "TA-4", "path": "Historian admin account -> direct DB edit",
     "existing": "Shared historian admin account",
     "L": 2, "I": 4, "controls": ["SC-15", "SC-09"], "rL": 1, "rI": 4},
    {"id": "T-20", "title": "Anonymous access to OPC UA server", "stride": "S",
     "assets": ["A-13"], "flows": ["DF-05", "DF-06", "DF-14"],
     "desc": "OPC UA runs with SecurityMode None and anonymous login; any client can impersonate the historian or gateway, browse the address space and write to writable nodes.",
     "actor": "TA-1, TA-3", "path": "Any OT host / IIoT gateway -> OPC UA 4840",
     "existing": "None",
     "L": 3, "I": 4, "controls": ["SC-15", "SC-03"], "rL": 1, "rI": 4},
    {"id": "T-21", "title": "PLC stopped via mode change or firmware flaw", "stride": "D",
     "assets": ["A-14", "A-15", "A-16"], "flows": ["DF-03"],
     "desc": "An attacker issues a CPU STOP via the engineering protocol, or exploits a published denial-of-service flaw in outdated PLC firmware.",
     "actor": "TA-1, TA-3, TA-7", "path": "OT foothold -> engineering protocol -> PLC",
     "existing": "Firmware not updated since commissioning (2019)",
     "L": 3, "I": 4, "controls": ["SC-07", "SC-03", "SC-13"], "rL": 1, "rI": 4},
    {"id": "T-22", "title": "Covert weld-parameter manipulation (quality escape)", "stride": "T",
     "assets": ["A-15"], "flows": ["DF-03", "DF-02"],
     "desc": "Subtle changes to weld current or robot timing produce parts that pass visual inspection but fail in service, leading to customer recall and OEM contract loss.",
     "actor": "TA-3, TA-4", "path": "EWS or Modbus access -> PLC-02 parameters",
     "existing": "End-of-line sample testing (1 in 200)",
     "L": 2, "I": 5, "controls": ["SC-07", "SC-03", "SC-10"], "rL": 1, "rI": 5},
    {"id": "T-23", "title": "PLC changes not logged or versioned", "stride": "R",
     "assets": ["A-11", "A-14", "A-15", "A-16"], "flows": ["DF-03"],
     "desc": "No version control or change log exists for PLC programs; it is impossible to tell whether a change was made by the vendor, an engineer or an attacker.",
     "actor": "TA-4, TA-5, TA-6", "path": "Any engineering session",
     "existing": "Paper change request for major changes only",
     "L": 4, "I": 3, "controls": ["SC-07", "SC-09"], "rL": 2, "rI": 3},
    {"id": "T-24", "title": "Unapproved TeamViewer on engineering workstation", "stride": "S",
     "assets": ["A-11", "A-22"], "flows": ["DF-20"],
     "desc": "TeamViewer installed by the vendor with an unattended-access password gives anyone holding that password direct Internet access to the EWS, bypassing VPN, IDMZ and logging.",
     "actor": "TA-6, TA-1", "path": "Internet -> TeamViewer -> EWS",
     "existing": "None - unknown to IT before this assessment",
     "L": 4, "I": 5, "controls": ["SC-01", "SC-06", "SC-02"], "rL": 1, "rI": 5},
    {"id": "T-25", "title": "Remote sessions not recorded", "stride": "R",
     "assets": ["A-08"], "flows": ["DF-10", "DF-11", "DF-12"],
     "desc": "Jump server sessions are neither recorded nor centrally logged, so vendor and IT administrator actions in OT cannot be reconstructed after an incident.",
     "actor": "TA-4, TA-6", "path": "Any jump server session",
     "existing": "Windows Security log, local only",
     "L": 3, "I": 3, "controls": ["SC-05", "SC-09"], "rL": 1, "rI": 3},
    {"id": "T-26", "title": "Exploitation of Internet-facing VPN appliance", "stride": "E",
     "assets": ["A-09"], "flows": ["DF-09"],
     "desc": "Edge VPN appliances are a frequent target of mass exploitation; the gateway firmware is two releases behind, and compromise yields administrative control of the remote-access path.",
     "actor": "TA-1, TA-2, TA-3", "path": "Internet -> VPN portal vulnerability -> appliance admin -> IDMZ",
     "existing": "Patching ad hoc; no exposure restriction",
     "L": 3, "I": 5, "controls": ["SC-13", "SC-01", "SC-10"], "rL": 2, "rI": 5},
    {"id": "T-27", "title": "No usable backup of PLC programs and HMI projects", "stride": "D",
     "assets": ["A-11", "A-14", "A-15", "A-16", "A-10"], "flows": ["DF-03"],
     "desc": "The only copies of PLC and HMI projects live on the EWS; if it is encrypted or logic is altered, rebuilding from vendor archives could take weeks.",
     "actor": "TA-1, TA-5", "path": "Loss of EWS -> no restore source",
     "existing": "Vendor holds an archive from 2022 commissioning update",
     "L": 3, "I": 5, "controls": ["SC-08"], "rL": 1, "rI": 3},
    {"id": "T-28", "title": "Malware introduced via removable media", "stride": "T",
     "assets": ["A-11", "A-10"], "flows": ["DF-19"],
     "desc": "Contractors and engineers move files to the EWS and HMIs on personal USB drives, a well-documented route into air-gapped and segmented control systems.",
     "actor": "TA-5, TA-3", "path": "USB -> EWS/HMI -> OT network",
     "existing": "Policy prohibits personal USB; not technically enforced",
     "L": 3, "I": 4, "controls": ["SC-06", "SC-14"], "rL": 2, "rI": 4},
    {"id": "T-29", "title": "Historian replication used to pivot into OT", "stride": "E",
     "assets": ["A-07", "A-12"], "flows": ["DF-07"],
     "desc": "Bidirectional SQL replication lets a compromised replica in the IDMZ open connections to the OT historian using a privileged SQL login.",
     "actor": "TA-1, TA-3", "path": "Enterprise -> replica (IDMZ) -> SQL 1433 -> OT historian",
     "existing": "SQL authentication with sysadmin replication login",
     "L": 3, "I": 4, "controls": ["SC-02", "SC-04"], "rL": 1, "rI": 4},
    {"id": "T-30", "title": "Rogue device connected in control cabinet", "stride": "T",
     "assets": ["A-23", "A-14", "A-15", "A-16"], "flows": ["DF-02", "DF-03"],
     "desc": "Unlocked control cabinets contain unmanaged switches with free ports; a contractor or insider laptop plugged in gets full Layer-2 access to the PLCs.",
     "actor": "TA-4, TA-5", "path": "Physical access -> cabinet switch -> Control network",
     "existing": "Badge access to production hall only",
     "L": 2, "I": 4, "controls": ["SC-03", "SC-10"], "rL": 2, "rI": 4},
]

STRIDE_NAMES = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation",
    "I": "Information Disclosure", "D": "Denial of Service", "E": "Elevation of Privilege",
}

# --------------------------------------------------------------------------- #
# Attack scenarios (narrative lives in threat-model/attack-scenarios.md)
# --------------------------------------------------------------------------- #
SCENARIOS = [
    {"id": "AS-01", "name": "Compromised vendor remote access -> PLC manipulation",
     "threats": ["T-01", "T-26", "T-24", "T-06", "T-02", "T-21", "T-23", "T-25"]},
    {"id": "AS-02", "name": "Corporate workstation -> AD compromise -> IT/OT pivot",
     "threats": ["T-09", "T-08", "T-10", "T-07", "T-15", "T-16"]},
    {"id": "AS-03", "name": "Compromised engineering workstation -> covert PLC logic change",
     "threats": ["T-28", "T-06", "T-02", "T-22", "T-23", "T-27"]},
    {"id": "AS-04", "name": "IIoT gateway compromise -> OT intrusion",
     "threats": ["T-11", "T-13", "T-20", "T-15", "T-16", "T-05"]},
    {"id": "AS-05", "name": "Ransomware -> historian/HMI outage -> production stop",
     "threats": ["T-09", "T-08", "T-10", "T-29", "T-17", "T-18", "T-27"]},
]

# --------------------------------------------------------------------------- #
# Remediation roadmap
# --------------------------------------------------------------------------- #
ROADMAP = [
    # 0-30 days
    {"id": "R-01", "horizon": "0-30 days", "controls": ["SC-01"], "owner": "IT Security Manager", "effort": "Low",
     "action": "Enforce MFA on the VPN; replace the shared vendor account with named accounts that are disabled by default and enabled per approved ticket."},
    {"id": "R-02", "horizon": "0-30 days", "controls": ["SC-01", "SC-02"], "owner": "OT Engineering Lead", "effort": "Low",
     "action": "Uninstall TeamViewer from the EWS; block known remote-access tools outbound at the IT/OT firewall."},
    {"id": "R-03", "horizon": "0-30 days", "controls": ["SC-13", "SC-01"], "owner": "IT Infrastructure", "effort": "Low",
     "action": "Patch the remote-access gateway; restrict the VPN portal to RoboServ source IPs; subscribe to the appliance vendor's advisories."},
    {"id": "R-04", "horizon": "0-30 days", "controls": ["SC-02"], "owner": "IT Infrastructure", "effort": "Low",
     "action": "Review the IT/OT firewall rule base; remove the any-any rule and direct Enterprise->OT RDP/SMB rules."},
    {"id": "R-05", "horizon": "0-30 days", "controls": ["SC-04"], "owner": "IT Security Manager", "effort": "Low",
     "action": "Review privileged accounts: reduce Domain Admins, remove operator local-admin rights, rotate vendor, service and historian admin passwords."},
    {"id": "R-06", "horizon": "0-30 days", "controls": ["SC-08"], "owner": "OT Engineering Lead", "effort": "Low",
     "action": "Take offline copies of all PLC programs, HMI projects and historian configuration; verify one restore on the test bench."},
    {"id": "R-07", "horizon": "0-30 days", "controls": ["SC-11"], "owner": "OT Engineering Lead", "effort": "Low",
     "action": "Disable the IIoT gateway's inbound web management, change default credentials, and restrict the LTE router to the cloud endpoint only."},
    {"id": "R-08", "horizon": "0-30 days", "controls": ["SC-07"], "owner": "OT Engineering Lead", "effort": "Low",
     "action": "Set PLC key switches to RUN; document the procedure for REMOTE/PROG only during approved change windows."},
    # 30-90 days
    {"id": "R-09", "horizon": "30-90 days", "controls": ["SC-02", "SC-04"], "owner": "IT Infrastructure", "effort": "High",
     "action": "Move OT Windows hosts to a separate OT identity domain (no trust to apex.local); force all IT->OT access through the IDMZ."},
    {"id": "R-10", "horizon": "30-90 days", "controls": ["SC-03", "SC-17"], "owner": "OT Engineering Lead", "effort": "Medium",
     "action": "Install a conduit firewall between Site Operations and Control zones with a protocol allowlist; enable port security and storm control; lock cabinets."},
    {"id": "R-11", "horizon": "30-90 days", "controls": ["SC-05"], "owner": "IT Security Manager", "effort": "Medium",
     "action": "Rebuild the jump server off-domain with MFA, session recording and an approved-target list."},
    {"id": "R-12", "horizon": "30-90 days", "controls": ["SC-06"], "owner": "OT Engineering Lead", "effort": "Medium",
     "action": "Harden the EWS and HMIs: application allowlisting, USB device control, a scanning kiosk, no Internet egress."},
    {"id": "R-13", "horizon": "30-90 days", "controls": ["SC-09", "SC-15"], "owner": "IT Security Manager", "effort": "Medium",
     "action": "Deploy an OT log collector in the IDMZ forwarding to the SIEM; introduce named, role-based HMI accounts."},
    {"id": "R-14", "horizon": "30-90 days", "controls": ["SC-11", "SC-15"], "owner": "OT Engineering Lead", "effort": "Medium",
     "action": "Re-route IIoT data via an IDMZ broker (gateway read-only toward OT); enable OPC UA SignAndEncrypt with user authentication."},
    {"id": "R-15", "horizon": "30-90 days", "controls": ["SC-02", "SC-15"], "owner": "IT Infrastructure", "effort": "Low",
     "action": "Change historian replication to OT-initiated push with a least-privilege login; restrict replica access by role."},
    {"id": "R-16", "horizon": "30-90 days", "controls": ["SC-12"], "owner": "IT Security Manager", "effort": "Medium",
     "action": "Strengthen enterprise phishing defences: DMARC enforcement, attachment sandboxing, EDR on all endpoints, phishing simulations."},
    # 3-12 months
    {"id": "R-17", "horizon": "3-12 months", "controls": ["SC-10", "SC-13"], "owner": "IT Security Manager", "effort": "High",
     "action": "Deploy passive OT network monitoring with asset discovery in Z3/Z4 and integrate alerts with the SOC."},
    {"id": "R-18", "horizon": "3-12 months", "controls": ["SC-07"], "owner": "OT Engineering Lead", "effort": "Medium",
     "action": "Formalise PLC change management: version-controlled projects, approval workflow, scheduled program compare against golden copies."},
    {"id": "R-19", "horizon": "3-12 months", "controls": ["SC-04", "SC-01"], "owner": "IT Security Manager", "effort": "High",
     "action": "Implement PAM for OT and vendor privileged access (vaulting, just-in-time access, approval)."},
    {"id": "R-20", "horizon": "3-12 months", "controls": ["SC-14"], "owner": "Plant Manager", "effort": "Medium",
     "action": "Write OT incident-response playbooks and manual-operation procedures; run a ransomware + PLC-manipulation tabletop exercise."},
    {"id": "R-21", "horizon": "3-12 months", "controls": ["SC-16"], "owner": "Procurement", "effort": "Medium",
     "action": "Add IEC 62443-2-4 aligned security requirements to RoboServ and IIoT/cloud supplier contracts; review annually."},
    {"id": "R-22", "horizon": "3-12 months", "controls": ["SC-13", "SC-08"], "owner": "OT Engineering Lead", "effort": "Medium",
     "action": "Establish OT asset inventory and vulnerability management (incl. PLC firmware plan); schedule quarterly restore tests and an annual reassessment."},
]

# --------------------------------------------------------------------------- #
# Risk methodology helpers
# --------------------------------------------------------------------------- #
LIKELIHOOD_SCALE = [
    (1, "Rare", "Requires nation-state capability and insider access; no known precedent in the sector."),
    (2, "Unlikely", "Requires significant skill plus an existing foothold; strong compensating controls in place."),
    (3, "Possible", "Feasible for a motivated attacker with OT knowledge once inside; controls are partial."),
    (4, "Likely", "Technique is used routinely against similar manufacturers; weak controls; low skill required."),
    (5, "Almost Certain", "Trivial to exploit, directly exposed, or already observed at Apex."),
]

IMPACT_SCALE = [
    (1, "Insignificant", "No production impact; < £10k; no safety or quality effect."),
    (2, "Minor", "< 4 h on one line; £10k-£50k; quality issue caught internally."),
    (3, "Moderate", "4-24 h on one line or < 8 h plant-wide; £50k-£250k; limited disclosure of sensitive data."),
    (4, "Major", "1-3 days plant outage; £250k-£1M; defective parts reach customer or equipment damage."),
    (5, "Severe", "> 3 days outage; > £1M; potential injury, product recall or loss of OEM contract."),
]

THRESHOLDS = [(1, 4, "Low"), (5, 9, "Medium"), (10, 16, "High"), (17, 25, "Critical")]


def rating(score):
    for lo, hi, name in THRESHOLDS:
        if lo <= score <= hi:
            return name
    raise ValueError(score)


def scenario_count(tid):
    return sum(tid in s["threats"] for s in SCENARIOS)


def enriched_threats():
    """Threats with computed score/rating/residual and scenario membership."""
    out = []
    for t in THREATS:
        t = dict(t)
        t["score"] = t["L"] * t["I"]
        t["rating"] = rating(t["score"])
        t["rscore"] = t["rL"] * t["rI"]
        t["rrating"] = rating(t["rscore"])
        t["scenarios"] = [s["id"] for s in SCENARIOS if t["id"] in s["threats"]]
        t["stride_name"] = STRIDE_NAMES[t["stride"]]
        out.append(t)
    return out


def ranked_threats():
    """Documented ranking: score desc, then impact desc, then number of attack
    scenarios the threat participates in desc, then ID."""
    return sorted(enriched_threats(),
                  key=lambda t: (-t["score"], -t["I"], -len(t["scenarios"]), t["id"]))


def top_risks(n=10):
    return ranked_threats()[:n]


def asset_name(aid):
    return next(a["name"] for a in ASSETS if a["id"] == aid)


def control(cid):
    return next(c for c in CONTROLS if c["id"] == cid)


def threats_for_control(cid):
    return [t["id"] for t in THREATS if cid in t["controls"]]


def validate():
    """Referential integrity checks - run by build_all before generating."""
    aids = {a["id"] for a in ASSETS}
    fids = {f["id"] for f in DATA_FLOWS}
    cids = {c["id"] for c in CONTROLS}
    tids = {t["id"] for t in THREATS}
    for t in THREATS:
        assert set(t["assets"]) <= aids, t["id"]
        assert set(t["flows"]) <= fids, t["id"]
        assert set(t["controls"]) <= cids, t["id"]
        assert t["stride"] in STRIDE_NAMES, t["id"]
        assert t["rL"] <= t["L"] and t["rI"] <= t["I"], t["id"]
        for a in t["actor"].split(", "):
            assert a in ACTORS, (t["id"], a)
    for s in SCENARIOS:
        assert set(s["threats"]) <= tids, s["id"]
    for r in ROADMAP:
        assert set(r["controls"]) <= cids, r["id"]
    used = {c for r in ROADMAP for c in r["controls"]}
    assert used == cids, f"controls without roadmap item: {cids - used}"
    for c in cids:
        assert threats_for_control(c), f"{c} mitigates no threat"
    assert 20 <= len(THREATS) <= 30

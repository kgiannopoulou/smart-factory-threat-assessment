"""Assemble the consulting-style PDF report from data.py and the rendered images."""
from collections import Counter
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

import data

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report" / "smart-factory-security-assessment.pdf"
NAVY = colors.HexColor("#1F3A5F")
INK = colors.HexColor("#1f2933")
MUTED = colors.HexColor("#52606d")
LINE = colors.HexColor("#cbd2d9")
ZEBRA = colors.HexColor("#f4f6f8")
RATING_BG = {"Low": "#c6efce", "Medium": "#ffeb9c", "High": "#f8cbad", "Critical": "#ff8b8b"}

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13.5,
                      textColor=INK, spaceAfter=6)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.6, leading=9.6, spaceAfter=0)
SMALLB = ParagraphStyle("smallb", parent=SMALL, fontName="Helvetica-Bold", textColor=colors.white)
H1 = ParagraphStyle("h1", parent=BODY, fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY,
                    spaceBefore=4, spaceAfter=10)
H2 = ParagraphStyle("h2", parent=BODY, fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY,
                    spaceBefore=8, spaceAfter=4)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2)
CAP = ParagraphStyle("cap", parent=BODY, fontSize=8, textColor=MUTED, alignment=TA_LEFT, spaceAfter=10)
CALL = ParagraphStyle("call", parent=BODY, backColor=colors.HexColor("#eef3f9"), borderColor=NAVY,
                      borderWidth=0, borderPadding=7, leftIndent=7, rightIndent=7, spaceBefore=4, spaceAfter=12)


class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2.2 * cm,
                         bottomMargin=2 * cm, title=data.ASSESSMENT["title"], author=data.ASSESSMENT["author"],
                         subject="Fictional case study")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate("cover", [frame], onPage=self.cover),
                               PageTemplate("body", [frame], onPage=self.chrome)])
        self.h1n = 0

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            level = 0 if f.style.name == "h1" else 1
            key = f"k{id(f)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(), key, level=level, closed=level > 0)
            if level == 0 and f.getPlainText() not in ("Document control", "Contents"):
                self.notify("TOCEntry", (level, f.getPlainText(), self.page, key))

    @staticmethod
    def cover(c, d):
        w, h = A4
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, h - 11 * cm, w, 11 * cm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 30)
        c.drawString(2 * cm, h - 5 * cm, "SMART FACTORY")
        c.setFont("Helvetica", 17)
        c.drawString(2 * cm, h - 6.2 * cm, "Cybersecurity Threat & Risk Assessment")
        c.setFont("Helvetica", 11)
        c.drawString(2 * cm, h - 8 * cm, f"Client: {data.ASSESSMENT['client']}  -  {data.COMPANY['site']}")
        c.drawString(2 * cm, h - 8.7 * cm, "STRIDE threat model  |  5x5 risk assessment  |  IEC 62443 / NIST mapping")
        c.setFillColor(INK)
        c.setFont("Helvetica", 10)
        y = 9 * cm
        for k, v in [("Version", data.ASSESSMENT["version"]), ("Date", data.ASSESSMENT["date"]),
                     ("Prepared by", data.ASSESSMENT["author"]), ("Classification", data.ASSESSMENT["classification"])]:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2 * cm, y, k)
            c.setFont("Helvetica", 10)
            c.drawString(5.5 * cm, y, v)
            y -= 0.7 * cm
        c.setFont("Helvetica-Oblique", 8.5)
        c.setFillColor(MUTED)
        c.drawString(2 * cm, 2.5 * cm, "Apex Manufacturing Ltd., RoboServ Automation GmbH and all systems described are fictional.")
        c.drawString(2 * cm, 2.0 * cm, "Prepared as a portfolio work sample; no real organisation was assessed.")
        c.restoreState()

    @staticmethod
    def chrome(c, d):
        w, h = A4
        c.saveState()
        c.setStrokeColor(LINE)
        c.line(2 * cm, h - 1.5 * cm, w - 2 * cm, h - 1.5 * cm)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(MUTED)
        c.drawString(2 * cm, h - 1.3 * cm, "Apex Manufacturing Ltd. - Smart Factory Threat & Risk Assessment")
        c.drawRightString(w - 2 * cm, h - 1.3 * cm, "CONFIDENTIAL - FICTIONAL CASE STUDY")
        c.drawRightString(w - 2 * cm, 1.2 * cm, f"Page {d.page}")
        c.restoreState()


def P(t, st=BODY):
    return Paragraph(t, st)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def tbl(headers, rows, widths, rating_cols=(), font=SMALL, zebra=True):
    body = [[Paragraph(str(h), SMALLB) for h in headers]]
    for r in rows:
        body.append([c if hasattr(c, "wrap") else Paragraph(str(c), font) for c in r])
    t = Table(body, colWidths=[w * cm for w in widths], repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("TOPPADDING", (0, 0), (-1, -1), 3),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4),
             ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if zebra:
        for i in range(2, len(body), 2):
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    for ci in rating_cols:
        for ri, r in enumerate(rows, 1):
            txt = str(r[ci])
            for name, bg in RATING_BG.items():
                if name in txt:
                    style.append(("BACKGROUND", (ci, ri), (ci, ri), colors.HexColor(bg)))
    t.setStyle(TableStyle(style))
    return t


def img(path, max_w=17 * cm, max_h=22 * cm):
    w, h = PILImage.open(path).size
    s = min(max_w / w, max_h / h)
    return Image(str(path), width=w * s, height=h * s)


def section(story, title):
    story.append(P(title, H1))


def build():
    ts = data.enriched_threats()
    top = data.top_risks()
    cc = Counter(t["rating"] for t in ts)
    rc = Counter(t["rrating"] for t in ts)
    order = ["Critical", "High", "Medium", "Low"]
    s = [NextPageTemplate("body"), PageBreak()]

    # Document control + TOC
    s.append(P("Document control", H1))
    s.append(tbl(["Version", "Date", "Author", "Change"],
                 [["0.1", "September 2026", data.ASSESSMENT["author"], "Scope, architecture and asset inventory"],
                  ["0.5", "September 2026", data.ASSESSMENT["author"], "DFD, STRIDE analysis, attack scenarios"],
                  ["1.0", data.ASSESSMENT["date"], data.ASSESSMENT["author"], "Risk scoring, recommendations, roadmap - issued"]],
                 [2, 3.2, 3.6, 8.2]))
    s.append(PageBreak())
    s.append(P("Contents", H1))
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("toc0", parent=BODY, fontSize=10, leading=13)]
    s.append(toc)
    s.append(PageBreak())

    # 1 Executive summary
    section(s, "1. Executive summary")
    s.append(P(f"{data.COMPANY['name']} commissioned a cybersecurity threat and risk assessment of its smart-factory "
               f"environment at Plant 1. The plant produces safety-relevant automotive components for two OEMs and "
               f"ships {data.COMPANY['production_value']}. The assessment modelled the plant's IT, OT, IIoT and "
               "third-party connectivity, identified threats with STRIDE, scored them on a documented 5x5 scale and "
               "produced a prioritised remediation roadmap mapped to IEC 62443 and NIST guidance."))
    s.append(P(f"<b>Overall position.</b> We identified <b>30 threats</b>. With today's controls, <b>{cc['Critical']} are Critical</b> "
               f"and <b>{cc['High']} are High</b>. The plant has a firewall and an industrial DMZ, but four "
               "design decisions undermine them, so a single phished password or a compromised vendor could plausibly reach the PLCs:", CALL))
    s += bullets([
        "OT servers and workstations are <b>joined to the corporate Active Directory</b>. Compromising the domain therefore compromises OT (T-08).",
        "The IT/OT firewall still has a <b>'temporary' any-any rule</b> and direct RDP/SMB from IT (T-10).",
        "<b>Vendor remote access</b> uses one shared, password-only, always-on account, and an <b>unapproved TeamViewer</b> on the engineering workstation bypasses every boundary (T-01, T-24).",
        "The <b>IIoT gateway has its own LTE Internet link</b>, which puts it outside the security architecture (T-11).",
    ])
    s.append(P("Nothing is enforced between the supervisory network and the PLCs, which run unauthenticated "
               "protocols with key switches in REMOTE. Once an attacker is inside OT, changing PLC logic or "
               "parameters needs no further exploit. The only copies of the PLC programs sit on the engineering "
               "workstation, so recovery after ransomware or logic tampering could take weeks."))
    s.append(P("<b>Key recommendations.</b> The first 30 days need configuration changes only: MFA and named, "
               "disabled-by-default vendor accounts; removal of TeamViewer; firewall rule clean-up; offline PLC/HMI "
               "backups; IIoT gateway lock-down; PLC key switches to RUN. Between 30 and 90 days, rebuild the identity "
               "and network boundaries (separate OT domain, control-zone firewall, hardened jump server and engineering "
               "workstation). Over 3-12 months, add OT monitoring, formal PLC change management, PAM, OT incident "
               "response and supplier security requirements."))
    s.append(tbl(["Rating", "Current", "Residual (after roadmap)"],
                 [[k, cc.get(k, 0), rc.get(k, 0)] for k in order], [4, 3, 5], rating_cols=(0,)))
    s.append(Spacer(1, 6))
    s.append(P("Once the roadmap is complete, no risk remains Critical. Three remain High (vendor credentials, "
               "engineering workstation compromise and VPN appliance exploitation), because remote vendor support "
               "and PLC programming capability are business requirements. We recommend that the Plant Manager formally "
               "accepts these with the compensating measures in Section 15."))
    s.append(PageBreak())

    # 2 Scope
    section(s, "2. Scope")
    s.append(P("<b>In scope:</b> Enterprise zone elements that affect OT (Active Directory, IT/OT firewall, email as an "
               "entry vector); the industrial DMZ; OT site operations (SCADA/HMI, engineering workstation, historian, "
               "OPC UA); control network (three PLCs); IIoT sensors, gateway and cloud platform; RoboServ vendor remote access."))
    s.append(P("<b>Out of scope:</b> hardwired safety circuits (assumed independent and non-networked); CNC machine "
               "controllers; physical security beyond control cabinets; the ERP application itself."))
    s.append(P("<b>Method:</b> desk-based review of architecture documentation, firewall rule export and stakeholder "
               "interviews (Plant Manager, OT Engineering Lead, IT Security Manager, RoboServ service lead). "
               "No intrusive testing was performed."))
    s.append(P("<b>Limitations:</b> the environment is fictional. Likelihood ratings are expert judgement informed by "
               "public threat reporting, not statistical frequencies. Results depend on the stated configuration being accurate."))

    # 3 Architecture
    section(s, "3. Factory architecture")
    s.append(P(f"{data.COMPANY['name']} operates {data.COMPANY['shifts']}. Parts flow from CNC machining over "
               "<b>PLC-01 (conveyor)</b> to <b>PLC-02 (robotic welding cell)</b> and <b>PLC-03 (packaging)</b>. "
               "Weld and torque records are kept in the historian for IATF 16949 traceability. Two years ago, "
               "24 wireless vibration sensors and an IIoT gateway were added for cloud-based predictive maintenance. "
               "RoboServ Automation GmbH maintains the PLC programs and robot cell remotely."))
    s.append(tbl(["Zone", "Purdue", "Components"],
                 [[f"{z['id']} {z['name']}", z["purdue"], z["desc"]] for z in data.ZONES], [4.2, 2.3, 10.5]))
    s.append(PageBreak())
    s.append(img(ROOT / "diagrams" / "factory-architecture.png", max_h=23 * cm))
    s.append(P("Figure 1 - As-is architecture. Red dashed lines are findings (unapproved or boundary-bypassing paths).", CAP))
    s.append(PageBreak())

    # 4 Assets
    section(s, "4. Critical assets")
    s.append(P("The full inventory of 23 assets is in Appendix B. The assets below are rated Critical: losing their "
               "integrity or availability directly stops production, affects product quality or exposes the whole OT estate."))
    crit = [a for a in data.ASSETS if a["criticality"] == "Critical"]
    s.append(tbl(["ID", "Asset", "Zone", "Function", "Security concern"],
                 [[a["id"], a["name"], a["zone"], a["function"], a["concern"]] for a in crit], [1.3, 4.2, 1.2, 5.3, 5]))

    # 5 Trust boundaries
    section(s, "5. Trust boundaries")
    s.append(P("Zones and conduits were defined in the spirit of IEC 62443-3-2. Each trust boundary was rated on how "
               "well it is enforced today. Two boundaries, TB-4 (supervisory to PLCs) and TB-6 (OT to IIoT/cloud), are "
               "not enforced at all. Three bypass paths cross several boundaries at once."))
    s.append(tbl(["ID", "Between", "Enforced by", "State", "Observation"],
                 [[t["id"], t["between"], t["enforced_by"], t["state"], t["observation"]] for t in data.TRUST_BOUNDARIES],
                 [1.2, 3.6, 3.3, 2.2, 6.7]))
    s.append(PageBreak())
    s.append(img(ROOT / "diagrams" / "network-zones.png", max_h=21 * cm))
    s.append(P("Figure 2 - Zones, conduits and trust boundaries. SL-T / SL-A are indicative target and achieved security levels.", CAP))
    s.append(PageBreak())

    # 6 DFD
    section(s, "6. Data flow diagram")
    s.append(P("The Level-1 DFD models the plant as external entities, processes, data stores and 20 numbered data flows "
               "(DF-01 to DF-20). Flows that cross a trust boundary were the main focus of the STRIDE analysis. "
               "The full flow table is in Appendix C."))
    s.append(img(ROOT / "diagrams" / "data-flow-diagram.png", max_h=20.5 * cm))
    s.append(P("Figure 3 - Level-1 DFD. Upward flows are drawn as lines with an up-arrow in the label.", CAP))
    s.append(PageBreak())

    # 7 Methodology
    section(s, "7. Threat modelling methodology")
    s += bullets([
        "<b>Model</b> - asset inventory, zones/conduits, DFD with numbered flows.",
        "<b>Identify</b> - STRIDE per element, focusing on trust-boundary crossings.",
        "<b>Chain</b> - combine threats into five attack scenarios mapped to MITRE ATT&amp;CK for ICS.",
        "<b>Score</b> - Likelihood x Impact on documented 5x5 scales (Section 10).",
        "<b>Treat</b> - map controls to IEC 62443-3-3, NIST SP 800-53 (SP 800-82r3 overlay) and NIST CSF 2.0; sequence into a roadmap.",
    ])
    s.append(tbl(["Element type", "S", "T", "R", "I", "D", "E"],
                 [["External entity", "X", "", "X", "", "", ""], ["Process", "X", "X", "X", "X", "X", "X"],
                  ["Data store", "", "X", "(logs)", "X", "X", ""], ["Data flow", "", "X", "", "X", "X", ""]],
                 [5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]))
    s.append(Spacer(1, 8))
    s.append(P("<b>Threat actors considered</b>"))
    s.append(tbl(["ID", "Actor"], [[k, v] for k, v in data.ACTORS.items()], [1.5, 10]))

    # 8 STRIDE
    s.append(PageBreak())
    section(s, "8. STRIDE analysis")
    s.append(P("The analysis produced 30 threats spread across all six STRIDE categories. Tampering, spoofing and "
               "elevation of privilege dominate. This is typical for OT, where integrity and the paths into Level 1 "
               "matter more than confidentiality. Appendix A has the complete register with actors, attack paths, "
               "existing controls and mitigations."))
    s.append(img(ROOT / "risk-assessment" / "stride-distribution.png", max_w=12 * cm, max_h=6 * cm))
    s.append(Spacer(1, 4))
    s.append(tbl(["ID", "Component / flow", "STRIDE", "Threat", "Score"],
                 [[t["id"], ", ".join(t["flows"]), t["stride_name"], t["title"], f"{t['score']} {t['rating']}"] for t in ts],
                 [1.2, 2.8, 3.2, 7.4, 2.4], rating_cols=(4,)))

    # 9 Scenarios
    s.append(PageBreak())
    section(s, "9. Attack scenarios")
    s.append(P("The five scenarios below show how individual threats chain into operational consequences. Each step is "
               "mapped to MITRE ATT&amp;CK for ICS and paired with a detection opportunity and the control that breaks "
               "the chain. The full narratives are in threat-model/attack-scenarios.md."))
    sc_text = {
        "AS-01": ("Initial access broker / ransomware affiliate", "Vendor SSL VPN",
                  "Vendor credentials phished -> VPN login as shared account (T-01) -> jump server -> EWS (T-07, or TeamViewer T-24) -> local admin on EWS (T-06) -> PLC program download / STOP (T-02, T-21) -> no attribution (T-23, T-25).",
                  "Line stop, possible equipment damage", "T0822, T0859, T0886, T0843, T0858, T0813",
                  "SC-01 MFA + disabled-by-default accounts; SC-07 key switch in RUN; SC-10 download alerting"),
        "AS-02": ("Ransomware affiliate or state-sponsored group", "Phishing email",
                  "Phishing foothold (T-09) -> AD privilege escalation (T-08) -> domain credentials valid on OT hosts -> direct RDP/SMB through permissive IT/OT rules (T-10) -> traffic capture (T-16) -> unauthenticated Modbus writes (T-15).",
                  "Unauthorized control of the lines", "T0865, T0859, T0886, T0842, T0855, T0831",
                  "SC-02 separate OT identity domain and deny-by-default IT/OT; SC-03 conduit allowlist"),
        "AS-03": ("State-sponsored group or malicious insider", "USB media / insider",
                  "Infected USB (T-28) -> admin on EWS (T-06) -> modified weld parameters on PLC-02 (T-02, T-22) -> parts pass inspection but fail in service -> change not attributable (T-23) and good program not recoverable (T-27).",
                  "Quality escape, OEM recall, contract loss", "T0847, T0863, T0889, T0836, T0879",
                  "SC-06 USB control + allowlisting; SC-07 golden-copy compare; SC-08 offline backups"),
        "AS-04": ("Opportunistic attacker or compromised IIoT supplier", "IIoT gateway LTE link",
                  "Gateway web admin with default credentials over LTE (T-11), or malicious firmware from cloud (T-13) -> dual-homed gateway gives OT foothold -> anonymous OPC UA (T-20) -> recon (T-16) -> Modbus writes / flooding (T-15, T-05).",
                  "OT foothold outside all IT controls", "T0883, T0812, T0862, T0861, T0855, T0814",
                  "SC-11 route via IDMZ, read-only gateway, signed firmware; SC-15 OPC UA security"),
        "AS-05": ("Ransomware affiliate", "Phishing email",
                  "Phishing -> domain admin (T-09, T-08) -> ransomware deployed to all domain hosts incl. OT (T-10, T-29) -> SCADA/HMI and historian encrypted (T-17, T-18) -> plant stops; no offline PLC/HMI backups (T-27).",
                  "Multi-day plant outage, loss of traceability", "T0859, T0815, T0809, T0826, T0828 (+ Enterprise T1486)",
                  "SC-02 separate OT domain; SC-08 offline backups + restore test; SC-14 OT IR"),
    }
    for sc in data.SCENARIOS:
        actor, entry, path, impact, attack, brk = sc_text[sc["id"]]
        s.append(KeepTogether([
            P(f"{sc['id']} - {sc['name']}", H2),
            tbl(["Field", "Detail"],
                [["Threat actor", actor], ["Entry point", entry], ["Attack path", path], ["Impact", impact],
                 ["STRIDE", ", ".join(sorted({data.STRIDE_NAMES[t['stride']] for t in ts if t['id'] in sc['threats']}))],
                 ["ATT&amp;CK for ICS", attack], ["Breaking controls", brk]],
                [3.2, 13.8], zebra=False),
            Spacer(1, 4)]))

    # 10 Risk assessment
    s.append(PageBreak())
    section(s, "10. Risk assessment")
    s.append(P("Risk = Likelihood x Impact (1-25). Current risk reflects existing controls. Residual risk assumes "
               "the recommended controls are implemented. These scales are the documented methodology of this "
               "assessment, not a universal standard. Impact is rated on the highest applicable dimension."))
    s.append(tbl(["Score", "Likelihood", "Criteria"], [[n, nm, d] for n, nm, d in data.LIKELIHOOD_SCALE], [1.3, 2.7, 13]))
    s.append(Spacer(1, 6))
    s.append(tbl(["Score", "Impact", "Criteria"], [[n, nm, d] for n, nm, d in data.IMPACT_SCALE], [1.3, 2.7, 13]))
    s.append(Spacer(1, 6))
    s.append(tbl(["Range", "Rating", "Expected response"],
                 [["17-25", "Critical", "Senior-management attention; mitigate within 30 days"],
                  ["10-16", "High", "Mitigation plan within 90 days"],
                  ["5-9", "Medium", "Mitigate within 12 months or formally accept"],
                  ["1-4", "Low", "Accept and monitor"]], [2, 2.5, 12.5], rating_cols=(1,)))
    s.append(PageBreak())
    s.append(img(ROOT / "risk-assessment" / "risk-matrix.png", max_h=9.5 * cm))
    s.append(P("Figure 4 - Risk matrix before and after treatment. Numbers in cells are threat IDs.", CAP))

    # 11 Top risks
    section(s, "11. Top risks")
    s.append(P("Ranking rule: score, then impact, then the number of attack scenarios the threat enables (chokepoints first)."))
    s.append(tbl(["#", "ID", "Risk", "Score", "Scenarios", "Controls", "Residual"],
                 [[k, t["id"], t["title"], f"{t['score']} {t['rating']}", ", ".join(t["scenarios"]),
                   ", ".join(t["controls"]), f"{t['rscore']} {t['rrating']}"] for k, t in enumerate(top, 1)],
                 [0.7, 1.2, 5.6, 2.3, 2.4, 2.8, 2.0], rating_cols=(3, 6)))

    # 12 Controls
    s.append(PageBreak())
    section(s, "12. Security control recommendations")
    s.append(P("We recommend 17 controls. Each one is traced to the threats it mitigates. They are grouped by the "
               "principle they serve: fix the boundaries before buying tools, protect the paths to Level 1, "
               "assume breach and recover quickly, and bring third parties inside the security model."))
    s.append(tbl(["ID", "Control", "Description", "Mitigates"],
                 [[c["id"], c["name"], c["desc"], ", ".join(data.threats_for_control(c["id"]))] for c in data.CONTROLS],
                 [1.3, 3.4, 8.8, 3.5]))

    # 13 Mapping
    s.append(PageBreak())
    section(s, "13. IEC 62443 / NIST mapping")
    s.append(P("IEC 62443 references are IEC 62443-3-3 system requirements unless another part is named. NIST "
               "references are SP 800-53 Rev. 5 controls as tailored by the SP 800-82 Rev. 3 OT overlay. CSF references "
               "are NIST Cybersecurity Framework 2.0 categories and subcategories."))
    s.append(tbl(["ID", "Control", "IEC 62443", "NIST SP 800-53", "NIST CSF 2.0"],
                 [[c["id"], c["name"], c["iec"], c["nist"], c["csf"]] for c in data.CONTROLS],
                 [1.3, 4.6, 4.0, 3.9, 3.2]))

    # 14 Roadmap
    s.append(PageBreak())
    section(s, "14. Remediation roadmap")
    s.append(P("Actions are sequenced by risk reduction per unit of effort. Every 0-30 day action is a low-effort "
               "configuration change that directly treats Critical risks."))
    for h, theme in [("0-30 days", "Close the open doors"), ("30-90 days", "Rebuild the boundaries"),
                     ("3-12 months", "Detect, govern, sustain")]:
        s.append(P(f"{h} - {theme}", H2))
        s.append(tbl(["ID", "Action", "Controls", "Owner", "Effort"],
                     [[r["id"], r["action"], ", ".join(r["controls"]), r["owner"], r["effort"]]
                      for r in data.ROADMAP if r["horizon"] == h], [1.2, 9.6, 2.2, 2.8, 1.2]))

    # 15 Residual
    s.append(PageBreak())
    section(s, "15. Residual risk")
    s.append(P(f"After the roadmap, the profile moves from {cc['Critical']} Critical / {cc['High']} High / {cc['Medium']} Medium / "
               f"{cc['Low']} Low to {rc.get('Critical', 0)} Critical / {rc['High']} High / {rc['Medium']} Medium / {rc['Low']} Low. "
               "Most controls lower likelihood. Backups (SC-08) and the IIoT redesign (SC-11) also lower impact, "
               "because they shorten recovery time and remove the gateway's write path into OT."))
    s.append(tbl(["Threat", "Residual", "Why it stays High", "Compensating measures"],
                 [["T-01 Stolen vendor credentials", "2 x 5 = 10 High",
                   "Remote vendor support is a business requirement; MFA can still be phished or approved by mistake.",
                   "Phishing-resistant MFA (FIDO2); session recording; OT IDS alerting on vendor sessions"],
                  ["T-06 EWS privilege escalation", "2 x 5 = 10 High",
                   "The EWS must be able to program PLCs; the capability can be controlled but not removed.",
                   "Allowlisting; golden-copy compare; EWS disconnected when not in use"],
                  ["T-26 VPN appliance exploitation", "2 x 5 = 10 High",
                   "Edge-device zero-days are outside Apex's control.",
                   "14-day patch SLA; exposure limited to vendor IPs; evaluate broker with no inbound listener"]],
                 [3.6, 2.4, 5.5, 5.5], rating_cols=(1,)))
    s.append(Spacer(1, 6))
    s.append(P("We recommend that the Plant Manager formally accepts these three residual risks, that they are reviewed "
               "at least annually, and that the assessment is repeated after the 30-90 day boundary changes are in place."))

    # 16 Conclusion
    section(s, "16. Conclusion")
    s.append(P("Apex's exposure comes from <b>how trust is connected</b> far more than from missing security products. "
               "A shared identity domain, a firewall rule base that has drifted, unmanaged vendor and IIoT connectivity, "
               "and a flat control network mean that ordinary IT compromises can turn into production and quality "
               "incidents. Fixing those boundaries is cheap compared with the £180k-per-day cost of an outage, and most "
               "of the first wave needs no capital spend. With monitoring, change management and tested recovery in "
               "place, the plant can keep expanding its smart-factory capabilities without taking on unmanaged risk."))

    # Appendices
    s.append(PageBreak())
    section(s, "Appendix A - STRIDE threat register")
    s.append(tbl(["ID", "Threat / description", "STRIDE / flow", "Actor", "Existing controls", "L x I", "Mitigation", "Res."],
                 [[t["id"], Paragraph(f"<b>{t['title']}</b><br/>{t['desc']}", SMALL),
                   f"{t['stride']} / {', '.join(t['flows'])}", t["actor"], t["existing"],
                   f"{t['L']}x{t['I']}={t['score']} {t['rating']}", ", ".join(t["controls"]),
                   f"{t['rL']}x{t['rI']}={t['rscore']} {t['rrating']}"] for t in ts],
                 [1.0, 5.4, 1.7, 1.4, 2.6, 1.6, 1.6, 1.7], rating_cols=(5, 7)))
    s.append(PageBreak())
    section(s, "Appendix B - Asset inventory")
    s.append(tbl(["ID", "Asset", "Zone", "Purdue", "Criticality", "Security concern"],
                 [[a["id"], a["name"], a["zone"], a["purdue"], a["criticality"], a["concern"]] for a in data.ASSETS],
                 [1.2, 5, 1.2, 1.4, 2, 6.2]))
    s.append(PageBreak())
    section(s, "Appendix C - Data flows")
    s.append(tbl(["ID", "Source", "Destination", "Protocol", "Boundary", "Threats"],
                 [[f["id"], f["src"], f["dst"], f["proto"], f["tb"],
                   ", ".join(t["id"] for t in data.THREATS if f["id"] in t["flows"]) or "-"] for f in data.DATA_FLOWS],
                 [1.3, 3, 3, 4, 2.7, 3]))

    OUT.parent.mkdir(exist_ok=True)
    doc = Doc(OUT)
    doc.multiBuild(s)
    print("wrote", OUT.relative_to(ROOT), f"({doc.page} pages)")


if __name__ == "__main__":
    data.validate()
    build()

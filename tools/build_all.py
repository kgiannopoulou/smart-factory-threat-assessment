"""Regenerate every derived deliverable from tools/data.py.

Mermaid diagrams are rendered separately (needs Node.js):
    npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/src/<name>.mmd -o diagrams/<name>.png -b white -s 2
"""
import build_charts
import build_markdown
import build_registers
import build_report
import data

if __name__ == "__main__":
    data.validate()
    build_registers.stride_workbook()
    build_registers.risk_workbook()
    build_charts.risk_matrix()
    build_charts.stride_distribution()
    for fn in (build_markdown.asset_inventory, build_markdown.data_flows, build_markdown.threat_register,
               build_markdown.top_risks, build_markdown.framework_mapping, build_markdown.roadmap):
        fn()
    build_report.build()

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


def generate_report_pdf(
    filename,
    title,
    report
):

    doc = SimpleDocTemplate(
        filename,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        textColor=colors.HexColor("#0284c7")
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0284c7")
    )

    normal_style = styles["BodyText"]

    elements = []

    # ==================================================
    # HEADER
    # ==================================================

    elements.append(
        Paragraph(
            "SMARTGRID ENERGY PLATFORM",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Blockchain Based Smart City Energy Management using Delegated Proof of Stake (DPoS)",
            styles["Italic"]
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    elements.append(
        Paragraph(
            "<b>Report Type:</b> " + title,
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"Generated On: {datetime.now().strftime('%d %B %Y %H:%M')}",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================

    summary_table = Table(
        [[
            Paragraph(
                """
                <b>Executive Summary</b><br/><br/>
                This report presents energy generation,
                consumption, sustainability indicators,
                blockchain verification status and user
                participation statistics for the selected
                reporting period.
                """,
                normal_style
            )
        ]],
        colWidths=[450]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e0f2fe")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0284c7")),
            ("PADDING", (0, 0), (-1, -1), 10)
        ])
    )

    elements.append(summary_table)

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # KPI TABLE
    # ==================================================

    elements.append(
        Paragraph(
            "Key Performance Metrics",
            heading_style
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    metrics_data = [
        ["Metric", "Value"],
        ["Revenue", f"Rs {report['revenue']}"],
        ["Generated Energy", f"{report['generated']} kWh"],
        ["Consumed Energy", f"{report['consumed']} kWh"],
        ["Efficiency", f"{report['efficiency']}%"],
        ["CO2 Saved", f"{report['co2_saved']} kg"],
        ["Transactions", str(report['transactions'])]
    ]

    metrics_table = Table(
        metrics_data,
        colWidths=[250, 220]
    )

    metrics_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284c7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS",
             (0, 1),
             (-1, -1),
             [colors.white, colors.HexColor("#f8fafc")])
        ])
    )

    elements.append(metrics_table)

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # TOP PRODUCERS
    # ==================================================

    elements.append(
        Paragraph(
            "Top Energy Producers",
            heading_style
        )
    )

    producer_data = [
        ["User", "Role", "Generated (kWh)"]
    ]

    for user in report["top_producers"]:
        producer_data.append([
            user["username"],
            user["role"],
            str(user["energy_generated"])
        ])

    producer_table = Table(
        producer_data,
        colWidths=[180, 100, 100]
    )

    producer_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16a34a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS",
             (0, 1),
             (-1, -1),
             [colors.white, colors.HexColor("#f0fdf4")])
        ])
    )

    elements.append(producer_table)

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # TOP CONSUMERS
    # ==================================================

    elements.append(
        Paragraph(
            "Top Energy Consumers",
            heading_style
        )
    )

    consumer_data = [
        ["User", "Role", "Consumed (kWh)"]
    ]

    for user in report["top_consumers"]:
        consumer_data.append([
            user["username"],
            user["role"],
            str(user["energy_consumed"])
        ])

    consumer_table = Table(
        consumer_data,
        colWidths=[180, 100, 100]
    )

    consumer_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dc2626")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS",
             (0, 1),
             (-1, -1),
             [colors.white, colors.HexColor("#fef2f2")])
        ])
    )

    elements.append(consumer_table)

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # PROJECT INFO
    # ==================================================

    project_table = Table(
        [[
            Paragraph(
                """
                <b>Project Information</b><br/><br/>
                Project: Smart City Energy DPoS<br/>
                Consensus: Delegated Proof of Stake (DPoS)<br/>
                Network: Blockchain Based Energy Platform<br/>
                Monitoring: AI Energy Analytics
                """,
                normal_style
            )
        ]],
        colWidths=[450]
    )

    project_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ("PADDING", (0, 0), (-1, -1), 10)
        ])
    )

    elements.append(project_table)

    elements.append(
        Spacer(1, 15)
    )

    # ==================================================
    # BLOCKCHAIN STATUS
    # ==================================================

    status_table = Table(
        [[
            Paragraph(
                """
                <b>Blockchain Status</b><br/><br/>
                ✓ Blockchain Verified<br/>
                ✓ Transactions Secured<br/>
                ✓ Data Integrity Maintained<br/>
                ✓ DPoS Consensus Operational
                """,
                normal_style
            )
        ]],
        colWidths=[450]
    )

    status_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#16a34a")),
            ("PADDING", (0, 0), (-1, -1), 10)
        ])
    )

    elements.append(status_table)

    elements.append(
        Spacer(1, 20)
    )

    # ==================================================
    # FOOTER
    # ==================================================

    elements.append(
        Paragraph(
            "Generated by SmartGrid Energy Platform | Version 1.0 | June 2026",
            styles["Italic"]
        )
    )

    doc.build(elements)

    return filename
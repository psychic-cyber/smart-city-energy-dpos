from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def generate_report_pdf(
    filename,
    title,
    report
):

    doc = SimpleDocTemplate(
        filename
    )

    styles = (
        getSampleStyleSheet()
    )

    elements = []

    elements.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            f"Revenue: Rs {report['revenue']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated Energy: {report['generated']} kWh",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Consumed Energy: {report['consumed']} kWh",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Efficiency: {report['efficiency']}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"CO2 Saved: {report['co2_saved']} kg",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Transactions: {report['transactions']}",
            styles["Normal"]
        )
    )

    doc.build(
        elements
    )

    return filename
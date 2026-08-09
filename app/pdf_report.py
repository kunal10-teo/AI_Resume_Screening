from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def create_report(
        name,
        role,
        score,
        experience,
        matched,
        missing,
        status
):

    file_name = f"{name}_Resume_Report.pdf"


    doc = SimpleDocTemplate(
        file_name,
        pagesize=letter
    )


    styles = getSampleStyleSheet()

    content = []


    content.append(
        Paragraph(
            "AI Resume Screening Report",
            styles["Title"]
        )
    )


    content.append(Spacer(1,20))


    details = f"""

    Candidate Name: {name}<br/>

    Predicted Role: {role}<br/>

    ATS Score: {score}%<br/>

    Experience: {experience} Years<br/>

    Final Decision: {status}<br/>

    """


    content.append(
        Paragraph(
            details,
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1,20)
    )


    content.append(
        Paragraph(
            "Matched Skills",
            styles["Heading2"]
        )
    )


    content.append(
        Paragraph(
            ", ".join(matched),
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1,20)
    )


    content.append(
        Paragraph(
            "Missing Skills",
            styles["Heading2"]
        )
    )


    content.append(
        Paragraph(
            ", ".join(missing),
            styles["Normal"]
        )
    )


    doc.build(content)


    return file_name
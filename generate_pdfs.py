import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas

# Custom Canvas for Page Numbers and Running Headers/Footers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#800020")) # Royal Maroon for GLS University

        # Top Header (Only on page 2 and onwards)
        if self._pageNumber > 1:
            self.drawString(54, 752, "GLS UNIVERSITY AHMEDABAD - OFFICIAL ACADEMIC & ADMINISTRATIVE RECORDS")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 752, "AY 2026-2027")
            self.setStrokeColor(HexColor("#CBD5E0"))
            self.setLineWidth(0.75)
            self.line(54, 744, 558, 744)

        # Bottom Footer (On all pages)
        self.setStrokeColor(HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 50, 558, 50)

        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#718096"))
        self.drawString(54, 36, "GLS University Campus | Opp. Law Garden, Ellisbridge, Ahmedabad - 380006 | www.glsuniversity.ac.in")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)

        self.restoreState()

def create_styles():
    styles = getSampleStyleSheet()

    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    styles['Normal'].textColor = HexColor("#2D3748")

    doc_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=HexColor("#800020"), # GLS Maroon
        alignment=TA_LEFT,
        spaceAfter=4
    )

    doc_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=HexColor("#1A365D"),
        alignment=TA_LEFT,
        spaceAfter=15
    )

    h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=HexColor("#800020"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=HexColor("#2C7A7B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=HexColor("#2D3748"),
        alignment=TA_LEFT,
        spaceAfter=6
    )

    bullet = ParagraphStyle(
        'CustomBullet',
        parent=body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    faq_q = ParagraphStyle(
        'FAQQuestion',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=HexColor("#800020"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    faq_a = ParagraphStyle(
        'FAQAnswer',
        parent=body,
        leftIndent=10,
        spaceAfter=8
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=HexColor("#2D3748")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=HexColor("#FFFFFF")
    )

    meta_box = ParagraphStyle(
        'MetaBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=HexColor("#4A5568")
    )

    return {
        'doc_title': doc_title,
        'doc_subtitle': doc_subtitle,
        'h1': h1,
        'h2': h2,
        'body': body,
        'bullet': bullet,
        'faq_q': faq_q,
        'faq_a': faq_a,
        'table_cell': table_cell,
        'table_header': table_header,
        'meta_box': meta_box
    }

def get_meta_table(styles, doc_code, effective_date, target_audience):
    data = [
        [
            Paragraph(f"<b>Document Code:</b> {doc_code}", styles['meta_box']),
            Paragraph(f"<b>Effective Date:</b> {effective_date}", styles['meta_box']),
            Paragraph(f"<b>Target Audience:</b> {target_audience}", styles['meta_box'])
        ]
    ]
    t = Table(data, colWidths=[160, 160, 184])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F7FAFC")),
        ('BORDER', (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

# ----------------------------------------------------------------------
# 1. COLLEGE HANDBOOK GENERATOR (GLS UNIVERSITY)
# ----------------------------------------------------------------------
def generate_college_handbook(output_path, styles):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )
    story = []

    story.append(Paragraph("GLS University, Ahmedabad", styles['doc_title']))
    story.append(Paragraph("Official Student & Academic Policy Handbook (Academic Year 2026-2027)", styles['doc_subtitle']))
    story.append(get_meta_table(styles, "GLSU-HB-2026-V1", "August 10, 2026", "Students, Faculty, Parents, Staff"))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#800020"), spaceAfter=12))

    story.append(Paragraph("1. About GLS University & Governance", styles['h1']))
    story.append(Paragraph(
        "GLS University, established under the Gujarat Private Universities Act, is sponsored by the Gujarat Law Society (GLS), a premier educational trust founded in 1927 by legendary visionaries Sardar Vallabhbhai Patel, Shri G.V. Mavlankar, and Seth Chaubildas. Located in the heart of Ahmedabad at Law Garden, GLS University manages over 25 institutes delivering quality education to more than 25,000 students across Computer Applications, IT, Management, Commerce, Design, Law, and Performing Arts.",
        styles['body']
    ))
    story.append(Paragraph("<b>1.1 Vision and Mission</b>", styles['h2']))
    story.append(Paragraph(
        "<b>Mission:</b> To impart industry-relevant, research-backed higher education that fosters innovation, ethical leadership, and global employability.",
        styles['body']
    ))
    story.append(Paragraph(
        "<b>Vision:</b> To emerge as a premier global institution recognized for academic rigor, state-of-the-art technological infrastructure, and holistic student development.",
        styles['body']
    ))
    story.append(Paragraph("<b>1.2 Institutional Leadership Directory</b>", styles['h2']))
    story.append(Paragraph("- <b>President / President Emeritus:</b> Shri Sudhir Nanavati, Senior Advocate", styles['bullet']))
    story.append(Paragraph("- <b>Provost / Vice-Chancellor:</b> Dr. Hitesh Ruparel, Ph.D.", styles['bullet']))
    story.append(Paragraph("- <b>Registrar:</b> Dr. Bimal Solanki (Contact: registrar@glsuniversity.ac.in | Phone: 079-26440525)", styles['bullet']))
    story.append(Paragraph("- <b>Dean of Student Affairs:</b> Dr. Avani Desai (Contact: studentaffairs@glsuniversity.ac.in)", styles['bullet']))
    story.append(Paragraph("- <b>Head of Placement & Corporate Relations:</b> Prof. Rajesh Shah (Contact: placement@glsuniversity.ac.in)", styles['bullet']))

    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Academic Regulations & Evaluation Framework", styles['h1']))
    story.append(Paragraph(
        "GLS University operates on a Choice Based Credit System (CBCS) aligned with UGC guidelines. Students are awarded grades based on Continuous Internal Evaluation (CIE) (40% weightage) and End-Semester Examinations (ESE) (60% weightage).",
        styles['body']
    ))

    story.append(Paragraph("<b>2.1 Grading Scale & Cumulative Grade Point Average (CGPA)</b>", styles['h2']))
    story.append(Paragraph("Performance is evaluated on a 10-point grading scale as detailed below:", styles['body']))

    gpa_data = [
        [Paragraph("<b>Letter Grade</b>", styles['table_header']), Paragraph("<b>Marks Range</b>", styles['table_header']), Paragraph("<b>Grade Points (10-Point Scale)</b>", styles['table_header']), Paragraph("<b>Performance Qualitative Description</b>", styles['table_header'])],
        [Paragraph("O", styles['table_cell']), Paragraph("85% - 100%", styles['table_cell']), Paragraph("10.0", styles['table_cell']), Paragraph("Outstanding Performance", styles['table_cell'])],
        [Paragraph("A+", styles['table_cell']), Paragraph("75% - 84.9%", styles['table_cell']), Paragraph("9.0", styles['table_cell']), Paragraph("Excellent Mastery", styles['table_cell'])],
        [Paragraph("A", styles['table_cell']), Paragraph("65% - 74.9%", styles['table_cell']), Paragraph("8.0", styles['table_cell']), Paragraph("Very Good", styles['table_cell'])],
        [Paragraph("B+", styles['table_cell']), Paragraph("55% - 64.9%", styles['table_cell']), Paragraph("7.0", styles['table_cell']), Paragraph("Good", styles['table_cell'])],
        [Paragraph("B", styles['table_cell']), Paragraph("50% - 54.9%", styles['table_cell']), Paragraph("6.0", styles['table_cell']), Paragraph("Above Average", styles['table_cell'])],
        [Paragraph("C", styles['table_cell']), Paragraph("45% - 49.9%", styles['table_cell']), Paragraph("5.0", styles['table_cell']), Paragraph("Average Pass", styles['table_cell'])],
        [Paragraph("P", styles['table_cell']), Paragraph("40% - 44.9%", styles['table_cell']), Paragraph("4.0", styles['table_cell']), Paragraph("Minimum Pass Threshold", styles['table_cell'])],
        [Paragraph("F", styles['table_cell']), Paragraph("Below 40.0%", styles['table_cell']), Paragraph("0.0", styles['table_cell']), Paragraph("Fail / Re-examination Required", styles['table_cell'])],
    ]
    t_gpa = Table(gpa_data, colWidths=[65, 120, 130, 189])
    t_gpa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#800020")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F7FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_gpa)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>2.2 Mandatory Attendance Rule (75% Rule)</b>", styles['h2']))
    story.append(Paragraph(
        "Attending lectures, practical labs, and tutorials is mandatory. Students must maintain a minimum of <b>75% attendance</b> in each course per semester to be eligible for End-Semester Examinations. Students with attendance between 60% and 74% due to verified medical illness or participation in university-sponsored sports/cultural events may apply for a condonation of attendance through the Dean's office with supporting medical certificates. Students below 60% attendance will be detained and required to re-register for the course.",
        styles['body']
    ))

    story.append(Paragraph("<b>2.3 Academic Integrity & Discipline Policy</b>", styles['h2']))
    story.append(Paragraph(
        "GLS University maintains strict anti-ragging and zero-tolerance policies for academic dishonesty. Plagiarism in project reports, assignments, or thesis papers exceeding 15% similarity index (via Turnitin/iThenticate) will result in rejection of the submission. Possessing unauthorized materials or mobile phones in examination halls incurs an automatic zero and disciplinary committee hearing.",
        styles['body']
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Campus Amenities, Security, and Student Support", styles['h1']))
    story.append(Paragraph("- <b>Central Library & Digital Resource Center:</b> Over 80,000 volumes, IEEE/ACM digital access, open 8:00 AM to 8:00 PM Monday through Saturday.", styles['bullet']))
    story.append(Paragraph("- <b>Incubation & Entrepreneurship Cell (GLS i-Hub):</b> Provides seed funding up to INR 5,00,000 for verified student startup ideas.", styles['bullet']))
    story.append(Paragraph("- <b>Anti-Ragging Helpline:</b> Toll-Free 1800-180-5522 | GLS Security Helpline: 079-26440525 (Ext 109).", styles['bullet']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated: {output_path}")

# ----------------------------------------------------------------------
# 2. PROGRAMS OVERVIEW GENERATOR (GLS UNIVERSITY)
# ----------------------------------------------------------------------
def generate_programs_overview(output_path, styles):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )
    story = []

    story.append(Paragraph("GLS University, Ahmedabad", styles['doc_title']))
    story.append(Paragraph("Academic Programs & Detailed Course Structure Guide (2026-2027)", styles['doc_subtitle']))
    story.append(get_meta_table(styles, "GLSU-PRG-2026-V2", "July 15, 2026", "Students, Academic Counselors, Industry Partners"))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#800020"), spaceAfter=12))

    story.append(Paragraph("1. Faculty of Computer Applications & Information Technology (FCAIT)", styles['h1']))
    story.append(Paragraph(
        "FCAIT is GLS University's flagship IT faculty, renowned for cutting-edge labs in Cloud Computing, AI/ML, Software Engineering, and Cybersecurity.",
        styles['body']
    ))

    story.append(Paragraph("<b>1.1 Integrated M.Sc. (Information Technology) - 5 Years Dual Degree</b>", styles['h2']))
    story.append(Paragraph("- <b>Duration:</b> 5 Years (10 Semesters) | <b>Total Credits:</b> 220 Credits | <b>Exit Option:</b> B.Sc. IT after 3 years (132 Credits)", styles['body']))
    story.append(Paragraph("- <b>Key Courses & Code Structure:</b>", styles['body']))
    story.append(Paragraph("  * <b>IT 101:</b> Fundamentals of Programming & C Language (4 Credits)", styles['bullet']))
    story.append(Paragraph("  * <b>IT 203:</b> Object-Oriented Programming with Java (4 Credits)", styles['bullet']))
    story.append(Paragraph("  * <b>IT 305:</b> Data Structures and Algorithms (4 Credits) [Prerequisite: IT 101]", styles['bullet']))
    story.append(Paragraph("  * <b>IT 402:</b> Full-Stack Web Development (MERN/MEAN) (4 Credits)", styles['bullet']))
    story.append(Paragraph("  * <b>IT 501:</b> Python for Machine Learning & Data Science (4 Credits)", styles['bullet']))
    story.append(Paragraph("  * <b>IT 804:</b> Cloud Computing Infrastructure & DevOps (4 Credits)", styles['bullet']))
    story.append(Paragraph("  * <b>IT 1001:</b> Full-Semester Industry Internship & Capstone Project (18 Credits)", styles['bullet']))

    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.2 Bachelor of Computer Applications (B.C.A.)</b>", styles['h2']))
    story.append(Paragraph("- <b>Duration:</b> 3 Years (6 Semesters) or 4-Year Honours | <b>Total Credits:</b> 132 / 176 Credits", styles['body']))
    story.append(Paragraph("- <b>Core Highlights:</b> Database Management Systems (SQL/NoSQL), Mobile App Development (Flutter/Android), Cyber Security Basics, Software Engineering.", styles['body']))

    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.3 Master of Computer Applications (M.C.A.)</b>", styles['h2']))
    story.append(Paragraph("- <b>Duration:</b> 2 Years (4 Semesters) | <b>Total Credits:</b> 88 Credits | <b>Eligibility:</b> BCA / B.Sc. CS / IT with min 50% aggregate", styles['body']))
    story.append(Paragraph("- <b>Advanced Electives:</b> Deep Learning, Blockchain Architecture, Natural Language Processing, Big Data Analytics with Apache Spark.", styles['body']))

    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Faculty of Management Studies (FMS)", styles['h1']))
    story.append(Paragraph("<b>2.1 Master of Business Administration (M.B.A.)</b>", styles['h2']))
    story.append(Paragraph("- <b>Duration:</b> 2 Years (4 Semesters) | <b>Total Credits:</b> 96 Credits | <b>Approved by:</b> AICTE & UGC", styles['body']))
    story.append(Paragraph("- <b>Specializations Offered:</b> Financial Management, Marketing & Digital Media, Human Resource Management, Business Analytics, International Business.", styles['body']))

    story.append(Paragraph("<b>2.2 Bachelor of Business Administration (B.B.A.)</b>", styles['h2']))
    story.append(Paragraph("- <b>Duration:</b> 3 Years (6 Semesters) | <b>Total Credits:</b> 130 Credits | Includes mandatory Summer Internship after Semester 4.", styles['body']))

    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Summary Matrix of GLS University Degree Offerings", styles['h1']))

    prog_table_data = [
        [Paragraph("<b>Degree Program</b>", styles['table_header']), Paragraph("<b>Faculty / Department</b>", styles['table_header']), Paragraph("<b>Duration</b>", styles['table_header']), Paragraph("<b>Total Credits</b>", styles['table_header']), Paragraph("<b>Min. Passing CGPA</b>", styles['table_header'])],
        [Paragraph("Integrated M.Sc. (IT)", styles['table_cell']), Paragraph("FCAIT", styles['table_cell']), Paragraph("5 Years", styles['table_cell']), Paragraph("220", styles['table_cell']), Paragraph("4.0 (40%)", styles['table_cell'])],
        [Paragraph("B.C.A.", styles['table_cell']), Paragraph("FCAIT", styles['table_cell']), Paragraph("3 Years", styles['table_cell']), Paragraph("132", styles['table_cell']), Paragraph("4.0 (40%)", styles['table_cell'])],
        [Paragraph("M.C.A.", styles['table_cell']), Paragraph("FCAIT", styles['table_cell']), Paragraph("2 Years", styles['table_cell']), Paragraph("88", styles['table_cell']), Paragraph("5.0 (45%)", styles['table_cell'])],
        [Paragraph("B.B.A. (Honours)", styles['table_cell']), Paragraph("FMS", styles['table_cell']), Paragraph("3 / 4 Years", styles['table_cell']), Paragraph("130 / 172", styles['table_cell']), Paragraph("4.0 (40%)", styles['table_cell'])],
        [Paragraph("M.B.A.", styles['table_cell']), Paragraph("FMS", styles['table_cell']), Paragraph("2 Years", styles['table_cell']), Paragraph("96", styles['table_cell']), Paragraph("5.0 (45%)", styles['table_cell'])],
        [Paragraph("B.Com. (Honours)", styles['table_cell']), Paragraph("Faculty of Commerce", styles['table_cell']), Paragraph("3 Years", styles['table_cell']), Paragraph("128", styles['table_cell']), Paragraph("4.0 (40%)", styles['table_cell'])],
        [Paragraph("B.Des. (Design)", styles['table_cell']), Paragraph("Institute of Design", styles['table_cell']), Paragraph("4 Years", styles['table_cell']), Paragraph("160", styles['table_cell']), Paragraph("4.5 (45%)", styles['table_cell'])],
    ]
    t_prog = Table(prog_table_data, colWidths=[120, 120, 74, 80, 110])
    t_prog.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#800020")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F7FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_prog)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated: {output_path}")

# ----------------------------------------------------------------------
# 3. ADMISSIONS GUIDE GENERATOR (GLS UNIVERSITY)
# ----------------------------------------------------------------------
def generate_admissions_guide(output_path, styles):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )
    story = []

    story.append(Paragraph("GLS University, Ahmedabad", styles['doc_title']))
    story.append(Paragraph("Admissions Policy, Eligibility & Fee Structure Guide (AY 2026-2027)", styles['doc_subtitle']))
    story.append(get_meta_table(styles, "GLSU-ADM-2026-V1", "August 1, 2026", "Prospective Applicants, Parents, Admission Cell"))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#800020"), spaceAfter=12))

    story.append(Paragraph("1. Admission Schedule & Key Application Dates", styles['h1']))
    story.append(Paragraph(
        "Admissions for the academic year 2026-2027 at GLS University are conducted online through the central application portal at <b>admission.glsuniversity.ac.in</b> or via campus counseling counters.",
        styles['body']
    ))

    deadline_data = [
        [Paragraph("<b>Program Stream</b>", styles['table_header']), Paragraph("<b>Application Start Date</b>", styles['table_header']), Paragraph("<b>Application Deadline</b>", styles['table_header']), Paragraph("<b>Merit List / Interview Date</b>", styles['table_header'])],
        [Paragraph("Integrated M.Sc. (IT) / BCA", styles['table_cell']), Paragraph("May 10, 2026", styles['table_cell']), Paragraph("June 30, 2026", styles['table_cell']), Paragraph("July 5, 2026", styles['table_cell'])],
        [Paragraph("M.C.A. (Postgraduate)", styles['table_cell']), Paragraph("June 1, 2026", styles['table_cell']), Paragraph("July 15, 2026", styles['table_cell']), Paragraph("July 20, 2026", styles['table_cell'])],
        [Paragraph("B.B.A. / B.Com.", styles['table_cell']), Paragraph("May 15, 2026", styles['table_cell']), Paragraph("July 5, 2026", styles['table_cell']), Paragraph("July 10, 2026", styles['table_cell'])],
        [Paragraph("M.B.A. (CMAT / GLS MAT)", styles['table_cell']), Paragraph("April 1, 2026", styles['table_cell']), Paragraph("June 25, 2026", styles['table_cell']), Paragraph("July 2-4, 2026 (GD/PI)", styles['table_cell'])],
        [Paragraph("B.Des. (Design Entrance Test)", styles['table_cell']), Paragraph("April 15, 2026", styles['table_cell']), Paragraph("June 20, 2026", styles['table_cell']), Paragraph("June 27, 2026 (DAT Exam)", styles['table_cell'])],
    ]
    t_deadlines = Table(deadline_data, colWidths=[140, 110, 110, 144])
    t_deadlines.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#800020")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F7FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_deadlines)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Eligibility Criteria & Selection Process", styles['h1']))

    story.append(Paragraph("<b>2.1 Undergraduate Eligibility (Integrated M.Sc. IT, BCA, BBA, B.Com)</b>", styles['h2']))
    story.append(Paragraph("- Passed Higher Secondary (10+2 / HSC) Examination from GSEB / CBSE / ICSE / IB board.", styles['bullet']))
    story.append(Paragraph("- Minimum Aggregate Marks: <b>45%</b> (40% for SC/ST/SEBC reserved categories).", styles['bullet']))
    story.append(Paragraph("- For Integrated M.Sc. (IT) & BCA: Must have studied English and either Mathematics / Statistics / Business Mathematics / Computer Science in 10+2.", styles['bullet']))

    story.append(Paragraph("<b>2.2 Postgraduate Eligibility (MCA, MBA)</b>", styles['h2']))
    story.append(Paragraph("- <b>M.C.A.:</b> Recognized Bachelor degree (BCA/B.Sc./B.Com./B.A.) with minimum 50% aggregate marks (45% for reserved category) and Mathematics at 10+2 or Graduation level.", styles['bullet']))
    story.append(Paragraph("- <b>M.B.A.:</b> Recognized Bachelor degree with minimum 50% aggregate. Valid score in CMAT / MAT / CAT or GLS University Entrance Test (GLSMAT) followed by Group Discussion (GD) & Personal Interview (PI).", styles['bullet']))

    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Annual Fee Structure (Academic Year 2026-2027)", styles['h1']))
    story.append(Paragraph("Fees are payable in two equal term installments at the start of each semester.", styles['body']))

    tuition_data = [
        [Paragraph("<b>Degree Program</b>", styles['table_header']), Paragraph("<b>Annual Tuition Fee (INR)</b>", styles['table_header']), Paragraph("<b>Term Installment (INR)</b>", styles['table_header']), Paragraph("<b>Enrollment & Exam Fee (One-Time)</b>", styles['table_header'])],
        [Paragraph("Integrated M.Sc. (IT)", styles['table_cell']), Paragraph("INR 55,000 / year", styles['table_cell']), Paragraph("INR 27,500 / term", styles['table_cell']), Paragraph("INR 3,500", styles['table_cell'])],
        [Paragraph("B.C.A.", styles['table_cell']), Paragraph("INR 48,000 / year", styles['table_cell']), Paragraph("INR 24,000 / term", styles['table_cell']), Paragraph("INR 3,500", styles['table_cell'])],
        [Paragraph("M.C.A.", styles['table_cell']), Paragraph("INR 75,000 / year", styles['table_cell']), Paragraph("INR 37,500 / term", styles['table_cell']), Paragraph("INR 4,000", styles['table_cell'])],
        [Paragraph("B.B.A. (Honours)", styles['table_cell']), Paragraph("INR 52,000 / year", styles['table_cell']), Paragraph("INR 26,000 / term", styles['table_cell']), Paragraph("INR 3,500", styles['table_cell'])],
        [Paragraph("M.B.A.", styles['table_cell']), Paragraph("INR 1,15,000 / year", styles['table_cell']), Paragraph("INR 57,500 / term", styles['table_cell']), Paragraph("INR 5,000", styles['table_cell'])],
        [Paragraph("B.Des. (Design)", styles['table_cell']), Paragraph("INR 1,80,000 / year", styles['table_cell']), Paragraph("INR 90,000 / term", styles['table_cell']), Paragraph("INR 6,000", styles['table_cell'])],
    ]
    t_tuition = Table(tuition_data, colWidths=[140, 120, 120, 124])
    t_tuition.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#800020")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F7FAFC")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_tuition)

    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Scholarships & Financial Assistance Schemes", styles['h1']))
    story.append(Paragraph("- <b>GLS Merit Scholarship:</b> 50% tuition fee waiver for students securing 90%+ aggregate in 10+2 or Graduation.", styles['bullet']))
    story.append(Paragraph("- <b>Digital Gujarat / Post-Matric Government Scholarships:</b> Fully supported for SC/ST/SEBC/EWS candidates.", styles['bullet']))
    story.append(Paragraph("- <b>Single Girl Child & Sports Excellence Quota:</b> 25% waiver on annual tuition fees.", styles['bullet']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated: {output_path}")

# ----------------------------------------------------------------------
# 4. STUDENT FAQ GENERATOR (GLS UNIVERSITY)
# ----------------------------------------------------------------------
def generate_student_faq(output_path, styles):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )
    story = []

    story.append(Paragraph("GLS University, Ahmedabad", styles['doc_title']))
    story.append(Paragraph("Student Knowledge Base & Frequently Asked Questions (FAQ)", styles['doc_subtitle']))
    story.append(get_meta_table(styles, "GLSU-FAQ-2026-V3", "August 20, 2026", "All Students, Parents, General Public"))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#800020"), spaceAfter=12))

    story.append(Paragraph("Section 1: Academics & Examination FAQs", styles['h1']))

    faqs_sec1 = [
        ("Q1: Where is GLS University located?",
         "GLS University is located in the heart of Ahmedabad city, opposite Law Garden, Ellisbridge, Ahmedabad - 380006, Gujarat, India."),

        ("Q2: What is the mandatory attendance percentage required at GLS University?",
         "Students must maintain a minimum of 75% attendance in each registered course to be eligible to appear for the End-Semester Examinations. Attendance below 60% results in detention."),

        ("Q3: What is the grading scale used at GLS University?",
         "GLS University follows a 10-point Cumulative Grade Point Average (CGPA) scale ranging from O (Outstanding - 10 points) down to P (Pass - 4 points) and F (Fail - 0 points)."),

        ("Q4: How do I apply for re-evaluation or re-checking of exam answer sheets?",
         "Re-evaluation applications must be submitted online via the GLS Student Portal within 7 days of result declaration along with a fee of INR 500 per subject."),

        ("Q5: What is the duration and exit option for the Integrated M.Sc. (IT) program?",
         "The Integrated M.Sc. (IT) is a 5-year dual degree program. Students have an exit option after completing 3 years with a B.Sc. (IT) degree.")
    ]

    for q, a in faqs_sec1:
        story.append(Paragraph(f"<b>{q}</b>", styles['faq_q']))
        story.append(Paragraph(a, styles['faq_a']))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Section 2: Admissions & Fees FAQs", styles['h1']))

    faqs_sec2 = [
        ("Q6: What is the annual tuition fee for the Integrated M.Sc. (IT) program?",
         "The annual tuition fee for Integrated M.Sc. (IT) is INR 55,000 per year, payable in two equal term installments of INR 27,500 each."),

        ("Q7: What is the annual tuition fee for the BCA program?",
         "The annual tuition fee for BCA at GLS University is INR 48,000 per year, payable in two term installments of INR 24,000 each."),

        ("Q8: What is the annual tuition fee for the MCA program?",
         "The annual tuition fee for MCA is INR 75,000 per year, payable in two term installments of INR 37,500 each."),

        ("Q9: Does GLS University offer scholarships for meritorious students?",
         "Yes. The GLS Merit Scholarship awards a 50% tuition fee waiver to students scoring 90% or above in their qualifying board/degree examination.")
    ]

    for q, a in faqs_sec2:
        story.append(Paragraph(f"<b>{q}</b>", styles['faq_q']))
        story.append(Paragraph(a, styles['faq_a']))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Section 3: Campus Life, Hostel & Placements FAQs", styles['h1']))

    faqs_sec3 = [
        ("Q10: Does GLS University provide placement assistance for IT and Management students?",
         "Yes. The Central Placement Cell at GLS University organizes placement drives with over 150 corporate recruiters including TCS, Infosys, Wipro, L&T Infotech, Gateway Group, Cybage, and Bank of America. The highest package recorded is INR 12.5 LPA with an average package of INR 4.8 LPA for IT streams."),

        ("Q11: Are hostel facilities available near the Law Garden campus?",
         "GLS University has tie-ups with verified private hostels and PG accommodations located within 1 km of the Law Garden campus, providing AC rooms, Wi-Fi, and meal facilities."),

        ("Q12: What is GLS i-Hub?",
         "GLS i-Hub is the dedicated Startup and Innovation Incubation Center at GLS University that provides seed funding up to INR 5,00,000, co-working space, and mentorship to student entrepreneurs.")
    ]

    for q, a in faqs_sec3:
        story.append(Paragraph(f"<b>{q}</b>", styles['faq_q']))
        story.append(Paragraph(a, styles['faq_a']))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Section 4: Contact & Technical Support FAQs", styles['h1']))

    faqs_sec4 = [
        ("Q13: How do I contact the Registrar office at GLS University?",
         "You can email registrar@glsuniversity.ac.in or call the main helpline at 079-26440525 during working hours (10:00 AM to 5:00 PM, Mon-Sat)."),

        ("Q14: What is the official website of GLS University?",
         "The official website is www.glsuniversity.ac.in and the student portal is portal.glsuniversity.ac.in."),

        ("Q15: What is the campus address of GLS University?",
         "GLS University Campus, Opposite Law Garden, Ellisbridge, Ahmedabad - 380006, Gujarat, India.")
    ]

    for q, a in faqs_sec4:
        story.append(Paragraph(f"<b>{q}</b>", styles['faq_q']))
        story.append(Paragraph(a, styles['faq_a']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated: {output_path}")

# ----------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------
def main():
    target_dir = r"C:\Users\LENOVO\.gemini\antigravity\scratch\gls_university_rag_chatbot\data"
    os.makedirs(target_dir, exist_ok=True)

    styles = create_styles()

    files = {
        "college_handbook.pdf": generate_college_handbook,
        "programs_overview.pdf": generate_programs_overview,
        "admissions_guide.pdf": generate_admissions_guide,
        "student_faq.pdf": generate_student_faq,
    }

    print(f"Generating 4 GLS University PDF database files in: {target_dir}\n")

    for filename, generator_func in files.items():
        file_path = os.path.join(target_dir, filename)
        generator_func(file_path, styles)

    print("\nAll 4 GLS University PDFs generated successfully!")

if __name__ == "__main__":
    main()

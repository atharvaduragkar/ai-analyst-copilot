from fpdf import FPDF
import tempfile
import os
import plotly.io as pio  # Required for saving charts as images

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "AI Analyst Copilot - Exported Report", ln=True, align="C")
        self.ln(10)

    def add_section_title(self, title):
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", '', 11)

    def add_multiline(self, text):
        self.multi_cell(0, 10, text)
        self.ln(3)

def export_to_pdf(query, df, summary=None, chart_fig=None):
    pdf = PDFReport()
    pdf.add_page()

    # Section: User Query
    pdf.add_section_title("User Query")
    pdf.add_multiline(query)

    # Section: Insight Summary
    if summary:
        pdf.add_section_title("Insight Summary")
        pdf.add_multiline(summary)

    # Section: Result Table
    pdf.add_section_title("Result Table (First 20 Rows)")
    headers = df.columns.tolist()
    col_width = pdf.w / len(headers) - 5  # dynamic width
    pdf.set_font("Arial", 'B', 10)
    for header in headers:
        pdf.cell(col_width, 8, str(header), border=1)
    pdf.ln()

    pdf.set_font("Arial", '', 9)
    for _, row in df.head(20).iterrows():
        for item in row:
            pdf.cell(col_width, 8, str(item), border=1)
        pdf.ln()

    # Section: Chart (Optional)
    if chart_fig:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as chart_file:
            chart_fig.write_image(chart_file.name, width=700, height=400)
            pdf.add_section_title("Generated Chart")
            pdf.image(chart_file.name, w=180)
            pdf.ln(10)

    # Save final PDF to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name
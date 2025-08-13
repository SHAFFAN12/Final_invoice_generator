from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any

class LetterTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Request Letter"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Date", "date"),
                ("To", "text"),
                ("Subject", "text")
            ],
            "content": {
                "paragraphs": [
                    "This is regarding the payment adjustment for the campaign.",
                    "Kindly process the request at the earliest."
                ]
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ["Date", "To", "Subject", "content"]
        return all(data.get(field) for field in required)

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, self.template_type.upper(), 0, 1, 'C')
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 10)
        for label, _ in self.get_template()["header_fields"]:
            pdf.cell(35, 8, f"{label}:", 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, data.get(label, ""), 0, 1)
            pdf.set_font("Arial", 'B', 10)
        pdf.ln(5)

        pdf.set_font("Arial", '', 11)
        for para in data.get("content", "").split("\n"):
            pdf.multi_cell(0, 6, para.strip())
            pdf.ln(2)

def get_template_class():
    return LetterTemplate()

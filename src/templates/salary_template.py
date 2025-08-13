from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any, List
from num2words import num2words
import locale

class SalaryTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Salary Slip"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Employee Name", "text"),
                ("Employee No", "text"),
                ("Designation", "text"),
                ("Department", "text"),
                ("CNIC", "text"),
                ("Month", "text")
            ],
            "earnings_inputs": [
                {"name": "Basic Salary", "type": "number"},
                {"name": "House Rent Allowance", "type": "number"},
                {"name": "Dearness Allowance", "type": "number"},
                {"name": "Conveyance Allowance", "type": "number"},
                {"name": "Medical Allowance", "type": "number"},
                {"name": "Special Allowance", "type": "number"},
                {"name": "Bonus", "type": "number"},
                {"name": "Overtime", "type": "number"},
                {"name": "Other Earnings", "type": "number"}
            ],
            "deductions_inputs": [
                {"name": "Provident Fund", "type": "number"},
                {"name": "Professional Tax", "type": "number"},
                {"name": "Income Tax (TDS)", "type": "number"},
                {"name": "ESI Contribution", "type": "number"},
                {"name": "Loan Recovery", "type": "number"},
                {"name": "Advance Recovery", "type": "number"},
                {"name": "Late Attendance", "type": "number"},
                {"name": "Other Deductions", "type": "number"}
            ],
            "line_items": {
                "Earnings": {"columns": ["Particulars", "Amount"]},
                "Deductions": {"columns": ["Particulars", "Amount"]}
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        # Validate header fields
        for field, _ in self.get_template()["header_fields"]:
            if not data.get(field):
                return False

        # Validate earnings and deductions format
        for section in ["Earnings", "Deductions"]:
            items = data.get(section)
            if not isinstance(items, list):
                return False
            for row in items:
                if not isinstance(row, dict) or not all(k in row for k in ["Particulars", "Amount"]):
                    return False
        return True

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 12, self.template_type.upper(), ln=True, align='C')
        pdf.ln(6)

        # Employee Information
        pdf.set_font("Arial", '', 10)
        for field, _ in self.get_template()["header_fields"]:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(40, 8, f"{field}:", 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, str(data.get(field, "")), 0, 1)
        pdf.ln(4)

        # Draw earnings and deductions
        def draw_table(title: str, items: List[Dict[str, str]]) -> float:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, title, ln=True)

            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "Particulars", border=1)
            pdf.cell(60, 8, "Amount (PKR)", border=1, ln=True, align='R')

            pdf.set_font("Arial", '', 10)
            total = 0.0
            for row in items:
                particular = row.get("Particulars", "")
                amount_str = row.get("Amount", "0").replace(",", "")
                try:
                    amount = float(amount_str)
                except:
                    amount = 0.0
                total += amount
                pdf.cell(120, 8, particular, border=1)
                pdf.cell(60, 8, f"{amount:,.2f}", border=1, ln=True, align='R')
            pdf.ln(4)
            return total

        earnings = data.get("Earnings", [])
        deductions = data.get("Deductions", [])

        total_earnings = draw_table("EARNINGS", earnings)
        total_deductions = draw_table("DEDUCTIONS", deductions)

        net_pay = total_earnings - total_deductions

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(120, 10, "NET PAY", border=1, align='R')
        pdf.cell(60, 10, f"{net_pay:,.2f}", border=1, ln=True, align='R')
        pdf.ln(5)

        # Amount in Words
        try:
            words = num2words(net_pay, lang='en_IN').capitalize()
        except:
            words = f"{net_pay:,.2f}"

        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 6, f"Amount in words: {words} rupees only", 0, 'L')


def get_template_class():
    return SalaryTemplate()
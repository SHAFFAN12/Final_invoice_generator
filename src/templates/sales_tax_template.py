from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any
from num2words import num2words
from datetime import datetime
import locale


class SalesTaxTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Sales Tax Invoice"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("M/s.", "text"),
                ("Campaign", "text"),
                ("PO Number", "text"),
                ("NTN", "text"),
                ("STRN", "text"),
                ("Date", "date"),
                ("Invoice No", "text"),
                ("Company NTN", "text"),
                ("Company STN", "text"),
                ("GST Percentage", "number")
            ],
            "line_items": {
                "columns": ["Description", "Size", "Duration", "Start Date", "End Date", "Amount"]
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        fields = [f[0] for f in self.get_template()["header_fields"]]
        if not all(data.get(f) for f in fields):
            return False
        if not isinstance(data.get("line_items"), list):
            return False
        return True

    def generate_pdf_content(self, pdf: FPDF, data: dict) -> None:
        locale.setlocale(locale.LC_ALL, '')

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 12, self.template_type.upper(), ln=True, align='C')
        pdf.ln(5)

        # Parse invoice month from date
        try:
            invoice_date = datetime.strptime(data.get("Date", ""), "%Y-%m-%d")
            invoice_month = invoice_date.strftime("%B %Y")
        except:
            invoice_month = ""

        # Header fields
        left_fields = ["M/s.", "Campaign", "PO Number", "NTN", "STRN"]
        right_fields = [
            ("Date", data.get("Date", "")),
            ("Invoice Month", invoice_month),
            ("Invoice No", data.get("Invoice No", "")),
            ("Company NTN No", data.get("Company NTN", "")),
            ("Company SRB No", data.get("Company STN", ""))
        ]

        box_height = 7
        x_left = pdf.get_x()
        y_start = pdf.get_y()

        # Left box
        for field in left_fields:
            pdf.set_xy(x_left, y_start)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(38, box_height, f"{field}:", border=1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(62, box_height, data.get(field, ""), border=1, ln=1)
            y_start += box_height

        # Right box
        x_right = 110
        y_top = pdf.get_y() - len(left_fields) * box_height
        for label, value in right_fields:
            pdf.set_xy(x_right, y_top)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(38, box_height, f"{label}:", border=1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(42, box_height, value, border=1, ln=1)
            y_top += box_height

        pdf.ln(8)

        # Line items header
        headers = ["Sr", "Description", "Size", "Duration", "Start Date", "End Date", "Amount"]
        widths = [8, 60, 15, 18, 23, 23, 30]

        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        for header, width in zip(headers, widths):
            pdf.cell(width, 8, header, 1, 0, 'C', fill=True)
        pdf.ln()

        # Line item rows
        pdf.set_font("Arial", '', 9)
        subtotal = 0
        for idx, item in enumerate(data.get("line_items", []), 1):
            values = [
                str(idx),
                item.get("Description", ""),
                item.get("Size", ""),
                item.get("Duration", ""),
                item.get("Start Date", ""),
                item.get("End Date", ""),
                f"{float(item.get('Amount', '0').replace(',', '')):,.0f}"
            ]
            for val, width in zip(values, widths):
                align = 'R' if val.replace(',', '').isdigit() else 'L'
                pdf.cell(width, 8, val, 1, 0, align)
            pdf.ln()
            subtotal += float(item.get("Amount", "0").replace(",", ""))

        pdf.ln(5)

        # Totals section (clean layout)
        gst_rate = float(data.get("GST Percentage", 15))
        gst_total = round(subtotal * gst_rate / 100)
        grand_total = subtotal + gst_total

        pdf.set_fill_color(245, 245, 245)
        label_width = 130
        value_width = 40
        row_height = 8

        def total_line(label, value, bold=False):
            pdf.set_font("Arial", 'B', 10 if not bold else 11)
            pdf.cell(label_width, row_height, label, border=1, align='R', fill=True)
            pdf.cell(value_width, row_height, f"Rs. {value:,.0f}/-", border=1, ln=1, align='R')

        total_line("Subtotal", subtotal)
        total_line(f"GST @ {gst_rate:.0f}%", gst_total)
        total_line("Grand Total", grand_total, bold=True)

        pdf.ln(6)

        # Amount in words
        pdf.set_font("Arial", 'I', 9)
        try:
            words = num2words(grand_total, lang='en_IN').capitalize()
        except:
            words = str(grand_total)
        pdf.multi_cell(0, 6, f"Amount in words: {words} Rupees Only/=", border=0)


def get_template_class():
    return SalesTaxTemplate()

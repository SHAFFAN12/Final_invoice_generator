from fpdf import FPDF
from PIL import Image
from pathlib import Path
from typing import Dict, Any, Optional, Type
import locale

from templates.base_template import BaseTemplate
from templates import (
    invoice_template,
    letter_template,
    salary_template,
    sales_tax_template
)

class PDFGenerator:
    """Handles PDF document generation with professional formatting."""

    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.set_left_margin(15)
        self.pdf.set_right_margin(15)
        self._initialize_locale()

    def _initialize_locale(self) -> None:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            self._locale_available = True
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, '')
                self._locale_available = True
            except locale.Error:
                self._locale_available = False

    def format_currency(self, amount: float) -> str:
        try:
            if self._locale_available:
                return locale.currency(amount, grouping=True, symbol=False)
            return "{:,.2f}".format(amount)
        except:
            return str(amount)

    def generate(
        self,
        company: str,
        doc_type: str,
        template: Dict[str, Any],
        letterhead_path: str,
        output_path: str,
        data: Dict[str, Any],
        signature_path: Optional[str] = None,
        stamp_path: Optional[str] = None
    ) -> None:
        self._create_page_with_letterhead(letterhead_path)

        template_class = self._get_template_class(doc_type)
        if template_class:
            template_instance = template_class()
            template_instance.generate_pdf_content(self.pdf, data)  # FIXED

        self._add_signature_stamp(company, signature_path, stamp_path)
        self.pdf.output(output_path)

    def _get_template_class(self, doc_type: str) -> Optional[Type[BaseTemplate]]:
        return {
            "Invoice": invoice_template.InvoiceTemplate,
            "Request Letter": letter_template.LetterTemplate,
            "Salary Slip": salary_template.SalaryTemplate,
            "Sales Tax Invoice": sales_tax_template.SalesTaxTemplate
        }.get(doc_type)

    def _create_page_with_letterhead(self, letterhead_path: str) -> None:
        self.pdf.add_page()

        if letterhead_path and Path(letterhead_path).exists():
            try:
                self.pdf.image(letterhead_path, x=0, y=0, w=210, h=297)  # A4 size in mm
                self.pdf.set_y(60)  # Move below the letterhead header space
            except Exception as e:
                print(f"Error loading letterhead: {e}")
                self.pdf.set_y(50)
        else:
            self.pdf.set_y(50)

    def _add_signature_stamp(
        self,
        company: str,
        signature_path: Optional[str],
        stamp_path: Optional[str]
    ) -> None:
        self.pdf.ln(15)

        if signature_path and Path(signature_path).exists():
            try:
                self.pdf.image(signature_path, x=120, w=60)
                self.pdf.ln(20)
            except Exception as e:
                print(f"Error adding signature: {e}")

        if stamp_path and Path(stamp_path).exists():
            try:
                self.pdf.image(stamp_path, x=140, w=40)
            except Exception as e:
                print(f"Error adding stamp: {e}")

        
        # self.pdf.ln(20)  # Add vertical space before printing the company name
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.cell(0, 10, company.upper(), 0, 1, 'L')

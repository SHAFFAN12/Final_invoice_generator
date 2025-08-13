import os
import importlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from pdf_generator import PDFGenerator


class DocumentManager:
    """Manages document templates and generation process."""
    
    def __init__(self):
        """Initialize with loaded templates."""
        self.templates = self._load_templates()
        self.signature_path: Optional[str] = None
        self.stamp_path: Optional[str] = None

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from the templates directory."""
        templates = {}
        templates_dir = Path(__file__).parent / "templates"

        # Ensure current directory is in Python path
        if str(Path(__file__).parent) not in sys.path:
            sys.path.insert(0, str(Path(__file__).parent))

        for filename in os.listdir(templates_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "base_template.py"):
                try:
                    module_name = f"templates.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    template_class = module.get_template_class()
                    template_data = template_class.get_template()
                    template_data["template_class"] = template_class  # Attach the class instance
                    templates[template_data["type"]] = template_data
                except (ImportError, AttributeError) as e:
                    print(f"Error loading template {filename}: {e}")
        return templates

    def get_letterhead_path(self, company: str) -> Optional[str]:
        """Find the appropriate letterhead image for a company."""
        base_name = company.lower().replace(' ', '_')
        assets_dir = Path(__file__).parent.parent / "assets" / "letterheads"

        for ext in ['.jpg', '.jpeg', '.png']:
            path = assets_dir / f"{base_name}{ext}"
            if path.exists():
                return str(path)
        return None

    def generate_document(
        self,
        company: str,
        doc_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a complete document with the given parameters."""
        template = self.templates.get(doc_type)
        if not template:
            raise ValueError(f"Unknown document type: {doc_type}")
        
        # Validate using the class
        template_class = template.get("template_class")
        if template_class and not template_class.validate_data(data or {}):
            raise ValueError("Invalid data provided for template.")

        letterhead = self.get_letterhead_path(company)
        if not letterhead:
            raise FileNotFoundError(
                f"Letterhead not found for {company}. "
                f"Please add an image to assets/letterheads/ as either: "
                f"{company.lower().replace(' ', '_')}.jpg, .jpeg, or .png"
            )

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "generated_docs"
        output_dir.mkdir(exist_ok=True)
        filename = output_dir / f"{company.replace(' ', '_')}_{doc_type.replace(' ', '_')}_{timestamp}.pdf"

        # Create and configure PDF generator
        pdf_gen = PDFGenerator()
        pdf_gen.generate(
            company=company,
            doc_type=doc_type,
            template=template,
            letterhead_path=letterhead,
            output_path=str(filename),
            data=data or {},
            signature_path=self.signature_path,
            stamp_path=self.stamp_path
        )

        return str(filename.absolute())

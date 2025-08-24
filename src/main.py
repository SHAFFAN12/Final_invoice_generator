import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from document_manager import DocumentManager
from signer import PDFSignatureApp

class DocumentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Generator")

        self.doc_manager = DocumentManager()
        self.entry_widgets = {}
        self.line_item_entries = []
        self.error_labels = {}
        self.earnings_entries = []  # New for salary slip

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('Error.TLabel', foreground='red', font=('Helvetica', 8))

    def _setup_ui(self):
        # Company Selection
        self.company_var = tk.StringVar()
        ttk.Label(self.root, text="Select Company:").pack(anchor='w', padx=10, pady=(10, 0))
        self.company_menu = ttk.Combobox(
            self.root,
            textvariable=self.company_var,
            values=["GoFar Media", "Glory Enterprises"],
            state="readonly"
        )
        self.company_menu.pack(fill=tk.X, padx=10)
        self.company_menu.current(0)

        # Document Type Selection
        self.doc_type_var = tk.StringVar()
        ttk.Label(self.root, text="Document Type:").pack(anchor='w', padx=10, pady=(10, 0))
        self.doc_type_menu = ttk.Combobox(
            self.root,
            textvariable=self.doc_type_var,
            values=list(self.doc_manager.templates.keys()),
            state="readonly"
        )
        self.doc_type_menu.pack(fill=tk.X, padx=10)
        self.doc_type_menu.bind("<<ComboboxSelected>>", lambda e: self.load_form_fields())

        # Scrollable Form Area
        self.canvas = tk.Canvas(self.root)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.generate_button = ttk.Button(self.root, text="Generate Document", command=self.generate_document)
        self.generate_button.pack(pady=10)

    def load_form_fields(self):
        # Clear old widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entry_widgets.clear()
        self.error_labels.clear()
        self.line_item_entries.clear()
        self.earnings_entries.clear()

        doc_type = self.doc_type_var.get()
        template = self.doc_manager.templates.get(doc_type, {})

        # Generate header fields dynamically
        for field, field_type in template.get("header_fields", []):
            self._add_form_field(field, field_type)

        # Special cases
        if doc_type in ["Invoice", "Sales Tax Invoice"]:
            self._add_line_items_section(template)
        elif doc_type == "Request Letter":
            self._add_letter_content_field()
        elif doc_type == "Salary Slip":
            self._add_salary_slip_sections(template)  # Add salary slip sections

    def _add_form_field(self, field: str, field_type: str) -> None:
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=3)

        ttk.Label(frame, text=f"{field}:", width=20, anchor='w').pack(side=tk.LEFT)
        error_label = ttk.Label(frame, text="", style='Error.TLabel')
        error_label.pack(side=tk.RIGHT)
        self.error_labels[field] = error_label

        if field_type == "date":
            entry = DateEntry(frame, date_pattern='yyyy-mm-dd')
        else:
            entry = ttk.Entry(frame)

        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_widgets[field] = entry

    def _add_salary_slip_sections(self, template):
        """Add earnings section only for salary slip"""
        # Earnings section
        ttk.Label(self.scrollable_frame, text="EARNINGS", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        for item in template.get("earnings_inputs", []):
            self._add_salary_item(item, "earnings")

    def _add_salary_item(self, item, section_type):
        """Add individual earning item"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=2)

        name = item["name"]
        field_type = item["type"]

        ttk.Label(frame, text=f"{name}:", width=25, anchor='w').pack(side=tk.LEFT)
        
        if field_type == "number":
            entry = ttk.Entry(frame, width=15)
            entry.insert(0, "0")  # Default value
        else:
            entry = ttk.Entry(frame, width=15)
        
        entry.pack(side=tk.LEFT)
        
        # Only earnings now
        self.earnings_entries.append((name, entry))

    def _add_letter_content_field(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(frame, text="Content:").pack(anchor='w')

        # Frame for text area + scrollbar
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Unlimited text area
        self.content_text = tk.Text(
            text_frame,
            height=20,
            width=90,
            font=("Helvetica", 10),
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.content_text.yview)

    def _add_line_items_section(self, template):
        ttk.Label(self.scrollable_frame, text="Line Items:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        line_item_frame = ttk.Frame(self.scrollable_frame)
        line_item_frame.pack(fill=tk.X)

        columns = template.get("line_items", {}).get("columns", [])
        self.line_item_entries = []

        header_frame = ttk.Frame(line_item_frame)
        header_frame.pack(fill=tk.X)
        for col in columns:
            ttk.Label(header_frame, text=col, font=('Helvetica', 9, 'bold'), width=15).pack(side=tk.LEFT, padx=2)

        self.items_container = ttk.Frame(line_item_frame)
        self.items_container.pack(fill=tk.X, pady=5)

        self._add_line_item_row(template)

        ttk.Button(line_item_frame, text="Add Item", command=lambda: self._add_line_item_row(template)).pack(anchor='w', pady=5)

    def _add_line_item_row(self, template):
        row = ttk.Frame(self.items_container)
        row.pack(fill=tk.X, pady=2)

        entry_list = []
        for col in template["line_items"]["columns"]:
            if "Date" in col:
                entry = DateEntry(row, date_pattern='yyyy-mm-dd')
            else:
                entry = ttk.Entry(row, width=15)
            entry.pack(side=tk.LEFT, padx=2)
            entry_list.append(entry)

        ttk.Button(row, text="×", width=3, command=lambda: self._remove_line_item_row(row, entry_list)).pack(side=tk.LEFT)
        self.line_item_entries.append(entry_list)

    def _remove_line_item_row(self, frame, entry_list):
        frame.destroy()
        self.line_item_entries.remove(entry_list)

    def collect_form_data(self) -> dict:
        doc_type = self.doc_type_var.get()
        template = self.doc_manager.templates.get(doc_type, {})
        data = {}

        # Collect header fields
        for field, _ in template.get("header_fields", []):
            widget = self.entry_widgets[field]
            if isinstance(widget, DateEntry):
                data[field] = widget.get_date().strftime('%Y-%m-%d')
            else:
                data[field] = widget.get().strip()

        # Collect salary slip data in new format
        if doc_type == "Salary Slip":
            # Direct values instead of list of dictionaries
            for name, entry in self.earnings_entries:
                amount = entry.get().strip()
                data[name] = amount
            
            

        # Auto-fill invoice month
        if doc_type == "Invoice" and "Date" in data:
            try:
                dt = datetime.strptime(data["Date"], "%Y-%m-%d")
                data["Invoice Month"] = dt.strftime("%B %Y")
            except:
                data["Invoice Month"] = ""

        # Collect letter content
        if doc_type == "Request Letter":
            data["content"] = self.content_text.get("1.0", "end").strip()

        # Collect line items
        if doc_type in ["Invoice", "Sales Tax Invoice"]:
            columns = template["line_items"]["columns"]
            data["line_items"] = []
            for entry_row in self.line_item_entries:
                row = {}
                for idx, col in enumerate(columns):
                    val = entry_row[idx].get().strip()
                    row[col] = val
                if any(row.values()):
                    data["line_items"].append(row)

        return data

    def generate_document(self):
        try:
            doc_type = self.doc_type_var.get()
            if not doc_type:
                messagebox.showwarning("Missing Type", "Please select a document type.")
                return

            company = self.company_var.get()
            if not company:
                messagebox.showwarning("Missing Company", "Please select a company.")
                return

            data = self.collect_form_data()
            valid = self.doc_manager.templates[doc_type]["template_class"].validate_data(data)
            if not valid:
                messagebox.showerror("Validation Error", "Required fields are missing or incorrect.")
                return

            filepath = self.doc_manager.generate_document(company=company, doc_type=doc_type, data=data)

            result = messagebox.askyesno("Success", f"Document generated:\n{filepath}\n\nDo you want to add a signature?")
            if result:
                # Launch signature window
                sig_root = tk.Toplevel(self.root)
                PDFSignatureApp(sig_root, filepath)

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentApp(root)
    root.mainloop()
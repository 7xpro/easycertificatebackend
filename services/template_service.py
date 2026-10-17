from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import io
import pymupdf


def _coord(coordinates, key, axis, default):
    if not coordinates:
        return default

    point = coordinates.get(key, {})
    if isinstance(point, dict):
        return point.get(axis, default)

    flat_key = f"{key}_{axis}"
    return coordinates.get(flat_key, default)


def generate_pdf(
    name, email,id,date, template_path="template.pdf", 
):
    data={
        "name": name,
        "email": email,
        "id": id,
        "date": date
    }
   

   
    doc=pymupdf.open(template_path)
    page=doc[0]
    jobs=[]
    for key,value in data.items():
        for rect in page.search_for("{{"+ key+"}}"):
            page.add_redact_annot(rect, fill=(1, 1, 1))
            jobs.append((rect, value))
    page.apply_redactions()
    for rect, value in jobs:
        box=pymupdf.Rect(rect.x0-120, rect.y0-6, rect.x0+120, rect.y1+6)
        page.insert_textbox(box, value, fontsize=12, fontname="helv", align=1)
    pdf_bytes = doc.tobytes()   


    return pdf_bytes
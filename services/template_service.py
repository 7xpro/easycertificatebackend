from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import io


def _coord(coordinates, key, axis, default):
    if not coordinates:
        return default

    point = coordinates.get(key, {})
    if isinstance(point, dict):
        return point.get(axis, default)

    flat_key = f"{key}_{axis}"
    return coordinates.get(flat_key, default)


def generate_pdf(
    name, email, template_path="template.pdf", coordinates=None, course=None, date=None
):
    name_x = _coord(coordinates, "name", "x", 300)
    name_y = _coord(coordinates, "name", "y", 250)
    email_x = _coord(coordinates, "email", "x", 300)
    email_y = _coord(coordinates, "email", "y", 230)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(595, 842))
    c.drawString(name_x, name_y, name)
    c.drawString(email_x, email_y, email)
    # c.drawString(300, 210, course)
    # c.drawString(300, 190, date)
    c.save()
    packet.seek(0)

    # Merge overlay onto the single template page
    overlay = PdfReader(packet).pages[0]
    base = PdfReader(template_path).pages[0]
    base.merge_page(overlay)
    
    writer = PdfWriter()
    writer.add_page(base)

    # Return in-memory PDF instead of saving
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer
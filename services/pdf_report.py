"""
Para generar PDFs
"""

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def generar_pdf(df, titulo="Reporte de Puntos - TuCosto App"):
    """
    Genera un PDF en memoria con los datos de un DataFrame de Polars.
    Retorna un BytesIO listo para descargar.
    """
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # === Encabezado ===
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, 27 * cm, titulo)

    c.setFont("Helvetica", 10)
    y = 25 * cm
    line_height = 0.6 * cm

    # Encabezados de tabla
    c.drawString(2 * cm, y, "Material")
    c.drawString(8 * cm, y, "Cantidad")
    c.drawString(12 * cm, y, "Costo Unit.")
    c.drawString(16 * cm, y, "Costo Total")
    y -= line_height

    # === Filas ===
    for row in df.iter_rows():
        c.drawString(2 * cm, y, str(row[0]))
        c.drawString(8 * cm, y, str(row[1]))
        c.drawString(12 * cm, y, f"{row[2]:.2f}")
        c.drawString(16 * cm, y, f"{row[3]:.2f}")
        y -= line_height
        if y < 2 * cm:
            c.showPage()
            y = 27 * cm

    # === Total general ===
    total_general = df["Costo total"].sum()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y - 0.5 * cm, f"Total general: ${total_general:.2f}")

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

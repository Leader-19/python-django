import os
import tempfile
import subprocess
from django.http import HttpResponse
from openpyxl import load_workbook


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, file.name)
        
        # Save uploaded file
        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        pdf_filename = os.path.splitext(file.name)[0] + ".pdf"
        output_pdf = os.path.join(tmp, pdf_filename)

        try:
            # === Step 1: Pre-process with openpyxl to force better print settings ===
            wb = load_workbook(input_path)
            for ws in wb.worksheets:
                # Force Landscape orientation
                ws.page_setup.orientation = 'landscape'
                
                # Critical: Fit to 1 page wide (this solves wide column breaking)
                ws.page_setup.fitToWidth = 1
                ws.page_setup.fitToHeight = 0   # Let height auto-adjust
                
                # Optional: Adjust margins for more space
                ws.page_margins.left = 0.2
                ws.page_margins.right = 0.2
                ws.page_margins.top = 0.5
                ws.page_margins.bottom = 0.5

            wb.save(input_path)

            # === Step 2: Convert using LibreOffice with calc_pdf_Export ===
            result = subprocess.run([
                "soffice",
                "--headless",
                "--nologo",
                "--nolockcheck",
                "--convert-to", "pdf:calc_pdf_Export",
                "--outdir", tmp,
                input_path
            ], check=True, capture_output=True, text=True)

            if os.path.exists(output_pdf):
                with open(output_pdf, "rb") as f:
                    response = HttpResponse(
                        f.read(),
                        content_type="application/pdf",
                    )
                    response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
                    return response
            else:
                return HttpResponse("PDF file not generated", status=500)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or str(e)
            return HttpResponse(f"LibreOffice conversion failed: {error_msg}", status=500)
        except Exception as e:
            return HttpResponse(f"Conversion error: {str(e)}", status=500)
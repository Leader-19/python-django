import os
import tempfile
import subprocess
import sys

from django.http import HttpResponse

# Try to import win32com only on Windows
try:
    import win32com.client as win32
    import pythoncom
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:
        excel_path = os.path.join(temp_dir, file.name)

        # Save uploaded file
        with open(excel_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        pdf_path = os.path.join(
            temp_dir,
            os.path.splitext(file.name)[0] + ".pdf"
        )

        try:
            if WIN32_AVAILABLE and sys.platform == "win32":
                # === WINDOWS: Use Microsoft Excel (Best formatting) ===
                pythoncom.CoInitialize()
                try:
                    excel_app = win32.Dispatch("Excel.Application")
                    excel_app.Visible = False
                    excel_app.DisplayAlerts = False

                    workbook = excel_app.Workbooks.Open(os.path.abspath(excel_path))
                    sheet_count = workbook.Sheets.Count

                    # Improve layout for wide tables
                    for i in range(1, sheet_count + 1):
                        sheet = workbook.Sheets(i)
                        sheet.PageSetup.Orientation = 2          # Landscape
                        sheet.PageSetup.FitToPagesWide = 1
                        sheet.PageSetup.FitToPagesTall = False
                        sheet.PageSetup.Zoom = False

                    # Export ALL sheets to one PDF
                    workbook.ExportAsFixedFormat(
                        Type=0,  # PDF
                        Filename=os.path.abspath(pdf_path),
                        Quality=0,
                        IncludeDocProperties=True,
                        IgnorePrintAreas=False,
                        OpenAfterPublish=False
                    )

                    workbook.Close(False)

                finally:
                    try:
                        excel_app.Quit()
                    except:
                        pass
                    pythoncom.CoUninitialize()

            else:
                # === LINUX (Render): Use LibreOffice with better settings ===
                cmd = "soffice.exe" if sys.platform == "win32" else "libreoffice"
                
                subprocess.run([
                    cmd,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_dir,
                    '--printer-name', 'PDF',
                    excel_path
                ], check=True, timeout=120, capture_output=True)

            # Return PDF
            with open(pdf_path, "rb") as pdf:
                response = HttpResponse(
                    pdf.read(),
                    content_type="application/pdf"
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(pdf_path)}"'
                )
                return response

        except Exception as e:
            return HttpResponse(f"Conversion failed: {str(e)}", status=500)
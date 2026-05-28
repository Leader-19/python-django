import os
import pythoncom
import win32com.client
from django.http import HttpResponse


def convert_excel_to_pdf(file):
    pythoncom.CoInitialize()

    try:
        os.makedirs("media", exist_ok=True)

        input_path = os.path.abspath(f"media/{file.name}")
        output_path = input_path.replace(".xlsx", ".pdf")

        # Save uploaded file
        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Start Excel
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        workbook = excel.Workbooks.Open(input_path)

        #IMPORTANT: Fix layout for all sheets
        for sheet in workbook.Worksheets:

            # Keep original scale but fit width nicely
            sheet.PageSetup.Zoom = False
            sheet.PageSetup.FitToPagesWide = 1   # fit all columns into one page width
            sheet.PageSetup.FitToPagesTall = False

            # Enable printing gridlines (optional)
            sheet.PageSetup.PrintGridlines = True

            # Orientation auto-switch
            if sheet.UsedRange.Columns.Count > 8:
                sheet.PageSetup.Orientation = 2  # Landscape
            else:
                sheet.PageSetup.Orientation = 1  # Portrait

        # Export to PDF
        workbook.ExportAsFixedFormat(0, output_path)

        workbook.Close(False)
        excel.Quit()

        # Return PDF
        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="output.pdf"'

        return response

    finally:
        pythoncom.CoUninitialize()
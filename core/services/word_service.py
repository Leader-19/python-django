import os
import pythoncom
import win32com.client
from urllib.parse import quote
from django.http import FileResponse


def convert_word_to_pdf(file):
    pythoncom.CoInitialize()

    try:
        #  Ensure media directory exists
        media_dir = os.path.abspath("media")
        os.makedirs(media_dir, exist_ok=True)

        # Clean original filename (IMPORTANT)
        original_name = os.path.basename(file.name)
        base_name, _ = os.path.splitext(original_name)

        # Safe filenames
        input_filename = original_name
        output_filename = f"{base_name}.pdf"

        input_path = os.path.join(media_dir, input_filename)
        output_path = os.path.join(media_dir, output_filename)

        # Save uploaded file
        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Open Word and convert
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False

        try:
            doc = word.Documents.Open(input_path)
            doc.SaveAs(output_path, FileFormat=17)  # 17 = PDF
            doc.Close()
        finally:
            word.Quit()

        # Return file with CORRECT original name
        response = FileResponse(open(output_path, "rb"), content_type="application/pdf")

        #  CRITICAL: proper filename for ALL browsers
        response["Content-Disposition"] = (
            f'attachment; filename="{output_filename}"; '
            f"filename*=UTF-8''{quote(output_filename)}"
        )

        return response

    finally:
        pythoncom.CoUninitialize()
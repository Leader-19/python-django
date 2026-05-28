import os
import pythoncom
import win32com.client
from django.http import HttpResponse


def convert_word_to_pdf(file):
    # IMPORTANT: initialize COM
    pythoncom.CoInitialize()

    try:
        input_path = os.path.abspath(f"media/{file.name}")
        output_path = input_path.replace(".docx", ".pdf")

        # save uploaded file
        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # open Word
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False

        doc = word.Documents.Open(input_path)

        # 17 = PDF
        doc.SaveAs(output_path, FileFormat=17)

        doc.Close()
        word.Quit()

        # return file
        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="output.pdf"'

        return response

    finally:
        # VERY IMPORTANT: clean COM
        pythoncom.CoUninitialize()

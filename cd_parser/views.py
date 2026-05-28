import pandas as pd
import docx
from django.shortcuts import render
from django.http import HttpResponse
from weasyprint import HTML


# =====================================
# HELPER: DATAFRAME → PDF
# =====================================
def dataframe_to_pdf(df):
    html = df.to_html(index=False)

    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="output.pdf"'

    return response


# =====================================
# TXT → EXCEL / PDF
# =====================================
def upload_and_export(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("txt_file")
        option = request.POST.get("option")

        results = []

        # ==============================
        # SECTION FLAGS
        # ==============================
        in_tapin = False
        in_tapout = False

        # ==============================
        # TEMP STORAGE
        # ==============================
        current_cd = None
        current_days = None

        for line in uploaded_file:
            decoded_line = line.decode("utf-8", errors="ignore").strip()
            line_lower = decoded_line.lower()

            # ==============================
            # SECTION DETECTION
            # ==============================
            if "tap in missing" in line_lower or "tap in pending" in line_lower:
                in_tapin = True
                in_tapout = False
                continue

            elif "tap out missing" in line_lower or "tap out pending" in line_lower:
                in_tapout = True
                in_tapin = False
                continue

            elif "tap out" in line_lower and "tap out missing" not in line_lower and "tap out pending" not in line_lower:
                in_tapout = False
                continue

            # ==============================
            # TAP IN PENDING
            # ==============================
            if option in ["tapin_pending", "tapin_pending_pdf"] and in_tapin:
                if "pending for" in line_lower and "cd" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        current_cd = decoded_line[pos:pos + 17]
                        current_days = decoded_line.split("pending for")[1].split("days")[0].strip()
                    except:
                        current_cd = None
                        current_days = None

                elif "error:" in line_lower and current_cd:
                    try:
                        errorType = decoded_line.split("error:")[-1].strip()

                        if len(current_cd) == 17:
                            results.append({
                                "CD Reference": current_cd,
                                "Days": current_days,
                                "Error": errorType
                            })

                        current_cd = None
                        current_days = None
                    except:
                        continue

            # ==============================
            # TAP OUT PENDING
            # ==============================
            if option in ["tapout_pending", "tapout_pending_pdf"] and in_tapout:
                if "pending for" in line_lower and "cd" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        current_cd = decoded_line[pos:pos + 17]
                        current_days = decoded_line.split("pending for")[1].split("days")[0].strip()
                    except:
                        current_cd = None
                        current_days = None

                elif "error:" in line_lower and current_cd:
                    try:
                        errorType = decoded_line.split("error:")[-1].strip()

                        if len(current_cd) == 17:
                            results.append({
                                "CD Reference": current_cd,
                                "Days": current_days,
                                "Error": errorType
                            })

                        current_cd = None
                        current_days = None
                    except:
                        continue

            # ==============================
            # TAP IN MISSING
            # ==============================
            if option in ["tapin_missing", "tapin_missing_pdf"] and in_tapin:
                if "missing file" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        cd_code = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        if len(cd_code) == 17:
                            results.append({
                                "CD Reference": cd_code,
                                "Days": days
                            })
                    except:
                        continue

            # ==============================
            # TAP OUT MISSING
            # ==============================
            if option in ["tapout_missing", "tapout_missing_pdf"] and in_tapout:
                if "missing file" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        cd_code = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        if len(cd_code) == 17:
                            results.append({
                                "CD Reference": cd_code,
                                "Days": days
                            })
                    except:
                        continue

        # ==============================
        # DATAFRAME
        # ==============================
        df = pd.DataFrame(results).drop_duplicates()

        # ==============================
        # EXPORT PDF or EXCEL
        # ==============================
        if "pdf" in option:
            return dataframe_to_pdf(df)

        # ==============================
        # EXPORT EXCEL
        # ==============================
        filename_map = {
            "tapin_missing": "tapin_missing.xlsx",
            "tapin_pending": "tapin_pending.xlsx",
            "tapout_missing": "tapout_missing.xlsx",
            "tapout_pending": "tapout_pending.xlsx",
        }

        filename = filename_map.get(option, "output.xlsx")

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        df.to_excel(response, index=False, engine="openpyxl")

        return response

    return render(request, "upload.html")


# =====================================
# WORD → PDF
# =====================================
def word_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])

        html = f"<pre>{text}</pre>"
        pdf_file = HTML(string=html).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="word.pdf"'

        return response

    return render(request, "upload_word.html")

import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
import re


# CLEAN TEXT FUNCTION (FIXES □ SYMBOL ISSUE)
def clean_text(value):
    if not value:
        return value

    # remove hidden/unicode/bad characters
    value = str(value)
    value = value.replace("\ufeff", "")
    value = value.replace("\u200b", "")
    value = value.replace("\xa0", " ")
    value = value.replace("�", "")
    value = value.replace("□", "")

    # keep only printable characters
    return re.sub(r"[^\x20-\x7E]", "", value).strip()


def upload_and_export(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("txt_file")
        option = request.POST.get("option")

        results = []

        # SECTION FLAGS
        in_tapin = False
        in_tapout = False

        # MULTI-LINE STORAGE
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

            elif "tap out" in line_lower and "missing" not in line_lower and "pending" not in line_lower:
                in_tapout = False
                continue

            # ==============================
            # TAP IN PENDING
            # ==============================
            if option == "tapin_pending" and in_tapin:

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
            if option == "tapout_pending" and in_tapout:

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
            if option == "tapin_missing" and in_tapin:
                if "missing file" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        cd_code = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        results.append({
                            "CD Reference": cd_code,
                            "Days": days,
                            "Error": "Missing File"
                        })
                    except:
                        continue

            # ==============================
            # TAP OUT MISSING
            # ==============================
            if option == "tapout_missing" and in_tapout:
                if "missing file" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        cd_code = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        results.append({
                            "CD Reference": cd_code,
                            "Days": days,
                            "Error": "Missing File"
                        })
                    except:
                        continue

        # ==============================
        # CREATE DATAFRAME
        # ==============================
        df = pd.DataFrame(results).drop_duplicates()

        # CLEAN DATA (VERY IMPORTANT)
        df = df.applymap(clean_text)

        # ==============================
        # FILE NAME
        # ==============================
        filename_map = {
            "tapin_missing": "tapin_missing.xlsx",
            "tapin_pending": "tapin_pending.xlsx",
            "tapout_missing": "tapout_missing.xlsx",
            "tapout_pending": "tapout_pending.xlsx",
        }

        filename = filename_map.get(option, "output.xlsx")

        # ==============================
        # EXPORT EXCEL
        # ==============================
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        df.to_excel(response, index=False, engine="openpyxl")

        return response

    return render(request, "forms/upload.html")

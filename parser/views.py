import pandas as pd
import re
from django.shortcuts import render
from django.http import HttpResponse


# CLEAN TEXT (FIX □ + ENCODING)
def clean_text(value):
    if not value:
        return value

    value = str(value)
    value = value.replace("\ufeff", "")   # BOM
    value = value.replace("\u200b", "")   # zero width
    value = value.replace("\xa0", " ")    # nbsp
    value = value.replace("�", "")        # unknown char
    value = value.replace("□", "")        # box char

    return re.sub(r"[^\x20-\x7E]", "", value).strip()


def upload_and_export(request):
    if request.method == "POST":

        uploaded_file = request.FILES.get("txt_file")
        option = request.POST.get("option")

        results = []

        # FLAGS
        in_tapin = False
        in_tapout = False

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
                    error = decoded_line.split("error:")[-1].strip()

                    if current_cd:
                        results.append({
                            "CD Reference": current_cd,
                            "Days": current_days,
                            "Error": error
                        })

                    current_cd = None
                    current_days = None

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
                    error = decoded_line.split("error:")[-1].strip()

                    if current_cd:
                        results.append({
                            "CD Reference": current_cd,
                            "Days": current_days,
                            "Error": error
                        })

                    current_cd = None
                    current_days = None

            # ==============================
            # TAP IN MISSING
            # ==============================
            if option == "tapin_missing" and in_tapin:
                if "missing file" in line_lower:
                    try:
                        pos = decoded_line.find("CD")
                        cd = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        results.append({
                            "CD Reference": cd,
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
                        cd = decoded_line[pos:pos + 17]
                        days = decoded_line.split("reported")[1].split("days")[0].strip()

                        results.append({
                            "CD Reference": cd,
                            "Days": days,
                            "Error": "Missing File"
                        })
                    except:
                        continue

        # ==============================
        # CREATE DATAFRAME
        # ==============================
        df = pd.DataFrame(results).drop_duplicates()

        # CLEAN DATA (FIX applymap ERROR)
        df = df.apply(lambda col: col.map(lambda x: clean_text(x) if isinstance(x, str) else x))

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

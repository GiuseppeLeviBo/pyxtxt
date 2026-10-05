from . import register_extractor
import io
import zipfile
from typing import Optional
try:
    import openpyxl
except ImportError:
    openpyxl = None

if openpyxl:
    def xtxt_xlsx(file_buffer, max_rows_per_sheet: Optional[int] = None) -> str:
        # max_rows_per_sheet: None or a negative value means no limit
        file_buffer.seek(0)
        buffer_copy = io.BytesIO(file_buffer.read())

        if not zipfile.is_zipfile(buffer_copy):
            raise ValueError("Invalid XLSX (not a ZIP archive)")

        buffer_copy.seek(0)
        wb = openpyxl.load_workbook(buffer_copy, data_only=True, read_only=True)

        testo = []
        for sheet in wb.worksheets:
            if sheet.sheet_state != 'visible':
                continue
            testo.append(f"# {sheet.title}")
            count = 0
            for row in sheet.iter_rows(values_only=True):
                if max_rows_per_sheet is not None and 0 <= max_rows_per_sheet <= count:
                    break
                valori = [str(cell).strip() if cell is not None else "" for cell in row]
                if any(valori):
                    testo.append(" | ".join(valori))
                    count += 1

        return "\n".join(testo)

    register_extractor(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        xtxt_xlsx,
        name="XLSX"
    )

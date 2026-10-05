import io
from typing import Optional
from . import register_extractor
try:
    import xlrd
except ImportError:
    xlrd = None

if xlrd:

 def xtxt_xls(file_buffer, max_rows_per_sheet: Optional[int] = None) -> str:
    # max_rows_per_sheet: None or a negative value means no limit
    try:
        file_buffer.seek(0)
        workbook = xlrd.open_workbook(file_contents=file_buffer.read())
        testo = []

        for sheet in workbook.sheets():
            testo.append(f"# {sheet.name}")
            nrows = sheet.nrows
            if max_rows_per_sheet is not None and max_rows_per_sheet >= 0:
                nrows = min(nrows, max_rows_per_sheet)
            for row_idx in range(nrows):
                row = sheet.row(row_idx)
                valori = [str(cell.value).strip() for cell in row if str(cell.value).strip()]
                if valori:
                    testo.append(" | ".join(valori))

        return "\n".join(testo)

    except Exception as e:
        print(f"⚠️ Error while extracting XLS: {e}")
        return ""

 register_extractor(
    "application/vnd.ms-excel",
    xtxt_xls,
    name="XLS"
)


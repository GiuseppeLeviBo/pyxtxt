import io
from . import register_extractor
try:
    import xlrd
except ImportError:
    xlrd = None

if xlrd:

 def xtxt_xls(file_buffer, max_rows_per_sheet: int = 100) -> str:
    try:
        file_buffer.seek(0)
        workbook = xlrd.open_workbook(file_contents=file_buffer.read())
        testo = []

        for sheet in workbook.sheets():
            testo.append(f"# {sheet.name}")
            for row_idx in range(min(sheet.nrows, max_rows_per_sheet)):
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


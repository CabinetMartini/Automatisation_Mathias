
import tempfile
from fastapi import APIRouter, File, HTTPException, Request, UploadFile #type: ignore
from fastapi.responses import FileResponse #type: ignore
from core.excel_process import change_cell

routerimportMcdo = APIRouter()

@routerimportMcdo.post("/process")
async def upload_file_endpoint(
    request: Request,
    import_file: UploadFile = File(...),
    xlsx_file: UploadFile = File(...),
):
    try:
        """Endpoint pour télécharger des fichiers"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xslx") as tmp_xlsx:
            tmp_xlsx.write(await xlsx_file.read())
            tmp_xlsx_path = tmp_xlsx.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(await import_file.read())
            tmp_pdf_path = tmp_pdf.name    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        res = change_cell(tmp_xlsx_path, tmp_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return FileResponse(tmp_xlsx_path, filename="result.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


from fastapi import APIRouter, Depends, UploadFile, File
from core.security import get_current_account

router = APIRouter(prefix="/loans", tags=["loans"])

@router.post("/import-aid")
async def import_aid(file: UploadFile = File(...), current = Depends(get_current_account)):
    # TODO: parse StudentAid txt in AidImportService
    content = await file.read()
    return {"message": "stub", "bytes": len(content), "user_id": str(current.id)}

@router.get("")
def list_loans(current = Depends(get_current_account)):
    # TODO: query LoanEntity by user_id
    return {"message": "stub", "user_id": str(current.id), "loans": []}
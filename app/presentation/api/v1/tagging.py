from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.domain.tagging_schemas import TagTextRequest, TagTextResponse, PaginatedSentencesResponse, SentenceWithTokensResponse, UpdateSentenceRequest
from app.internal.tagging.http.controller import TaggingController
from app.shared.dependencies import get_admin_user, get_current_user

router = APIRouter(prefix="/tagging", tags=["tagging"])

controller = TaggingController()

@router.post("/run", response_model=TagTextResponse, dependencies=[Depends(get_admin_user)])
async def run_tagging(payload: TagTextRequest | None = None, file: UploadFile | None = File(None), db: Session = Depends(get_db)):
    # Accept either JSON text or a txt file
    text: str | None = None

    if file is not None:
        if file.content_type not in ("text/plain", "application/octet-stream") and not file.filename.endswith(".txt"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .txt files are supported")
        content_bytes = await file.read()
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # try cp1251 fallback common for RU texts
            text = content_bytes.decode("cp1251", errors="ignore")
    elif payload is not None and getattr(payload, "text", None):
        text = payload.text

    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide text in JSON or upload a .txt file")

    return await controller.tag_text(TagTextRequest(text=text), db)


# User routes (authenticated, not admin-only)
@router.get("/sentences", response_model=PaginatedSentencesResponse)
async def get_sentences(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return await controller.list_sentences(page, page_size, db)


@router.get("/sentences/{sentence_id}", response_model=SentenceWithTokensResponse)
async def get_sentence(sentence_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return await controller.get_sentence_with_tokens(sentence_id, db)


@router.patch("/sentences/{sentence_id}", response_model=SentenceWithTokensResponse)
async def patch_sentence(sentence_id: int, payload: UpdateSentenceRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return await controller.update_sentence_and_tokens(sentence_id, payload, db)

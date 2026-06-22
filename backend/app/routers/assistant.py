from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import AssistantLog
from ..schemas import SummarizeRequest, SummarizeResponse
from ..summarizer import summarize_text

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    payload: SummarizeRequest,
    session: AsyncSession = Depends(get_session),
):
    summary = summarize_text(payload.text)

    log = AssistantLog(request_text=payload.text, response_text=summary)
    session.add(log)
    await session.commit()
    await session.refresh(log)

    return SummarizeResponse(summary=summary, log_id=log.id)

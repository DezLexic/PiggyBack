from pydantic import BaseModel

from app.schemas.file import FileRead
from app.schemas.proposal import ProposedUpdateRead


class ProposalAcceptedResponse(BaseModel):
    proposal: ProposedUpdateRead
    file: FileRead

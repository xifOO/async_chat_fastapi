from typing import Annotated

from fastapi import Depends

from app.db.db import get_session_factory
from app.uow.uow import AbstractUnitOfWork, UnitOfWork


def get_uow() -> AbstractUnitOfWork:
    session_factory = get_session_factory()
    return UnitOfWork(session_factory)


UOWDep = Annotated[AbstractUnitOfWork, Depends(get_uow)]

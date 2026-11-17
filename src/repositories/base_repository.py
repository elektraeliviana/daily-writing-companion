"""
Base Repository implementing foundational database access methods.
"""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from src.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing basic CRUD operations.
    """
    def __init__(self, model_class: Type[ModelType], session: Session):
        self.model_class = model_class
        self.session = session

    def get_by_id(self, item_id: int) -> Optional[ModelType]:
        return self.session.get(self.model_class, item_id)

    def get_all(self) -> List[ModelType]:
        return self.session.query(self.model_class).all()

    def add(self, item: ModelType) -> ModelType:
        self.session.add(item)
        self.session.flush()
        return item

    def delete(self, item: ModelType) -> None:
        self.session.delete(item)
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    @classmethod
    def __tablename__(cls: type["Base"]) -> str:
        return f"{cls.__name__.lower()}s"

from sqlmodel import Field, Relationship, SQLModel


class Coin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    identifier_id: int | None = Field(
        default=None, foreign_key="identifier.id", ondelete="CASCADE"
    )
    identifier: "Identifier" = Relationship(back_populates="coins")


class Identifier(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    coins: list[Coin] = Relationship(
        back_populates="identifier",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

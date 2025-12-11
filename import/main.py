from sqlmodel import SQLModel, Session
from src.model import Coin, Identifier
from src.data import get_data
from src.db import engine


def main():
    SQLModel.metadata.create_all(engine)

    reader = get_data()
    identifier_cache: dict[str, Identifier] = {}

    with Session(engine) as session:
        for _, row in enumerate(reader):
            coin = Coin(id=int(row["ID"]))

            if name := row.get("Identified by"):
                if name not in identifier_cache:
                    identifier_cache[name] = Identifier(name=name)
                    session.add(identifier_cache[name])
                coin.identifier = identifier_cache[name]

            session.add(coin)
            session.commit()


if __name__ == "__main__":
    main()

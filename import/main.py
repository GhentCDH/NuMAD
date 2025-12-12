from sqlmodel import SQLModel, Session
from src.model import Coin, Identifier
from src.data import get_data
from src.db import engine

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def main():
    SQLModel.metadata.create_all(engine)

    reader = get_data()
    identifier_cache: dict[str, Identifier] = {}

    with Session(engine, autoflush=False) as session:
        for i, row in enumerate(reader):
            try:
                coin = Coin()
                if name := row.get("Identified by"):
                    if name not in identifier_cache:
                        identifier_cache[name] = Identifier(name=name)
                        session.add(identifier_cache[name])
                    coin.identifier = identifier_cache[name]
                session.add(coin)

                print(f"Created coin object {i}")
            except Exception as e:
                print(f"Failed row with id {row['ID']}: {e}")

        print("Commiting...")
        session.commit()
        print("Done!")


if __name__ == "__main__":
    main()

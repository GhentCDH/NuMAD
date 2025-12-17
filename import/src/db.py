import sqlmodel

from src.config import DB_STRING

engine = sqlmodel.create_engine(DB_STRING)


def create_updated_at_trigger(engine):
    with engine.begin() as conn:
        conn.execute(
            sqlmodel.text("""
            CREATE OR REPLACE FUNCTION update_modified_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = now();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        )

        for table_name, table in sqlmodel.SQLModel.metadata.tables.items():
            if "updated_at" in table.columns:
                conn.execute(
                    sqlmodel.text(f"""
                    DROP TRIGGER IF EXISTS update_{table_name}_modtime ON {table_name};
                    CREATE TRIGGER update_{table_name}_modtime
                        BEFORE UPDATE ON {table_name}
                        FOR EACH ROW EXECUTE FUNCTION update_modified_column();
                """)
                )

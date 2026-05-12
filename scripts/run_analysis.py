from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os


def run_analysis():

    try:
        # =====================================================
        # DATABASE CONNECTION
        # =====================================================

        load_dotenv()

        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise Exception("DATABASE_URL not found in .env file")

        engine = create_engine(database_url)

        # =====================================================
        # READ SQL FILE
        # =====================================================

        sql_file_path = "/opt/airflow/sql/copy_analysis.sql"


        try:
            with open(sql_file_path, "r") as f:
                sql = f.read()

        except FileNotFoundError:
            raise Exception(
                f"SQL file not found: {sql_file_path}"
            )

        # =====================================================
        # EMPTY SQL CHECK
        # =====================================================

        if not sql.strip():
            raise Exception("SQL file is empty")

        # =====================================================
        # EXECUTE SQL
        # =====================================================
        try:
            with engine.begin() as conn:
                conn.execute(text(sql))

            print("✅ Analysis completed successfully")

        except SQLAlchemyError as e:
            raise Exception(f"SQL execution failed: {e}")
        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        print("✅ Analysis completed successfully")

    except Exception as e:

        print(f"❌ Analysis pipeline failed: {e}")

        raise


if __name__ == "__main__":
    run_analysis()
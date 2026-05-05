from sqlalchemy import create_engine, text

def run_analysis():
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/crypto_pulse"
    )

    with open("/mnt/c/Users/Intern_PBI/Desktop/Project1/copy_analysis.sql", "r") as f:
        sql = f.read()

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

    print("✅ Analysis completed")

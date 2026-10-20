import os

import oracledb


def conectar() -> oracledb.Connection:
    usuario = os.getenv("DB_USER", "app_embedding")
    dsn = os.getenv("DB_DSN", "localhost:1521/FREEPDB1")
    return oracledb.connect(user=usuario, password=os.environ["DB_PASSWORD"], dsn=dsn)


if __name__ == "__main__":
    with conectar() as conexao, conexao.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM kb_docs")
        print("Número de registros na tabela kb_docs:", cur.fetchone()[0])


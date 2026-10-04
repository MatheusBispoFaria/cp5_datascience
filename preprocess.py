from pathlib import Path
import json

from src.data_service import _carregar_base_e_auditoria


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

PARQUET_PATH = PROCESSED_DIR / "despesas_poc.parquet"
AUDITORIA_PATH = PROCESSED_DIR / "auditoria.json"


def main():
    print("Processando bases oficiais...")

    df, auditoria = _carregar_base_e_auditoria()

    print(f"Registros do recorte: {len(df):,}")

    df.to_parquet(
        PARQUET_PATH,
        index=False,
        compression="snappy",
    )

    with open(
        AUDITORIA_PATH,
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            auditoria,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("Arquivos gerados:")
    print(PARQUET_PATH)
    print(AUDITORIA_PATH)


if __name__ == "__main__":
    main()
from pathlib import Path
import locale

import pandas as pd
from sqlalchemy import create_engine, text

from config import DB_CONFIG

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "Portuguese_Brazil")
    except:
        pass


BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "dataset" / "Sample - Superstore.csv"

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


def carregar_csv():

    print("Lendo CSV...")

    df = pd.read_csv(
        CSV_FILE,
        encoding="latin1"
    )

    df.columns = [
        "row_id",
        "order_id",
        "order_date",
        "ship_date",
        "ship_mode",
        "customer_id",
        "customer_name",
        "segment",
        "country",
        "city",
        "state",
        "postal_code",
        "region",
        "product_id",
        "category",
        "sub_category",
        "product_name",
        "sales",
        "quantity",
        "discount",
        "profit"
    ]

    df["order_date"] = pd.to_datetime(df["order_date"])

    df["ship_date"] = pd.to_datetime(df["ship_date"])

    return df


def limpar_tabelas():

    print("Limpando tabelas...")

    with engine.begin() as conn:

        conn.execute(text("TRUNCATE TABLE fato_vendas RESTART IDENTITY CASCADE"))

        conn.execute(text("TRUNCATE TABLE dim_cliente RESTART IDENTITY CASCADE"))

        conn.execute(text("TRUNCATE TABLE dim_produto RESTART IDENTITY CASCADE"))

        conn.execute(text("TRUNCATE TABLE dim_local RESTART IDENTITY CASCADE"))

        conn.execute(text("TRUNCATE TABLE dim_tempo RESTART IDENTITY CASCADE"))


def criar_dim_cliente(df):

    print("Criando Dim Cliente...")

    dim = (

        df[
            [
                "customer_id",
                "customer_name",
                "segment"
            ]
        ]

        .drop_duplicates()

        .sort_values("customer_id")

        .reset_index(drop=True)

    )

    dim.insert(0, "id_cliente", range(1, len(dim) + 1))

    dim.to_sql(

        "dim_cliente",

        engine,

        if_exists="append",

        index=False

    )

    return dim


def criar_dim_produto(df):

    print("Criando Dim Produto...")

    dim = (

        df[
            [
                "product_id",
                "product_name",
                "category",
                "sub_category"
            ]
        ]

        .drop_duplicates()

        .sort_values(
            [
                "product_id",
                "product_name"
            ]
        )

        .reset_index(drop=True)

    )

    dim.insert(0, "id_produto", range(1, len(dim) + 1))

    dim.to_sql(

        "dim_produto",

        engine,

        if_exists="append",

        index=False

    )

    return dim


def criar_dim_local(df):

    print("Criando Dim Local...")

    dim = (

        df[
            [
                "country",
                "region",
                "state",
                "city",
                "postal_code"
            ]
        ]

        .drop_duplicates()

        .sort_values(
            [
                "country",
                "region",
                "state",
                "city"
            ]
        )

        .reset_index(drop=True)

    )

    dim.insert(0, "id_local", range(1, len(dim) + 1))

    dim.to_sql(

        "dim_local",

        engine,

        if_exists="append",

        index=False

    )

    return dim

def criar_dim_tempo(df):

    print("Criando Dim Tempo...")

    datas = (
        pd.DataFrame(
            {
                "data": sorted(df["order_date"].drop_duplicates())
            }
        )
        .reset_index(drop=True)
    )

    datas["dia"] = datas["data"].dt.day
    datas["mes"] = datas["data"].dt.month
    datas["nome_mes"] = datas["data"].dt.strftime("%B")
    datas["trimestre"] = datas["data"].dt.quarter
    datas["ano"] = datas["data"].dt.year
    datas["dia_semana"] = datas["data"].dt.strftime("%A")

    datas.insert(0, "id_tempo", range(1, len(datas) + 1))

    datas.to_sql(
        "dim_tempo",
        engine,
        if_exists="append",
        index=False
    )

    return datas


def criar_fato(df,
               dim_cliente,
               dim_produto,
               dim_local,
               dim_tempo):

    print("Criando Tabela Fato...")

    fato = df.copy()

    fato = fato.merge(
        dim_cliente[
            [
                "id_cliente",
                "customer_id"
            ]
        ],
        on="customer_id",
        how="left"
    )

    fato = fato.merge(
        dim_produto[
            [
                "id_produto",
                "product_id",
                "product_name"
            ]
        ],
        on=[
            "product_id",
            "product_name"
        ],
        how="left"
    )

    fato = fato.merge(
        dim_local[
            [
                "id_local",
                "country",
                "region",
                "state",
                "city",
                "postal_code"
            ]
        ],
        on=[
            "country",
            "region",
            "state",
            "city",
            "postal_code"
        ],
        how="left"
    )

    fato = fato.merge(
        dim_tempo[
            [
                "id_tempo",
                "data"
            ]
        ],
        left_on="order_date",
        right_on="data",
        how="left"
    )

    fato = fato[
        [
            "id_cliente",
            "id_produto",
            "id_local",
            "id_tempo",
            "order_id",
            "ship_mode",
            "sales",
            "quantity",
            "discount",
            "profit"
        ]
    ]

    fato.columns = [
        "id_cliente",
        "id_produto",
        "id_local",
        "id_tempo",
        "order_id",
        "ship_mode",
        "sales",
        "quantity",
        "discount",
        "profit"
    ]

    fato.to_sql(
        "fato_vendas",
        engine,
        if_exists="append",
        index=False
    )

    return fato

def validar_carga():

    print("\nVALIDANDO CARGA\n")

    with engine.connect() as conn:

        consultas = [
            "SELECT COUNT(*) FROM dim_cliente",
            "SELECT COUNT(*) FROM dim_produto",
            "SELECT COUNT(*) FROM dim_local",
            "SELECT COUNT(*) FROM dim_tempo",
            "SELECT COUNT(*) FROM fato_vendas"
        ]

        nomes = [
            "Dim Cliente",
            "Dim Produto",
            "Dim Local",
            "Dim Tempo",
            "Fato Vendas"
        ]

        for nome, sql in zip(nomes, consultas):

            total = conn.execute(text(sql)).scalar()

            print(f"{nome}: {total}")


def main():

    print("=" * 60)
    print("ETL - DATA WAREHOUSE SUPERSTORE")
    print("=" * 60)

    df = carregar_csv()

    limpar_tabelas()

    dim_cliente = criar_dim_cliente(df)

    dim_produto = criar_dim_produto(df)

    dim_local = criar_dim_local(df)

    dim_tempo = criar_dim_tempo(df)

    fato = criar_fato(
        df,
        dim_cliente,
        dim_produto,
        dim_local,
        dim_tempo
    )

    validar_carga()

    print("\nETL FINALIZADO COM SUCESSO")

    print(f"\nRegistros carregados na Fato: {len(fato)}")


if __name__ == "__main__":
    main()
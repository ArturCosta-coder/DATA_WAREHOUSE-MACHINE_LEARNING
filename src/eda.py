from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from config import DB_CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT = BASE_DIR / "graficos"

OUTPUT.mkdir(exist_ok=True)

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

query = """
SELECT

    f.sales,
    f.quantity,
    f.discount,
    f.profit,
    f.ship_mode,
    p.category,
    p.sub_category,
    c.segment,
    l.region,
    l.state,
    t.data,
    t.ano,
    t.mes

FROM fato_vendas f

JOIN dim_cliente c
ON f.id_cliente = c.id_cliente

JOIN dim_produto p
ON f.id_produto = p.id_produto

JOIN dim_local l
ON f.id_local = l.id_local

JOIN dim_tempo t
ON f.id_tempo = t.id_tempo
"""

df = pd.read_sql(query, engine)

print(df.head())

print(df.describe())

print(df.isnull().sum())

plt.figure(figsize=(10,6))

plt.hist(df["sales"], bins=30)

plt.title("Distribuição das Vendas")

plt.xlabel("Sales")

plt.ylabel("Frequência")

plt.tight_layout()

plt.savefig(OUTPUT / "01_distribuicao_vendas.png")

plt.close()


categoria = (

    df.groupby("category")["profit"]

    .sum()

    .sort_values(ascending=False)

)

plt.figure(figsize=(10,6))

categoria.plot(kind="bar")

plt.title("Lucro por Categoria")

plt.xlabel("Categoria")

plt.ylabel("Lucro")

plt.tight_layout()

plt.savefig(OUTPUT / "02_lucro_categoria.png")

plt.close()


vendas_mes = (

    df.groupby(["ano","mes"])["sales"]

    .sum()

    .reset_index()

)

vendas_mes["periodo"] = (

    vendas_mes["ano"].astype(str)

    + "-"

    + vendas_mes["mes"].astype(str).str.zfill(2)

)

plt.figure(figsize=(14,6))

plt.plot(

    vendas_mes["periodo"],

    vendas_mes["sales"]

)

plt.xticks(rotation=90)

plt.title("Evolução Temporal das Vendas")

plt.xlabel("Período")

plt.ylabel("Vendas")

plt.tight_layout()

plt.savefig(OUTPUT / "03_evolucao_temporal.png")

plt.close()


regiao = (

    df.groupby("region")["sales"]

    .sum()

)

plt.figure(figsize=(8,6))

regiao.plot(kind="bar")

plt.title("Vendas por Região")

plt.xlabel("Região")

plt.ylabel("Total de Vendas")

plt.tight_layout()

plt.savefig(OUTPUT / "04_vendas_regiao.png")

plt.close()


segmento = (

    df.groupby("segment")["profit"]

    .sum()

)

plt.figure(figsize=(8,6))

segmento.plot(kind="bar")

plt.title("Lucro por Segmento")

plt.xlabel("Segmento")

plt.ylabel("Lucro")

plt.tight_layout()

plt.savefig(OUTPUT / "05_lucro_segmento.png")

plt.close()


correlacao = df[

    [

        "sales",

        "quantity",

        "discount",

        "profit"

    ]

].corr()

print()

print("Correlação")

print(correlacao)

print()

print("EDA FINALIZADA")

print()

print("Gráficos salvos em:")

print(OUTPUT)
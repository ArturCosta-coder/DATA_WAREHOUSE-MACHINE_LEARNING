from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from config import DB_CONFIG

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.neighbors import KNeighborsClassifier

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

import numpy as np


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

c.segment,

p.category,

p.sub_category,

l.region

FROM fato_vendas f

JOIN dim_cliente c
ON c.id_cliente=f.id_cliente

JOIN dim_produto p
ON p.id_produto=f.id_produto

JOIN dim_local l
ON l.id_local=f.id_local

"""

df = pd.read_sql(query,engine)

df["lucro"]=(df["profit"]>0).astype(int)

encoders={}

for coluna in [

"ship_mode",

"segment",

"category",

"sub_category",

"region"

]:

    le=LabelEncoder()

    df[coluna]=le.fit_transform(df[coluna])

    encoders[coluna]=le


X=df[

[
"sales",
"quantity",
"discount",
"ship_mode",
"segment",
"category",
"sub_category",
"region"
]

]

y=df["lucro"]

X_train,X_test,y_train,y_test=train_test_split(

X,

y,

test_size=0.25,

random_state=42,

stratify=y

)

scaler=StandardScaler()

X_train_sc=scaler.fit_transform(X_train)

X_test_sc=scaler.transform(X_test)

print("="*70)

print("CLASSIFICAÇÃO")

print("="*70)

modelos={

"KNN":KNeighborsClassifier(),

"Decision Tree":DecisionTreeClassifier(random_state=42),

"Random Forest":RandomForestClassifier(
    n_estimators=200,
    random_state=42
),

"Logistic Regression":LogisticRegression(
    max_iter=500
)

}

resultado=[]

for nome,modelo in modelos.items():

    if nome=="KNN":

        modelo.fit(X_train_sc,y_train)

        pred=modelo.predict(X_test_sc)

    elif nome=="Logistic Regression":

        modelo.fit(X_train_sc,y_train)

        pred=modelo.predict(X_test_sc)

    else:

        modelo.fit(X_train,y_train)

        pred=modelo.predict(X_test)

    acc=accuracy_score(y_test,pred)

    prec=precision_score(y_test,pred)

    rec=recall_score(y_test,pred)

    f1=f1_score(y_test,pred)

    cm=confusion_matrix(y_test,pred)

    resultado.append(

        [

        nome,

        acc,

        prec,

        rec,

        f1

        ]

    )

    print()

    print(nome)

    print()

    print("Accuracy :",round(acc,4))

    print("Precision:",round(prec,4))

    print("Recall   :",round(rec,4))

    print("F1 Score :",round(f1,4))

    print()

    print("Confusion Matrix")

    print(cm)

resultado=pd.DataFrame(

resultado,

columns=[

"Modelo",

"Accuracy",

"Precision",

"Recall",

"F1"

]

)

print()

print("="*70)

print("COMPARAÇÃO")

print("="*70)

print(resultado.sort_values(

"Accuracy",

ascending=False

))

print()

print("="*70)

print("REGRESSÃO LINEAR")

print("="*70)

X=df[

[
"quantity",
"discount",
"ship_mode",
"segment",
"category",
"sub_category",
"region"
]

]

y=df["sales"]

X_train,X_test,y_train,y_test=train_test_split(

X,

y,

test_size=0.25,

random_state=42

)

scaler=StandardScaler()

X_train=scaler.fit_transform(X_train)

X_test=scaler.transform(X_test)

modelo=LinearRegression()

modelo.fit(

X_train,

y_train

)

pred=modelo.predict(X_test)

mae=mean_absolute_error(

y_test,

pred

)

mse=mean_squared_error(

y_test,

pred

)

rmse=np.sqrt(mse)

r2=r2_score(

y_test,

pred

)

print()

print("MAE :",round(mae,2))

print("MSE :",round(mse,2))

print("RMSE:",round(rmse,2))

print("R²  :",round(r2,4))

print()

print("PROJETO FINALIZADO")
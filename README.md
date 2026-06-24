# Projeto Final — Desenvolvimento para Ciência de Dados II

## Construção de um Data Warehouse e Aplicação de Machine Learning

### Objetivo

Este projeto apresenta o desenvolvimento completo de uma solução analítica utilizando Data Warehouse e técnicas de Machine Learning aplicadas a um conjunto de dados de vendas.

O projeto contempla:

* Modelagem Dimensional
* Implementação em PostgreSQL
* Processo ETL
* Análise Exploratória de Dados (EDA)
* Machine Learning
* Comparação de Modelos
* Geração de Insights

---

## Estrutura

```
Projeto

├── SQL
│   ├── CreateDatabase.sql
│   ├── CreateTables.sql
│   ├── ETL.sql
│   └── Views.sql
│
├── Notebook
│   └── Projeto_Final.ipynb
│
├── Slides
│   └── Apresentação.pptx
│
└── Documentação
```

---

## Modelagem

O Data Warehouse foi desenvolvido utilizando o modelo Star Schema.

### Tabela Fato

* Fato_Vendas

### Dimensões

* Dim_Cliente
* Dim_Produto
* Dim_Local
* Dim_Tempo

Além disso, foi utilizada uma Dimensão Degenerada para representar o Número do Pedido.

---

## Machine Learning

### Classificação

* K-Nearest Neighbors
* Decision Tree
* Random Forest
* Logistic Regression

### Regressão

* Linear Regression

---

## Métricas

### Classificação

* Accuracy
* Precision
* Recall
* F1-Score
* Confusion Matrix

### Regressão

* MAE
* MSE
* RMSE
* R²

---

## Ferramentas

* PostgreSQL
* Python
* Pandas
* Matplotlib
* Scikit-learn
* Jupyter Notebook

---

## Autor

Artur Nemer Xavier Costa

Disciplina: Desenvolvimento para Ciência de Dados II

Professor: José Antonio de Paiva Júnior

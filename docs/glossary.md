# Glossário — Projeto FinOps Pipeline

## Domínio de Negócio

**FinOps (Financial Operations)**
Disciplina que combina finanças, tecnologia e negócio para otimizar custos de cloud. O objetivo é dar visibilidade sobre onde o dinheiro de cloud é gasto e por quem.

**Budget (Orçamento)**
Valor máximo mensal aprovado para um time gastar em um provedor de cloud. Quando o custo real supera o budget, o time está "over budget".

**Cost Entry (Lançamento de Custo)**
Registro diário do custo gerado por um recurso de cloud. É a unidade mínima de medição — um lançamento = um recurso × um dia.

**Cost Center (Centro de Custo)**
Código contábil que agrupa gastos de cloud por unidade de negócio. Usado para rateio e accountability.

**Team (Time)**
Grupo de pessoas responsável por um conjunto de recursos de cloud. Cada time tem donos de orçamento e é responsabilizado por seus gastos.

**Provider (Provedor)**
Empresa que fornece infraestrutura de cloud. No projeto: `AWS`, `GCP`, `Azure`.

**Resource (Recurso)**
Unidade alocável de cloud: VMs, bancos de dados, buckets de storage, funções serverless, etc.

**Environment (Ambiente)**
Classificação do propósito de um recurso: `prod`, `staging`, `dev`. Usado para detectar desperdício em ambientes não-produtivos.

**MoM (Month-over-Month)**
Variação percentual de um indicador comparando o mês atual com o anterior.

**Over Budget**
Situação em que o custo real de um time supera o budget aprovado para aquele mês/provedor.

---

## Arquitetura de Dados

**Medallion Architecture**
Padrão de organização de data lake em camadas de qualidade crescente: Landing → Bronze → Silver → Gold.

**Landing Zone**
Primeira camada do pipeline. Armazena dados brutos extraídos da fonte (Postgres) sem nenhuma transformação. Formato: JSON. Particionamento: `year=/month=/day=`.

**Bronze Layer**
Segunda camada. Dados da landing convertidos para Delta Lake com tipagem explícita. Sem regras de negócio — apenas casting e adição de metadados de pipeline (`_ingested_at`, `_source`).

**Silver Layer**
Terceira camada. Dados limpos, deduplicados e padronizados. Aplicação de regras de negócio simples: normalização de moeda, validação de campos obrigatórios, joins de enriquecimento.

**Gold Layer**
Quarta e última camada. Agregações finais prontas para consumo analítico. Dados carregados para Postgres (`finops_gold`) para consumo pelo Metabase.

**Delta Lake**
Formato de armazenamento open-source que adiciona transações ACID, versionamento (time travel) e schema enforcement sobre arquivos Parquet. Armazenado no MinIO.

**Data Mart**
Subconjunto de dados otimizado para um caso de uso analítico específico. Ex: `monthly_cost_by_team`.

**Partition Pruning**
Otimização do Spark/Delta que ignora partições que não correspondem ao filtro da query. Ex: `WHERE year=2025 AND month=6` lê apenas a partição `year=2025/month=06/`.

**Time Travel**
Funcionalidade do Delta Lake para consultar versões anteriores de uma tabela. Ex: `SELECT * FROM tabela VERSION AS OF 3`.

---

## Infraestrutura

**MinIO**
Object storage compatível com S3 rodando localmente via Docker. Simula o Amazon S3 em ambiente de desenvolvimento. Buckets acessados via protocolo `s3a://`.

**s3a://**
Protocolo Hadoop para acessar object storage compatível com S3. Prefixo usado nos paths do Spark: `s3a://datalake/bronze/cost_entries/`.

**Apache Spark**
Motor de processamento distribuído. Executa as transformações nos notebooks via PySpark. Conecta ao MinIO via `hadoop-aws`.

**Apache Airflow**
Orquestrador de pipelines. Executa os notebooks via `PapermillOperator` com schedule diário. DAGs encadeados via `ExternalTaskSensor`.

**Papermill**
Biblioteca que executa notebooks Jupyter programaticamente, passando parâmetros como `execution_date`. Usado pelo Airflow via `PapermillOperator`.

**PapermillOperator**
Operador do Airflow que usa o Papermill para executar um notebook `.ipynb` como task, injetando parâmetros via célula `parameters`.

**ExternalTaskSensor**
Operador do Airflow que aguarda a conclusão de uma task em outro DAG antes de prosseguir.

**Metabase**
Ferramenta de BI open-source. Conecta ao schema `finops_gold` no Postgres e expõe KPIs financeiros pré-configurados.

---

## KPIs do Gold Layer

**Total Spend MTD**
Custo total acumulado no mês corrente, em USD.

**Budget Utilization %**
`(custo_real / budget_aprovado) × 100` para o mês corrente. Acima de 100% = over budget.

**MoM Cost Variation %**
`((custo_mes_atual - custo_mes_anterior) / custo_mes_anterior) × 100`.

**Teams Over Budget**
Contagem de times cujo `budget_utilization` superou 100% no mês corrente.

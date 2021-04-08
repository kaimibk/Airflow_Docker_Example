Coming Soon

## Environment File

Create an `.env` under the project root, example file:

```
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
FERNET_KEY=YOUR FERNET KEY
LOAD_EX=y
```
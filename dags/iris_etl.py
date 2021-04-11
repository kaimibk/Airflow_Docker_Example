from datetime import timedelta, datetime
import os
import urllib
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd

dag_args = {
    "owner": "kaimibk",
    "email": "kaimibk@gmail.com",
    "start_date": datetime(2021, 4, 10),
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

dag = DAG(
    dag_id="Simple_Iris_ETL",
    default_args=dag_args,
    schedule_interval=None,
    tags=["example"]
)

_data_root = "/usr/local/airflow/data/"

def extract_data(source_path: str, destination_path: str) -> None:
    """Extract data from URL and save to local file

    Args:
        source_path (str): URL of data file
        destination_path (str): File directory to write to
    """
    print("Downloading Data...")
    urllib.request.urlretrieve(source_path, destination_path)
    

t1 = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    op_kwargs={
        "source_path": "https://gist.githubusercontent.com/curran/a08a1080b88344b0c8a7/raw/0e7a9b0a5d22642a06d3d5b9bcbad9890c8ee534/iris.csv",
        "destination_path": os.path.join(_data_root, "data.csv")
        },
    dag=dag
)

def _to_categorical(species: str) -> int:
    """Convert species to a integer category

    Args:
        species (str): iris species

    Returns:
        int: encoded species
    """
    if species=="setosa":
        return 0
    elif species=="versicolor":
        return 1
    elif species=="virginica":
        return 2
    else:
        raise "InvalidSpecies"

def transform_data(data_path: str, **kwargs) -> pd.DataFrame:
    """Transform the data (only encode the species label)

    Args:
        data_path (str): Location of csv file to transform
    """
    print("Transforming Data...")
    df = pd.read_csv(data_path)
    print(df.head())

    print("Encoding Species Label")
    df["species"] = df["species"].apply(_to_categorical)

    print(df["species"].head())

    kwargs["ti"].xcom_push("df", value=df)

t2 = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    op_kwargs={
        "data_path": os.path.join(_data_root, "data.csv")
        },
    dag=dag,
    provide_context=True,
)

def load_data(destination_path: str, **kwargs) -> None:
    """Save the data into a csv file

    Args:
        destination_path (str): File directory to write to
    """
    ti = kwargs["ti"]
    df = ti.xcom_pull(key=None, task_ids="transform_data")

    print(f"Saving Dataframe to {destination_path}")

    df.to_csv(destination_path)

t3 = PythonOperator(
    task_id="load_data",
    python_callable=load_data,
    op_kwargs={
        "destination_path": os.path.join(_data_root, "data_transform.csv")
    },
    dag=dag,
    provide_context=True,
)

t1 >> t2 >> t3
# import the libraries

from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago

#defining DAG arguments

# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'NeilP',
    'start_date': days_ago(0),
    'email': ['NeilP@somemail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# defining the DAG

# define the DAG
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='Apache Airflow Final Assignment',
    schedule_interval=timedelta(days=1),
)

# define the tasks

# define the first task

unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command="tar -xzf tolldata.tgz -C /home/project/airflow/dags/finalassignment",
    dag=dag,
)

# define the second task
extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command=""""awk -F"," "{print $1','$2','$3','$4}"\
     /home/project/airflow/dags/finalassignment/vehicle-data.csv\
     > /home/project/airflow/dags/finalassignment/csv-data.csv""",
    dag=dag,
)
#third task

extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command="""awk -F"\t" "{print $5'\t'$6'\t'$7}"\
     /home/project/airflow/dags/finalassignment/tollplaza-data.tsv\
     > /home/project/airflow/dags/finalassignment/tsv-data.csv""",
    dag=dag,
)

#fourth task

extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command="""awk "{print substr($0, 69) "," substr($0, 101)}\
     /home/project/airflow/dags/finalassignment/payment-data.txt\
     > /home/project/airflow/dags/finalassignment/fixed_width_data.csv""",
    dag=dag,
)


#fifth task
consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command="""paste -d','\
     /home/project/airflow/dags/finalassignment/csv-data.csv\
     /home/project/airflow/dags/finalassignment/tsv-data.csv\
     /home/project/airflow/dags/finalassignment/fixed_width_data.csv\
     > /home/project/airflow/dags/finalassignment/extracted_data.csv""",
    dag=dag,
)

#sixth task

transform_data= BashOperator(
    task_id='transform_data',
    bash_command="""awk "BEGIN{FS=OFS=','} { $4 = toupper($4) } 1"\
     /home/project/airflow/dags/finalassignment/extracted_data.csv\ 
    > /home/project/airflow/dags/finalassignment/transformed_data.csv""",
    dag=dag,
)

# task pipeline
unzip_data >> extract_data_from_csv >>extract_data_from_tsv\
>>extract_data_from_fixed_width>>consolidate_data>>transform_data
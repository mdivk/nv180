from __future__ import print_function

#airflow related packages
import airflow
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator

#email related packages
import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
import os
import time

#other packages
from pprint import pprint
import subprocess

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

dag = DAG(
    dag_id='BM3_Ingestion_ETL_Collection', default_args=args,
    schedule_interval=None)

def run_impala_ingestion(**context):
    pprint(context)
    print("starting BM3 ingestion job from within airflow now....")
    print("Working folder: " + str(os.getcwd()))
    #subprocess.Popen(['./test_impala.sh'], shell=1) 
    subprocess.Popen(['./BM3_ingestion.sh'], shell=1) 

    return 'Completed BM3 ingestion job from within airflow'

def run_impala_etl(**context):
    pprint(context)
    print("starting BM3 ETL job from within airflow now....")
    subprocess.Popen(['./BM3_etl.sh'], shell=1) 

    return 'Completed BM3 ETL job from within airflow'

def run_impala_collection(**context):
    pprint(context)
    print("starting BM3 collection job from within airflow now....")
    subprocess.Popen(['./BM3_collection.sh'], shell=1) 

    return 'Completed BM3 collection job from within airflow'

def build_email(**context):

    message = ""

    for key, value in context.items():
        try:
            message = message + "\n\n" + key + ": " + str(value)
        except:
            message = message + "\n\n" + key + ": N/A" 

    log_dag_name = os.environ['AIRFLOW_CTX_DAG_ID']
    log_task_name = os.environ['AIRFLOW_CTX_TASK_ID']
    log_time = os.environ['AIRFLOW_CTX_EXECUTION_DATE']

    log = '/home/pchoix/airflow/logs/' + log_dag_name + '/' + log_task_name + '/' + log_time + '/' + '1.log'
    print("log path: " + log)
    file1 = open(log, "r")

    me = os.path.realpath(__file__)
    print("me: " + me)
    file2 = open(me, "r")
    
    email_op = EmailOperator(
        task_id='send_email',
        to="pchoix@company.com",
        subject="BM3 Workflow Completed for Client1 Pipeline - Ingestion_ETL_Collection",
        html_content=message,
        files=[file1.name, file2.name]
        )

    email_op.execute(context)

    file1.close()
    file2.close()

    return 'Email is sent'

ingestion = PythonOperator(
    task_id='ingestion',
    provide_context=True,
    python_callable=run_impala_ingestion,
    dag=dag)

etl = PythonOperator(
    task_id='etl',
    provide_context=True,
    python_callable=run_impala_etl,
    dag=dag)

collection = PythonOperator(
    task_id='collection',
    provide_context=True,
    python_callable=run_impala_collection,
    dag=dag)

send_notification = PythonOperator(
    task_id='send_notification',
    provide_context=True,
    #python_callable=SendEmail,
    dag_status = 1
    python_callable=build_email, 
    dag=dag,
)

send_notification_start = PythonOperator(
    task_id='send_notification_start',
    provide_context=True,
    #python_callable=SendEmail,
    dag_status = 0 
    python_callable=build_email(dag_status), 
    dag=dag,
)



send_notification_start >> ingestion >> etl >> collection >> send_notification

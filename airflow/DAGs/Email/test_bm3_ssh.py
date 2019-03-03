import airflow
from builtins import range
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG
from datetime import datetime
from datetime import timedelta
from tempfile import NamedTemporaryFile
from pprint import pprint
import os

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

dag = DAG(
    dag_id='test_BM3_ssh', default_args=args,
    schedule_interval='0 0 * * *',
    start_date=datetime(2018, 12, 7),
    )


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
        subject="Test Email With Log Attachment using EmailOperator",
        html_content=message,
        files=[file1.name, file2.name]
        )

    email_op.execute(context)

    file1.close()
    file2.close()

notification = PythonOperator(
    task_id="notification", python_callable=build_email, provide_context=True, dag=dag
)

task1 = SSHOperator(
    task_id='switch2ALhome',
    bash_command="cd /home/pchoix/BM3 && ./BM3.py runjob -p client1 -j ingestion",
    dag=dag)

ssh_task = SSHOperator(
    ssh_conn_id='ssh_default', 
    task_id='ssh_to_other_host',
    command='cd /home/pchoix/BM3;./BM3.py runjob -p client1 -j ingestion', 
    dag=dag
)

task1.set_downstream(notification)

if __name__ == "__main__":
    dag.cli()
#airflow test test_bm3_ssh ssh_to_other_host 2001-01-01 works! ssh_default must be pre-created in Airflow/Admin/Connections

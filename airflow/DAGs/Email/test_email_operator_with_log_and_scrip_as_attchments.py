from airflow.models import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from tempfile import NamedTemporaryFile
from pprint import pprint
import os

dag = DAG(
    dag_id = "email_operator_with_log_attachment_example",
    description="Sample Email Example with File attachments",
    schedule_interval="@daily",
    start_date=datetime(2018, 12, 7),
    catchup=False,
)


def build_email(**context):

	pprint(context)
	print("ds:" + context.pop('ds'))	
	print("task_instance_key_str:" + context.get('task_instance_key_str'))
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

email_op_python = PythonOperator(
    task_id="python_send_email", python_callable=build_email, provide_context=True, dag=dag
)

import airflow
from airflow.models import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime
from datetime import timedelta
from tempfile import NamedTemporaryFile
from pprint import pprint

import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path

args = {
    'owner': 'pchoix',
    'start_date': airflow.utils.dates.days_ago(2)
}

dag = DAG(
	dag_id = "dag_id_email_test",
	description="Sample Email with File attachments with PythonOperator and EmailOperator",
	schedule_interval="@daily",
	start_date=datetime(2018, 12, 7),
)

def SendEmail(**kwargs):
	print("kwargs info below:")
	pprint(kwargs)

	from_email = "Airflow_Notification_No_Reply@company.Com"
	send_to_email = 'pchoix@company.com'
	subject = 'Test Email with Attachment From task_id_email_task_python_operator'
	message = 'This is a test Email From task_id_email_task_python_operator'

	for key, value in kwargs.items():
		try:
			message = message + "\n" + key + ": " + str(value)
		except:
			message = message + "\n" + key + ": N/A" 
	file_location = '201902260920AM.log'

	msg = MIMEMultipart()
	msg['From'] = from_email
	msg['To'] = send_to_email
	msg['Subject'] = subject

	msg.attach(MIMEText(message, 'plain'))

	filename = os.path.basename(file_location)
	attachment = open(file_location, "rb")
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

	msg.attach(part)


	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()

email_task_email_operator = EmailOperator(
    task_id='task_id_email_task_email_operator',
    owner='Pasle Choix',
    to='pchoixcompany.com',
    subject='Test Email From task_id_email_task_python_operator with macro: start_date {{ ds }}',
    params={'content1': 'random'},
    html_content="Templated Content: content1 - {{ params.content1 }}  task_key - {{ task_instance_key_str }} test_mode - {{ test_mode }} task_owner - {{ task.owner}} hostname - {{ ti.hostname }}",
    dag=dag,)

email_task_python_operator = PythonOperator(
    owner="pchoix",
    task_id='task_id_email_task_python_operator',
    provide_context=True,
    python_callable=SendEmail,
    op_kwargs=None,
    #op_kwargs={'dag_id_macro': {{ dag.dag_id }}, 'task_id_macro': {{  task.task_id }}},
    dag=dag,
)

dummy_operator = DummyOperator(task_id='task_id_dummy_task', retries=3, dag=dag)

email_task_email_operator >> email_task_python_operator >> dummy_operator

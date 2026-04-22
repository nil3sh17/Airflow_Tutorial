from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator

@dag(
        dag_id="bash_operator_dag"
)

def bash_operator_dag():

    @task.python
    def first_dag_task():
        print("Hello World, Third DAG") 
    
    @task.python
    def second_dag_task():
        print("Hello World, Third DAG, Second Task")

    @task.bash
    def bash_task_new() -> str:
        return "echo Hello World, Third DAG, 3rd Task, Bash Task"

    bash_task_old_way = BashOperator(
        task_id="bash_task_old_way",
        bash_command="echo https://airflow.apache.org/",
    )
    
    first = first_dag_task()
    second = second_dag_task()
    third = bash_task_new()
    fourth = bash_task_old_way

    first >> second >> third >> fourth

#Instantiating the DAG
bash_operator_dag()
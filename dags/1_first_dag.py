from airflow.sdk import dag, task

@dag(
        dag_id="first_dag"
)
def first_dag():
    
    @task.python
    def first_task():
        print("Hello World, First DAG")
    
    @task.python
    def second_task():
        print("Hello World, Second DAG")
    
    @task.python
    def third_task():
        print("Hello World, Third DAG> Try to run this DAG in Airflow UI")

    #first_task() >> second_task() >> third_task()
    first = first_task()
    second = second_task()
    third = third_task()

    first >> second >> third

#Instantiating the DAG
first_dag()
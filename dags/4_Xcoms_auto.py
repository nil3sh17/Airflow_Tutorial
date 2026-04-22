from airflow.sdk import dag, task

@dag(
        dag_id="xcom_dag_auto"
)
def xcom_dag_auto():
    
    @task.python
    def first_task():
        print("Hello World, Extracting Data")
        fetched_data = {"name": "John", "age": 30, "city": "New York"}
        return fetched_data
    
    @task.python
    def second_task(data: dict):
        print("Hello World, Transforming Data")
        fetched_data = data['age']
        transformed_data = fetched_data * 2
        transformed_data_dict = {"transformed_age": transformed_data}
        return transformed_data_dict
        #transformed_data2 = {key: str(value).upper() for key, value in data.items()}
        #return transformed_data2
    
    @task.python
    def third_task(data: dict):
        print("Final Task, Loading Data")
        load_data = data['transformed_age']
        print(f"Data to be loaded: {load_data}")
        return f"Data {load_data} loaded successfully!"

    #first_task() >> second_task() >> third_task()
    first = first_task()
    second = second_task(first)
    third = third_task(second)

    first >> second >> third

#Instantiating the DAG
xcom_dag_auto()
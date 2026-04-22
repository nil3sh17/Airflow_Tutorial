# Apache Airflow

## What is Apache Airflow?

Apache Airflow is an open-source workflow orchestration tool used to schedule, manage, and monitor data pipelines.

A data pipeline often includes multiple tasks such as:

- Extracting data from APIs or databases
- Cleaning and transforming data
- Loading data into a warehouse
- Sending notifications after completion

Airflow helps define all of this as a workflow, where tasks are connected with dependencies.

## Why do we need Airflow instead of Cron jobs?

### Problem with Cron jobs

Cron is a basic Unix scheduler used to run scripts at a fixed time.

Example:

```bash
0 2 * * * /home/user/run_etl.sh
```

Limitations of Cron
Cron can schedule jobs, but it is not designed for modern data workflows.

## Issues

### No dependency management

If task B depends on task A, Cron doesn’t handle this well.  
You need to manually script the logic.

### No retry mechanism

If a task fails because of a network issue, Cron just fails silently unless you build custom retry logic.

### Poor logging and monitoring

Cron doesn’t provide a dashboard to visualize failures and successes.

### No workflow visibility

You cannot easily see which tasks succeeded, failed, or are running.

### No backfilling

If a job didn’t run yesterday, Cron won’t automatically rerun for historical dates.

### Hard to scale

Managing many interdependent Cron jobs becomes messy.

## Why Airflow is better

Airflow solves these issues by providing:

- Task dependency management
- Automatic retries
- Logging
- Monitoring via UI
- Backfilling
- Scheduling
- Parallelism
- Extensibility with operators, hooks, sensors

## Example: Cron vs Airflow

### Scenario

Suppose you need to run a daily pipeline:

- Extract sales data from source database
- Transform the data
- Load into Snowflake
- Send email if successful

### In Cron

You might create 4 scripts and somehow chain them manually.  
If step 2 fails, step 3 may still run unless you add custom checks.

### In Airflow

You define tasks with dependencies:

```python
extract >> transform >> load >> notify
```

## Deep Dive into Airflow Architecture

Airflow is made up of several components working together.

### Airflow ensures:
- Step 2 runs only after Step 1 succeeds
- Retries happen if a task fails
- Logs are available
- The UI shows the entire workflow

### The 4 Pillars of Airflow Architecture
1. **Webserver**
2. **Scheduler**
3. **Metadata Database**
4. **Executor**

## 2.1 Webserver

The webserver provides the Airflow UI.

### What it does
- Shows DAGs
- Displays task status
- Allows manual triggering
- Lets users inspect logs
- Gives Graph, Tree, Grid, and Gantt views

### Example
If a task fails, you go to the Airflow UI, click the task instance, and inspect the logs.

## 2.2 Scheduler

The scheduler is the brain of Airflow.

### What it does
- Scans DAG files
- Determines which tasks are ready to run
- Checks schedules
- Creates DAG runs and task instances
- Sends runnable tasks to the executor

### Example
Suppose your DAG runs daily at 1 AM.  
At the scheduled time, the scheduler creates a DAG run and checks which task should run first.

### Important
The scheduler does not directly run the task code in most setups.  
It decides what should run and hands execution to the executor.

## 2.3 Metadata Database

This is the central database where Airflow stores state.

### Stores
- DAG metadata
- Task instance states
- DAG run history
- XCom values
- Users, connections, and configurations
- Scheduling information

### Example
If task `extract_data` succeeded at 2:05 AM today, that state is stored in the metadata database.

### Common databases used
- PostgreSQL
- MySQL
- SQLite is only for basic or local experimentation and is not recommended for production

### Why it matters
Without the metadata database, Airflow cannot track what ran, what failed, what should run next, or what data was shared via XCom.

## 2.4 Executor

The executor determines how tasks are actually executed.

### Popular executors
- `SequentialExecutor`
- `LocalExecutor`
- `CeleryExecutor`
- `KubernetesExecutor`

### SequentialExecutor
- Runs one task at a time
- Mostly for local testing
- Not suitable for production

### LocalExecutor
- Runs tasks in parallel on the same machine
- Good for small to medium setups

### CeleryExecutor
- Distributed execution using Celery workers
- Tasks can run on multiple worker machines
- Good for scalable production systems

### KubernetesExecutor
- Each task can run in its own Kubernetes pod
- Highly scalable and isolated
- Common in cloud-native deployments

### Example of component interaction
Let’s say you have a DAG scheduled daily at 6 AM.

### Flow
- Scheduler scans the DAG file
- Scheduler sees it should run at 6 AM
- Scheduler creates a DAG run
- First task is marked ready
- Executor receives the task
- Worker executes the task
- Status is written to the metadata database
- Webserver reads the metadata database and shows status in the UI

## The DAG File Processor

This is a very important internal concept.

### What is it?
The DAG File Processor is responsible for:
- Continuously scanning the `dags/` folder
- Parsing Python files
- Identifying valid DAG objects
- Serializing and parsing DAG definitions so Airflow can display and schedule them

### Important clarification
Airflow does not run your DAG as a normal script from top to bottom for task execution.  
It parses the DAG file repeatedly to understand workflow structure.

### Why this matters
If you put heavy code at the top level of a DAG file, it will slow down parsing.

### Bad example
```python
data = huge_api_call()  # bad at DAG parse time
```
This is bad because every time Airflow parses the file, that API call runs.

### Good practice
Put runtime logic inside tasks or functions.

## Local Environment Setup

### Why Docker is preferred
In modern projects, Airflow is usually set up with Docker and Docker Compose instead of installing directly on the machine.

### Why?
- Reproducible environment
- Easy dependency management
- Same setup across team members
- Simpler installation of Airflow, database, scheduler, and webserver
- Avoids local Python package conflicts

## Docker basics in Airflow setup

### Docker
Packages the application and its environment in a container.

### Docker Compose
Helps define and run multiple containers together.

For Airflow, you commonly need:
- Webserver container
- Scheduler container
- Database container, such as PostgreSQL
- Possibly worker and Redis containers for `CeleryExecutor`

## Example: Airflow with Docker Compose

A `docker-compose` setup includes:
- `airflow-webserver`
- `airflow-scheduler`
- `postgres`
- `redis`
- `airflow-worker`

This mirrors production-like architecture much better than a simple local install.

## Airflow UI Mastery

The Airflow UI is very important in real jobs and interviews.

### Key UI Views

#### DAGs List View
Shows all DAGs and their overall status.

#### Graph View
Shows tasks as nodes and dependencies as edges.

### Example
```python
extract >> transform >> load
```

#### Tree/Grid View
Shows historical runs and task status across execution dates.

Useful for:
- Seeing patterns of failures
- Checking which dates failed
- Rerunning specific task instances

#### Gantt View
Shows task durations and overlaps.

Useful for:
- Performance analysis
- Identifying long-running bottlenecks
- Spotting opportunities for parallelism

#### Task Logs
Each task instance has logs that show:
- Printed outputs
- Errors
- Retries
- Stack traces

### Debugging through logs
If a Python task fails because of division by zero:
```python
def divide():
    return 10 / 0
```

## Core DAG Components & Coding

### What is a DAG?
DAG stands for **Directed Acyclic Graph**.

#### Directed
Tasks have a direction or order.

#### Acyclic
There must be no loops or cycles.

#### Graph
Represents tasks and dependencies.

### Example
```python
start >> extract >> transform >> load >> end
```
### Important DAG parameters

#### `dag_id`
Unique identifier of the DAG.

#### `start_date`
The logical date from which scheduling begins.

#### `schedule_interval` / `schedule`
Defines how often DAG runs.

Examples:
- `@daily`
- `0 6 * * *`

#### `catchup`
Whether to run missed historical schedules.

#### `default_args`
Used to define common settings like retries, owner, email, and retry delay.

## Operators

Operators define what work gets done.

### `BashOperator`
Used to run shell commands.

## Bitshift operators

- `>>` means “runs before”
- `<<` means “runs after”

### Example
```python
task1 >> task2 >> task3
```

This means:
- `task1` runs first
- Then `task2`
- Then `task3`

### Parallel tasks

#### Example
```
task1 >> [task2, task3] >> task4
```
- `task2` and `task3` run in parallel after `task1`
- `task4` waits for both `task2` and `task3` to finish

### Interview-ready explanation
In Airflow, dependencies are explicitly defined between tasks. Using operators like `>>` and `<<`, we create a DAG structure that ensures tasks execute in the correct order, including sequential and parallel execution patterns.

## Advanced Task Communication & Logic

### Why task communication is needed
Airflow tasks are designed to be isolated and ideally independent. Because of this, if one task generates a value needed by another task, we need a mechanism to share that value.

This is where XCom comes in.

## XCom (Cross-Communication)

XCom allows tasks to exchange small pieces of data.

### Important
XCom is not meant for large datasets like full tables or huge JSON files.

Use it for:
- IDs
- Status flags
- File paths
- Small metadata
- Dates or counts

If a `PythonOperator` returns a value, Airflow can automatically store it in XCom.

XCom is useful for small metadata exchange, but not for passing large data. Large data should be stored externally, such as in S3, a database, or a data lake, and only the reference or path should be passed through XCom.

## Branching in Airflow

Branching allows you to implement conditional logic.

This is useful when pipeline flow depends on:
- File existence
- Row counts
- Validation status
- Business rules

### BranchPythonOperator
This operator chooses which downstream task or tasks should run.

### Example scenario
If sales count is greater than 0:
- Run the processing task

Else:
- Run the `skip_processing` task

### Important behavior
- The function returns the `task_id` of the task to follow
- Tasks on the non-selected branch are marked as skipped


## Scheduling, Time, and “The Change”

This is one of the most important sections for interviews because many people struggle with Airflow scheduling concepts.

## Cron Syntax

Cron expressions define schedules.

### Cron format

```text
* * * * *
| | | | |
| | | | Day of week
| | | Month
| | Day of month
| Hour
Minute
```

### Examples

#### Every day at midnight
`0 0 * * *`

#### Every day at 6 AM
`0 6 * * *`

#### Every Monday at 9 AM
`0 9 * * 1`

#### Every 15 minutes
`*/15 * * * *`

### Airflow schedule examples
- `schedule_interval="@daily"`
- `schedule="0 6 * * *"`

## Logical Date / Execution Date concept

This is one of the most confusing Airflow concepts.

Airflow schedules runs for a time interval, not simply “run now”.

### Example
A daily DAG for `2026-01-10` usually represents the data interval covering that day and may run after the interval ends.

This means Airflow is often processing data for a completed period, not the current live minute.

### Interview insight
Mentioning logical date shows strong understanding.

## Catchup

Catchup means Airflow will create DAG runs for missed intervals from the `start_date` until now.

### Example
If:
- `start_date = Jan 1`
- `schedule = daily`
- `today = Jan 5`
- `catchup = True`

Then Airflow creates runs for:
- Jan 1
- Jan 2
- Jan 3
- Jan 4
- Jan 5, depending on schedule semantics

### If `catchup = False`
It runs only the latest scheduled interval.

## Backfilling

Backfilling means running historical DAG runs intentionally for past dates.

### Use case
Suppose your daily sales pipeline failed for the past 3 days. You can backfill those missed dates.

### Why useful
Data engineering often requires historical reprocessing.

## Idempotency

This is a very important interview concept.

### Definition
A process is idempotent if running it multiple times gives the same safe final result, without causing duplicates or corruption.

### Why needed in Airflow
Tasks can retry, rerun, or be backfilled. If your pipeline is not idempotent, repeated runs can create problems.

### Interview answer on idempotency
Idempotency means a pipeline can be rerun safely without creating duplicate or inconsistent data. This is crucial in Airflow because retries, backfills, and reruns are common. Production-grade pipelines should always be designed to be idempotent.

## Jinja Templating

Airflow supports Jinja templates to inject runtime variables.

### Common variables
- `{{ ds }}` → execution date as `YYYY-MM-DD`
- `{{ ts }}`
- `{{ dag_run }}`
- `{{ params }}`
- `{{ var.value.some_key }}`

### Example use cases
- Printing the logical date for a DAG run
- Writing dynamic SQL filters based on the run date
- Passing runtime parameters into tasks

### Why this is powerful
You can write one DAG that automatically adapts to each execution date.

## Incremental Loads

Instead of reprocessing all historical data every time, incremental loads process only new or changed data.

### Why important
- Faster
- Cheaper
- Scalable
- Production-friendly

## Full load vs Incremental load

### Full load
Every run reloads the entire dataset.

#### Pros
- Simpler logic

#### Cons
- Expensive
- Slow
- Unnecessary for large data

### Incremental load
Only loads delta or new records since the last successful run.

#### Pros
- Efficient
- Scalable

#### Cons
- More logic required

### Example
Suppose the `orders` table has a `last_updated_at` column.

You process only records newer than the previous successful watermark.

Another common approach is to process data per date partition.

```
sql
WHERE order_date = '{{ ds }}'
```

### Interview answer
Incremental loading is a strategy where only new or modified data is processed instead of reloading the full dataset each time. In Airflow, this is commonly combined with templated execution dates and idempotent design.

## Production & Advanced Features

## Event-Driven Architecture

Traditional Airflow pipelines are time-based:
- Run every hour
- Run every day

But sometimes you want to trigger workflows when something happens.

### Examples
- A file lands in S3
- A message arrives in Kafka
- A table receives new data
- An API sends an event

This is event-driven orchestration.

### Why event-driven pipelines are useful
- Lower latency
- No unnecessary polling every few hours
- More responsive systems
- Better alignment with real business events

### Example
Suppose a CSV file is uploaded to an S3 bucket. Instead of running a DAG every hour to check for files, an event or sensor can trigger the DAG only when the file appears.

### Airflow support
Airflow can implement this using:

- Sensors
- Triggering DAGs via API
- External task triggers
- Deferrable operators in modern Airflow

### Interview answer
Event-driven architecture in Airflow means workflows are triggered by actual events rather than fixed schedules. This is useful for low-latency and efficient processing, such as triggering a pipeline when a new file arrives in cloud storage.

## Modular DAGs

In real enterprise systems, DAGs can become huge and hard to maintain if all logic is written in one file.

### Bad pattern
One massive DAG file with:
- All SQL inline
- All Python logic inline
- Repeated code
- Poor readability

### Better pattern: modular DAG design
Break code into:
- Reusable Python modules
- Utility functions
- Config files
- Custom operators or hooks if needed
- Separate task logic from DAG definition

### Benefits
- Maintainability
- Reusability
- Readability
- Easier testing
- Cleaner team collaboration

### Example of modular approach
In the DAG file, you import reusable utilities instead of writing everything directly in the DAG itself.

## Summary

Apache Airflow is a powerful tool for building and managing data pipelines. Key concepts to remember:

- **DAGs** define workflows as tasks with explicit dependencies
- **Operators** determine what work gets done
- **Scheduling** uses cron expressions to define when DAGs run
- **Logical dates** represent data intervals, not execution times
- **XCom** enables small data exchanges between tasks
- **Idempotency** ensures safe reruns and retries
- **Incremental loading** is essential for scalable pipelines
- **Modular design** improves maintainability in production systems

Mastering these concepts prepares you for production Airflow deployments and technical interviews.



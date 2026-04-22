# Airflow

![Notes](./notes.png)

## 1) What is Airflow?
- **Apache Airflow** is an **open-source workflow orchestration framework**.
- It is used to **schedule, manage, and monitor workflows/pipelines**.
- Workflows are defined as code using **DAGs (Directed Acyclic Graphs)**.
### DAG meaning
- **Directed** → tasks have order/direction
- **Acyclic** → no loops/cycles
- **Graph** → tasks connected by dependencies
### In a DAG:
- **Nodes** = tasks
- **Edges** = dependencies
Example:

```python
extract >> transform >> load
```
---

## 2) Why Orchestration is Needed
Orchestration is needed when a workflow is more than a single script and includes:

- **Multiple steps** across systems
    - SQL
    - APIs
    - S3/object storage
    - Spark
    - ML jobs

- **Dependencies**
    - Task B should run only after Task A succeeds

- **Scheduling**
    - hourly / daily / weekly

- **Retries and failure handling**
    - recover gracefully from temporary failures

- **Parallelism**
    - independent tasks can run at the same time

- **Observability**
    - track runs, failures, success, logs, timings

### Example pipeline
1. Load data from SQL/API
2. Store in S3
3. Process using PySpark
4. Repeat on schedule
---

## 3) What Airflow is NOT
### 1. Not a Data Processing Framework
- Airflow should **orchestrate** tools like Spark, dbt, SQL engines, etc.
- It should **not do heavy data processing inside workers**.
### 2. Not a Real-time / Streaming Framework
- Airflow is mainly for **batch** and **scheduled workflows**.
- It is not a streaming engine like Kafka, Flink, or Spark Streaming.
### 3. Not an ETL Tool
- Airflow can manage ETL/ELT workflows,
- but its core purpose is:
    - **coordination**
    - **scheduling**
    - **monitoring**

---

## 4) Why Airflow Instead of a Simple Python Script?
A single script becomes hard to manage when you need:

- multiple tasks
- branching and parallelism
- state tracking
- retries
- backfills
- catchup
- logs and monitoring
- distributed execution
Airflow gives all this as a platform instead of writing custom logic manually.

---

## 5) Why Airflow Instead of Cron Jobs?
### Problem with Cron
Cron is a basic Unix scheduler.

Example:

```
0 2 * * * /home/user/run_etl.sh
```
### Limitations of Cron
#### No dependency management
- Cron cannot naturally manage task A → task B → task C dependencies.
#### No retry mechanism
- If a task fails, you need custom retry handling.
#### Poor logging and monitoring
- No UI/dashboard.
#### No workflow visibility
- Hard to see what succeeded, failed, or is running.
#### No backfilling
- Missed runs are not automatically recreated.
#### Hard to scale
- Many interdependent cron jobs become messy.
---

## 6) Why Airflow is Better than Cron
Airflow provides:

- task dependency management
- automatic retries
- logging
- monitoring via UI
- backfilling
- scheduling
- parallelism
- extensibility using:
    - operators
    - hooks
    - sensors

### Example: Cron vs Airflow
#### Scenario
Daily pipeline:

- Extract sales data
- Transform data
- Load into Snowflake
- Send email notification
#### In Cron
- You may create 4 separate scripts
- Must manually chain them
- If step 2 fails, step 3 may still run unless custom checks are added
#### In Airflow
```
extract >> transform >> load >> notify
```
Airflow ensures:

- correct order
- retries
- visibility
- logs
- monitoring
---

# 7) Core Concepts of Airflow
## DAG
- Directed Acyclic Graph
- Represents the workflow structure
## Task
- A single unit of work in a DAG
## Task Instance
- A specific execution of a task for a given DAG run
## Operator
- A pre-built template for defining a task
Examples:

- PythonOperator
- BashOperator
---

# 8) Core Components & Architecture
Airflow is a distributed system with multiple components.

## Main Components
### 1. Metadata Database
Stores:

- DAG metadata
- DAG runs
- task instances
- task states
- schedules
- retries
- XComs
- users, connections, and configs
Common production DB:

- **Postgres**
---

### 2. DAG File Processor / Parser
- Scans the dags/ folder
- Parses Python DAG files
- Identifies DAG objects
- Registers DAG/task structure
### Important
Parsing should be lightweight.

#### Bad practice
```
data = huge_api_call()
```
This runs during parse time repeatedly.

#### Good practice
Put heavy logic inside task functions.

---

### 3. Web Server
Provides the Airflow UI.

### What it does
- shows DAGs
- shows task status
- allows manual trigger
- allows log inspection
- shows Graph / Grid / Gantt views
---

### 4. Scheduler
The scheduler is the brain of Airflow.

### What it does
- scans DAG files
- checks schedules
- creates DAG runs
- determines which tasks are ready
- sends runnable tasks to the executor
### Important
The scheduler usually does **not directly execute task code**.

---

### 5. Executor & Workers
## Executor
Determines **how and where** tasks run.

## Workers
Actually, execute task code.

### Common Executors
- Sequential Executor
- Local Executor
- Celery Executor
- Kubernetes Executor
Sequential Executor

- one task at a time
- local testing only
Local Executor

- runs tasks in parallel on the same machine
Celery Executor

- distributed execution using workers
- good for production
Kubernetes Executor

- each task can run in its own pod
- scalable and isolated
---

### 6. Triggerer
- Handles **deferred / idle tasks efficiently**
- Useful for waiting tasks:
    - file arrival
    - external event
    - API response

- Prevents wasting worker slots
---

## Architecture Flow Example
For a DAG scheduled daily at 6 AM:

1. Scheduler scans DAG file
2. Scheduler sees DAG should run
3. Scheduler creates DAG run
4. Runnable task instance is created
5. Executor sends task to worker
6. Worker executes task
7. Status is written to the metadata DB
8. Webserver reads the DB and shows UI status
---

# 9) Installation & Setup (Local via Docker)
## Why Docker is Recommended
- easy setup
- reproducible environment
- avoids dependency conflicts
- production-like architecture
- good for Windows using WSL2 + Docker Desktop
## Common Project Structure
-  → DAG Python files /dags
-  → task logs/logs
-  → custom operators/hooks/sensors/plugins
-  → optional config overrides/config
## Docker Compose setup usually includes:
- airflow-webserver
- airflow-scheduler
- postgres
- redis
- airflow-worker
## Common customizations
- disable example DAGs
- map local into the container dags/
- expose Postgres port if needed
---

# 10) Airflow UI Important Views
## DAG List View
- shows all DAGs
## Graph View
- shows tasks and dependencies visually
## Grid View
- shows historical runs and task states across dates
## Gantt View
- shows task durations and overlaps
## Task Logs
- printed output
- errors
- retries
- stack traces
---

# 11) Writing DAGs and Tasks
## Modern TaskFlow API
Airflow encourages:

-  decorator → define a DAG @dag
-  decorator → define Python tasks @task
### Benefits
- cleaner code
- easier task definition
- automatic XCom support through return values
### Key idea
- the DAG function defines workflow structure
- tasks are created by calling decorated task functions
---

## Operators
Bash Operator

- runs shell commands/scripts
Python Operator

- runs a Python callable
- older style but still used
### Task Flow vs Python Operator
-  is the modern style @task
-  is the classic style PythonOperator
---

## Defining Dependencies
### Bitshift operators
-  means upstream to downstream>>
-  means downstream dependency in reverse notation<<
Example:

```
task1 >> task2 >> task3
```
---

## Parallel Tasks
Example:

```
task1 >> [task2, task3] >> task4
```
Meaning:

-  task2 & task3 run in parallel after task1
-  waits for both task4
This is called:

- **fan-out / fan-in**
---

# 12) DAG Versioning
- DAGs can evolve over time
- Airflow reflects updated DAG definitions after deployment
- New runs use the updated DAG definition after deployment
---

# 13) XComs – Task Communication
## What is XCom?
- **XCom = cross-communication**
- Let's tasks exchange **small pieces of data**
- stored in the metadata DB
## Use XCom for:
- IDs
- file paths
- flags
- counts
- small metadata
## Do NOT use XCom for:
- large datasets
- tables
- huge JSON payloads
Store large data externally:

- S3
- DB
- data lake
Pass only references via XCom.

---

## Auto-XCom with TaskFlow
With, the task return value is automatically stored in XCom.

Example concept:

- task A returns a file path
- task B receives that file path as input
---

## Manual XCom Push/Pull
Can be done using the task instance object ().

Useful when:

- custom keys are needed
- multiple values are pushed
- using classic operators
---

# 14) Branching in Airflow
Branching is used for conditional execution.

## Use cases
- file exists or not
- row count > 0
- validation pass/fail
- business rule-based flow
## Branch Python Operator
- returns the to follow task_id
- non-selected branches become **skipped**
---

# 15) Scheduling Concepts
Important scheduling parameters:

## ```
start_date
```

- logical start for scheduling
## ```
end_date
```

- optional stop point
## ```
schedule
```

- defines how often DAG runs happen
## ```
catchup
```

- whether to create missed historical runs from start_date
---

## Scheduling Methods
### 1. Presets
Examples:

- @daily
- @hourly
### 2. Cron Syntax
Format:

```
* * * * *
| | | | |
| | | | Day of week
| | | Month
| | Day of month
| Hour
Minute
```
Examples:

- Every day at midnight: 0 0 * * *
- Every day at 6 AM: 0 6 * * *
- Every Monday at 9 AM: 0 9 * * 1
- Every 15 minutes: */15 * * * *
### 3. Fixed intervals / timed delta-style schedules
- run every 3 days, etc.
### 4. Specific dates / event-driven custom schedules
- for irregular cases
- often handled by manual triggers or custom timetables
---

# 16) Logical Date / Data Interval
This is an important Airflow concept.

Airflow runs are associated with a **logical date / data interval**, not simply “the current moment”.

## Key variables
- data_interval_start
- data_interval_end
### Example
A daily DAG run for often represents processing data for that completed interval.

### Interview point
Airflow usually processes **completed time windows**, not live real-time data.

---

# 17) Catchup and Backfill
## Catchup
If, Airflow creates DAG runs for missed intervals from until now.

Example:

- start_date = Jan 1
- schedule = daily
- Airflow creates runs for all missed dates
## Backfill
Backfill means intentionally rerunning historical dates.

### Use case
- pipeline failed for previous 3 days
- rerun those days
---

# 18) Idempotency
## Definition
A process is **idempotent** if rerunning it gives the same safe final result without duplicates or corruption.

## Why important in Airflow
Because Airflow supports:

- retries
- reruns
- backfills
- catchup
Pipelines must be safe to run multiple times.

### Interview-ready answer
Idempotency means a pipeline can be rerun safely without producing duplicate or inconsistent results. This is critical in Airflow because retries, reruns, and backfills are common.

---

# 19) Incremental Loads
## What is Incremental Loading?
Only process new or changed data instead of full history every run.

## Why important?
- faster
- cheaper
- scalable
- production-friendly
## Full Load vs Incremental Load
### Full Load
- reload all data every time
#### Pros
- simple logic
#### Cons
- expensive
- slow
### Incremental Load
- process only new/changed records
#### Pros
- efficient
- scalable
#### Cons
- requires more logic
## Common methods
- watermark last_updated_at
- date partitions
- data interval-based loads
Example:

```
WHERE order_date = '{{ ds }}'
```
Or use:

- data_interval_start
- data_interval_end
---

# 20) Assets and Data-Driven Scheduling
Modern Airflow versions introduce stronger support for **assets**.

## Mindset shift
From:

- “run every day at 1 AM”
To:

- “run when dataset X is updated”
## Asset examples
- table
- file
- S3 path
- dataset
## Materializing an asset
- upstream DAG produces/updates the dataset
- downstream DAG triggers when that asset is updated
## Benefit
Better alignment with real data availability rather than fixed time schedules

---

# 22) Event-Driven Architecture
Traditional Airflow is time-based, but sometimes workflows should start when an event happens.

## Examples
- file arrives in S3
- Kafka message appears
- API event occurs
- upstream table updated
## Airflow support
- sensors
- API triggers
- external task triggers
- deferrable operators
- assets
## Benefit
- lower latency
- more efficient
- avoids unnecessary polling
---

# 23) DAG-to-DAG Orchestration
## Trigger Dag Run Operator
Used to trigger one DAG from another DAG.

## Use cases
- parent-child workflows
- separate ingestion from processing
- modular pipelines
## Best practice
- keep DAGs independently runnable if possible
- pass parameters carefully
- maintain traceability using run IDs
---

# 24) Modular DAG Design
Avoid one giant DAG file.

## Bad pattern
- all logic inline
- all SQL inline
- repeated code
- poor readability
## Better pattern
Break logic into:

- reusable Python modules
- utility functions
- config files
- custom hooks/operators if needed
## Benefits
- maintainability
- reusability
- readability
- testing
- team collaboration



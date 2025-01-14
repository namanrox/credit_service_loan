# Loan Management
Credit Service designed to facilitate efficient lending by a Loan provider to users
# ER Diagram on how this service can be provided
![ER diagram](https://github.com/user-attachments/assets/ae3a2448-de8e-45d5-971c-a305d2938d4a)
# Installation & Usage
* Clone this repository:
```

https://github.com/namanrox/credit_service_loan.git

```
* Now install all dependencies:
```

$ pip3 install -r requirements.txt

Note: If any conflict occurs, install them separately.

```
1. Migrate the models. Create a migration for the models using the command:
```

>> python manage.py makemigrations

Then run the migration to create the necessary tables in the database using the command:

>> python manage.py migrate

```
2. Install and configure Celery and RabbitMQ using the following commands:
```

Install Celery and RabbitMQ using the following commands:

>> pip install celery
>> sudo apt-get install rabbitmq-server

Configure Celery to use RabbitMQ as the message broker by adding the following code to the settings.py file:

>> CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
>> CELERY_RESULT_BACKEND = 'rpc://'`

```
3. Start the Django server, Celery worker, and RabbitMQ server using the command:
```

Start the Django server using the command:
>> python manage.py runserver

Start the Celery worker using the command:
>> celery -A loan_api_project worker -l info

Start the RabbitMQ server using the command:
>> rabbitmq-server

```
Now, we can test the project by using the API endpoints to register users, apply for loans, and make payments.

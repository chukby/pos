## POS APP

 A point of Sale application built for a mini mart with Django


 ## Setup guide

 ### STEP 1

 Set up a virtual environment using the venv module and activate the environment

 ### STEP 2 

 Run the command 

 ``` pip install -r requirements.txt ```


 Then set your ```.env``` file  as follows and replace the values with your postgres database details

 ``` 
DB_NAME=pos_system
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

```

### STEP 3

Run makemigrations if you have made any adjustments to models and commit to the changes to the database byrun migrate s follows

``` python manage.py makemigrations ```

then next run 

``` python manage.py migrate ```

### STEP 4

Run this command to createsuper

``` python manage.py createsuperuser ```

follow the prompt to create the superuser


### STEP 5 

Run this command to run the development server

``` python manage.py runserver ```

NB: You should install a production server like gunicorn when you want to deploy the code


Go to http://localhost:8000 to view your pos application
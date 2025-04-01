# HU-Edge-Python
Assignment for HU-Edge-Python Track.

The split_it_project folder contains all the configurations file related to the project and the split_it_app folder contains the actual code logic.

There are 4 Models used.
1. User
2. Event
3. Occasion
4. Expenditure Summary

There are 7 views used.
1. UserApi - to lists all the users available.
2. RegisterApi - to help with a new user registration.
3. LoginApi - it authenticates a user and logs them in.
4. OccasionApi - it is used to create and view the occasion created.
5. EventApi - it is used to create an event, tag it to occasion (optional) and calculate split of every participant involved in the occasion.
6. ExpenseApi - it is used when the user wishes to settle their expense.
7. OccasionSummaryApi - it generates the occasion expenditure summary. 

All the models have their corresponnding serializers.

The swagger can be viewed using this: http://127.0.0.1:8000/split_it_app/docs/

The schema can be downloaded using this: http://127.0.0.1:8000/split_it_app/schema/

To run the application, make sure you are inside the parent split_it_project directory.

##### To run the application, use the command: 
python manage.py runserver

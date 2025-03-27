The projet7 repository contains a django application / credit scoring API that predicts whether or not a bank client will repay his or her loans on time.

The api_credit folder contains several files that build the structure and design of the django application as well as its backend logic. The critical ones are:

- views.py : backend of application, contains most of the logic
- urls.py : links the django views (functions) to the respective templates where they are being used
- models.py : where database tables are created

The project folder contains, among others, the settings.py file where all environment variables are set.

The mlruns folder and its 3 subdirectories contains information about the trained algorithms; metrics and artifacts logged using mlflow.

The requirements.txt file contains all packages / dependencies used in the virtual environment.

The Ferreira_Frederic_5_test_API_032025.py file was created to test the API by sending remote HTTP requests using a Streamlit UI

Finally, the tests folder contains the test_functions.py file where some tests were performed using pytest.






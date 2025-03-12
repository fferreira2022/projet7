This projet7 repository contains a django application and credit scoring API that predicts whether or not a bank client will repay his or her loans on time. 

The api_credit folder contains several files that build the structure and design of the django application as well as its backend logic. The critical ones are: 
 - views.py : backend of application, contains most of the logic
 - urls.py : links the django views (functions) to the respective templates where they are being used
 - models.py : where database tables are created

The project folder contains, among others, the settings.py file where all environment variables are set.

The mlruns folder and its 3 subdirectories contains information about the trained algorithms; metrics and artifacts logged using mlflow, and the models themselves.

The best_models directory only contains the 3 best models saved with the joblib module.

The requirements.txt file contains all packages / dependencies used in the virtual environment.

The Ferreira_Frederic_1_notebook_modelisation is a notebook where the exploratory data analysis, feature engineering and training of models were performed.

Finally, the tests folder contains the test_functions.py file where some tests were performed using pytest.






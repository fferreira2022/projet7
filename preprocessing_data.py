def preprocessing_data(df_train, df_test, vars_to_use, features_to_log_transform):
    df_train_copy = df_train.copy()
    df_test_copy = df_test.copy()
    # create a label encoder object
    le = LabelEncoder()
    # Iterate through the columns
    for col in df_train_copy:
        if df_train_copy[col].dtype == 'object':
            # If 2 or fewer unique categories
            if len(list(df_train_copy[col].unique())) <= 2:
                # Train on the training data
                le.fit(df_train_copy[col])
                # Transform both training and testing data
                df_train_copy[col] = le.transform(df_train_copy[col])
                df_test_copy[col] = le.transform(df_test_copy[col])
            else:
                df_train_copy = pd.get_dummies(df_train_copy)
                df_test_copy = pd.get_dummies(df_test_copy)
                
    # extract the target
    train_labels = df_train_copy['TARGET']
    # Align the training and testing data, keep only columns present in both dataframes
    df_train_copy, df_test_copy = df_train_copy.align(df_test_copy, join = 'inner', axis = 1)
               
    # Add the target back in
    df_train_copy['TARGET'] = train_labels
    
    dfs = [df_train_copy, df_test_copy]
    for df in dfs:
        # Create an anomalous flag column
        df['DAYS_EMPLOYED_ANOM'] = df["DAYS_EMPLOYED"] == 365243
        # Replace the anomalous values with nan
        df['DAYS_EMPLOYED'].replace({365243: np.nan}, inplace = True)
    
    # take absolute value of DAYS_BIRTHand divide by 365 to get age at the time of application
    df_train_copy['DAYS_BIRTH'] = abs(df_train_copy['DAYS_BIRTH'])
    df_test_copy['DAYS_BIRTH'] = abs(df_test_copy['DAYS_BIRTH'])
  
    # create variables in df_train_copy
    df_train_copy['CREDIT_INCOME_PERCENT'] = df_train_copy['AMT_CREDIT'] / df_train_copy['AMT_INCOME_TOTAL']
    df_train_copy['ANNUITY_INCOME_PERCENT'] = df_train_copy['AMT_ANNUITY'] / df_train_copy['AMT_INCOME_TOTAL']
    df_train_copy['CREDIT_TERM'] = df_train_copy['AMT_ANNUITY'] / df_train_copy['AMT_CREDIT']
    df_train_copy['DAYS_EMPLOYED_PERCENT'] = df_train_copy['DAYS_EMPLOYED'] / df_train_copy['DAYS_BIRTH']
    
    # create variables in df_test_copy
    df_test_copy['CREDIT_INCOME_PERCENT'] = df_test_copy['AMT_CREDIT'] / df_test_copy['AMT_INCOME_TOTAL']
    df_test_copy['ANNUITY_INCOME_PERCENT'] = df_test_copy['AMT_ANNUITY'] / df_test_copy['AMT_INCOME_TOTAL']
    df_test_copy['CREDIT_TERM'] = df_test_copy['AMT_ANNUITY'] / df_test_copy['AMT_CREDIT']
    df_test_copy['DAYS_EMPLOYED_PERCENT'] = df_test_copy['DAYS_EMPLOYED'] / df_test_copy['DAYS_BIRTH']
    
    # let's pick some of the variables most correlated with the target 
    # and we will aslo keep the client id for practicality sake
    df_train_copy = df_train_copy[vars_to_use]
    df_test_copy = df_test_copy[vars_to_use[1:]]  # since the test set lacks a target variable we remove it from vars_model1
    
    # remove missing values
    df_train_no_nan = df_train_copy.dropna()
    df_test_no_nan = df_test_copy.dropna()
    
    # take only a fraction of df_train_model1_no_nan so as to reduce training time
    df_train_sampled = df_train_no_nan.groupby('TARGET', group_keys=False).apply(lambda x: x.sample(frac=0.10, random_state=66))
    
    # take the absolute value of DAYS_EMPLOYED and DAYS_EMPLOYED_PERCENT to avoid errors caused by log of values <= 0
    df_train_sampled['DAYS_EMPLOYED'] = abs(df_train_sampled['DAYS_EMPLOYED'])
    df_train_sampled['DAYS_EMPLOYED_PERCENT'] = abs(df_train_sampled['DAYS_EMPLOYED_PERCENT'])
    
    # same for the test set
    df_test_no_nan['DAYS_EMPLOYED'] = abs(df_test_no_nan['DAYS_EMPLOYED'])
    df_test_no_nan['DAYS_EMPLOYED_PERCENT'] = abs(df_test_no_nan['DAYS_EMPLOYED_PERCENT'])
    
    # # Apply log transformation before building the ColumnTransformer
    # features_to_log_transform = ['DAYS_EMPLOYED', 'CREDIT_INCOME_PERCENT', 'AMT_INCOME_TOTAL', 'AMT_ANNUITY']

    df_train_log = df_train_sampled.copy()
    df_test_log = df_test_no_nan.copy()

    df_train_log[features_to_log_transform] = df_train_sampled[features_to_log_transform].apply(np.log1p)
    df_test_log[features_to_log_transform] = df_test_no_nan[features_to_log_transform].apply(np.log1p)

    # Add suffix '_log' to the name of log-transformed columns
    df_train_log.rename(columns={col: f"{col}_log" for col in features_to_log_transform}, inplace=True)
    df_test_log.rename(columns={col: f"{col}_log" for col in features_to_log_transform}, inplace=True)
   
   # drop redundant column
    df_train_log = df_train_log.drop(columns=['CODE_GENDER_F'])
    df_test_log = df_test_log.drop(columns=['CODE_GENDER_F'])
    
    return df_train_log, df_test_log
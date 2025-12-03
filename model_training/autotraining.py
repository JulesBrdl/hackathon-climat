import os
import pandas as pd
import time
import datetime as dt
from joblib import dump, load

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from sklearn.ensemble import RandomForestClassifier


name_for_this_training = "test" # doit etre sous ce format de string : "must_be_attached"

# path = '../data/'
path_perso = '../data_perso/'
data_full_file = 'feature_engineering_V1_2004_2024.parquet'

data = pd.read_parquet(os.path.join(path_perso,data_full_file))

cols = ['prAdjust', 'tasAdjust', 'prWeek', 'prMonth', 'tasWeekAverage',
       'tasWeekMax', 'tasWeekMin', 'tasMonthAverage']
target_col = 'fire'

#### LOGS AND FILES :  
date_str = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logs_file = os.path.join(path_perso, "log_fire_classification.csv")
rf_grid_search_results_file = os.path.join(path_perso,"gs_files", f"rf_grid_search_{name_for_this_training}_{date_str}.csv")
rf_model_file = os.path.join(path_perso,"model_files", f"fire_classification_rf_{name_for_this_training}_{date_str}.joblib")

######################################## PARAMS MODEL RF ########################################

#### GRID ####
GRID_RF = {
    'n_estimators': [150,300],  #100, 500, 1000, 1500
    'max_features': [None], # "log2","sqrt"
    'max_depth': [5,10],  # 35,50,100, None
    'min_samples_leaf': [2], # 3,10,15,20
    'min_samples_split' : [5], # 2,10,20,30
    'class_weight': ["balanced"]
}

##################################################################################################

def split_train_test_data(cols, target_col, df):    
    df = df.copy()

    zeros = df[df["fire"] == 0]
    ones  = df[df["fire"] == 1]

    # Sample 80% of the zero-rows to DROP we have way too much data
    zeros_to_keep = zeros.sample(frac=0.20) # , random_state=42

    df_balanced = pd.concat([zeros_to_keep, ones], axis=0).sample(frac=1) # , random_state=42
    df_balanced.index = df_balanced.index.set_levels(pd.to_datetime(df_balanced.index.levels[0]),level=0)

    time_index = df_balanced.index.get_level_values("time")

    # Train: 
    train_df = df_balanced[(time_index >= "2005-01-01") & (time_index < "2018-01-01")]
    # Test: time ≥ 2018
    test_df = df_balanced[time_index >= "2018-01-01"]

    X_train = train_df[cols]
    X_test = test_df[cols]
    y_train = train_df[target_col]
    y_test = test_df[target_col]
    print('split_train_test_data Done !')

    return X_train, X_test, y_train, y_test


def get_and_print_metrics(y_pred, y_test):
    # Évaluer les performances du modèle
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)

    print(f"accuracy : {accuracy}")
    print(f"f1 : {f1}")
    print(f"precision : {precision}")
    print(f"recall : {recall}")
    print(f"roc_auc : {roc_auc}")

    return accuracy, f1, precision, recall, roc_auc

def save_logs(log_data, logs_file):
    # Save les logs donnés sous forme de dict
    log_df = pd.DataFrame(log_data)
    log_df.to_csv(logs_file, sep=";", index=False, mode='a', header=not os.path.exists(logs_file))
    print("Logs saved")
    return 

##################### RandomForestClassifier #####################

def rf_model_training(X_train, X_test, y_train, y_test, grid, name_for_this_training, grid_search_results_file, model_file, logs_file):
    """
    Entrainement (GridSearchCV) de modele RandomForestClassifier
    """
    time_start = time.time()
    date_str = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("Starting GridSearchCV for RF")

    ### GRIDSEARCH ###
    grid_search = GridSearchCV(estimator=RandomForestClassifier(), param_grid=grid, cv=5, scoring='f1', n_jobs=-1, verbose=3, return_train_score=True)
    grid_search.fit(X_train, y_train)

    best_params = grid_search.best_params_
    best_model = grid_search.best_estimator_
    grid_search_results = pd.DataFrame(grid_search.cv_results_).sort_values(by="rank_test_score")
    grid_search_results.to_csv(grid_search_results_file, index=False, sep=";")
    print('GridSearchCV Done !')

    ### TRAINING BEST MODEL ###
    model = RandomForestClassifier(
        max_depth=best_params['max_depth'],
        max_features=best_params['max_features'],
        min_samples_leaf=best_params['min_samples_leaf'],
        min_samples_split=best_params['min_samples_split'],
        n_estimators=best_params['n_estimators'],
        class_weight=best_params["class_weight"]
    )
    model.fit(X_train, y_train)

    ### PREDICTIONS ###
    y_pred = model.predict(X_test)
    y_pred_train = model.predict(X_train)
    # Évaluer les performances du modèle
    print("Meilleurs paramètres : ", best_params)
    print("Test metrics : ")
    accuracy, f1, precision, recall, roc_auc = get_and_print_metrics(y_pred, y_test)
    print("Train metrics : ")
    accuracy_train, f1_train, precision_train, recall_train, roc_auc_train = get_and_print_metrics(y_pred_train, y_train)

    time_end = time.time()

    ### SAVING AND LOGS ###
    model_type = type(model).__name__
    assert model_type == "RandomForestClassifier", "Wrong model type (not RandomForestClassifier)"
    # Save model
    dump(model, model_file, compress=3)
    # Calculer la taille du modèle
    model_size = os.path.getsize(model_file)
    print("Model saved locally")

    train_size = len(y_train)
    test_size = len(y_test)
    training_duration = int(time_end - time_start)
    # logs
    log_data = {
        "model_type" : ["rf"],
        "train_date" : [date_str],
        "train_size": [train_size],
        "test_size": [test_size],
        "training_duration": [training_duration],
        "accuracy": [accuracy],
        "f1": [f1],
        "precision": [precision],
        "recall": [recall],
        "roc_auc": [roc_auc],
        "accuracy_train": [accuracy_train],
        "f1_train": [f1_train],
        "precision_train": [precision_train],
        "recall_train": [recall_train],
        "roc_auc_train": [roc_auc_train],
        "best_params" : [best_params],
        "model_size": [model_size],
        "model_training_name": [name_for_this_training],
        "model_grid": [grid]
    }
    save_logs(log_data, logs_file)

    return model, grid_search_results, log_data


def model_training():

    print('Starting ',name_for_this_training)

    X_train, X_test, y_train, y_test = split_train_test_data(cols, target_col, data)
    rf_model_training(X_train, X_test, y_train, y_test, GRID_RF, name_for_this_training, rf_grid_search_results_file, rf_model_file, logs_file)

    print("RF Training done.")


def main():
    try:
        model_training()

    except Exception as exc:
        print(f'Error during model training : {exc}')
        return "fail"


if __name__ == '__main__':
    main()
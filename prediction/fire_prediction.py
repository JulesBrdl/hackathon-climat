import os
import pandas as pd
import joblib


def predict_solar_production(data_to_predict):

    # Indiquer le nom et la date du modèle choisi pour faire les prédictions 
    name_for_this_training = ""
    date_str = ""

    model_path = os.path.join('../data_perso/',"model_files", f"fire_classification_rf_{name_for_this_training}_{date_str}.joblib")
    model = joblib.load(model_path)

    model_type = type(model).__name__
    assert model_type == "RandomForestClassifier", "Wrong model type"


    # Choix des colonnes utilisées par le modèle
    x_cols = ['prAdjust', 'tasAdjust', 'prWeek', 'prMonth', 'tasWeekAverage',
              'tasWeekMax', 'tasWeekMin', 'tasMonthAverage']

    X = data_to_predict[x_cols]
    predictions = model.predict(X)

    # predictions = pd.DataFrame({'solar_kwh': predictions}, index=X.index)
    # predictions["solar_kwh"] = predictions["solar_kwh"].round(1)
    # predictions.index = predictions.index.tz_convert("UTC").strftime('%Y-%m-%d %H:%M:%S')
    # predictions.index.name = 'date'
    # predictions.reset_index(inplace=True, drop=False)
    
    # print("Predictions : ", predictions)
    return predictions
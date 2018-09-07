import os
import time
import pandas as pd
import numpy as np
import json


def get_acum(pm1, pm2, Temp_df):

    Temp_df['PM1'] = Temp_df['Average'].rolling(pm1).mean()
    Temp_df['PM2'] = Temp_df['Average'].rolling(pm2).mean()
    Temp_df.dropna(inplace=True)
    Temp_df['Posicion'] = np.where(Temp_df['PM1'] > Temp_df['PM2'], 1, -1)
    Temp_df['Retornos'] = np.log(
        Temp_df['Average']/Temp_df['Average'].shift(1))
    Temp_df.dropna(inplace=True)
    Temp_df['Estrategia'] = Temp_df['Retornos']*Temp_df['Posicion'].shift(1)
    Temp_df.dropna(inplace=True)
    # Temp_df['Retacum'] = Temp_df['Retornos'].cumsum().apply(np.exp)
    Temp_df['Estracum'] = Temp_df['Estrategia'].cumsum().apply(np.exp)

    return Temp_df['Estracum'].tail(1).copy()


def get_df():

    the_path = os.getcwd()
    data_path = os.path.join(the_path, '../data/processed-data/')
    file_name = 'BTC-USDT-processed.csv'
    file_path = data_path + file_name
    df = pd.read_csv(file_path, index_col='Date')

    df.drop(df.columns[df.columns.str.contains(
        'unnamed', case=False)], axis=1, inplace=True)
    df.index = pd.to_datetime(df.index)

    return df.last('31D').copy()


def surrounding_peek(PM1, Steps_PM1=1, Steps_PM2=2):

    Best_Stra = 0
    Best_PM1 = 0
    Best_PM2 = 0
    Start_PM1 = PM1-10
    Last_PM1 = PM1+10
    Start_PM2 = 1
    Last_PM2 = 1440

    df_M = get_df()

    for pm1 in np.arange(Start_PM1, Last_PM1, Steps_PM1):
        for pm2 in np.arange(Start_PM2, Last_PM2, Steps_PM2):
            if (pm1 < pm2) and (pm1/pm2 > 0.35) and ((pm1+2) < pm2):
                Val_Stra = get_acum(pm1, pm2, df_M.copy())
                if (Val_Stra[0] > Best_Stra):
                    Best_Stra = Val_Stra[0]
                    Best_PM1 = pm1
                    Best_PM2 = pm2
        print('\r{:.2f}%'.format(((pm1-Start_PM1+1)/21)*100), end='')
    print('\r100%\n')
    return [Best_PM1, Best_PM2, Best_Stra]


def adjust_param():

    with open('parameters.json') as f:
        params = json.load(f)

    actual_pm1 = params['PM1']
    actual_pm2 = params['PM2']

    df = get_df()

    actual_score = get_acum(actual_pm1, actual_pm2, df.copy())[0]
    print('Actual score: {}'.format(actual_score))
    params['Score'] = float(actual_score)
    with open('parameters.json', 'w') as outfile:
        json.dump(params, outfile)
    print('Searching surroundings...')
    surrounding = surrounding_peek(actual_pm1)

    if (surrounding[2] > actual_score):

        print('Better parameters found!')
        print('New Values\nPM1: {}\nPM2: {}\nScore: {}'.format(
            surrounding[0], surrounding[1], surrounding[2]))
        params['PM1'] = int(surrounding[0])
        params['PM2'] = int(surrounding[1])
        params['Score'] = float(surrounding[2])
        params['Last-PM1'] = int(actual_pm1)
        params['Last-PM2'] = int(actual_pm2)

        print('Adjusting parameters...')
        with open('parameters.json', 'w') as outfile:
            json.dump(params, outfile)
    else:
        print('Actual parameters are fine')


print('Starting Parameters Lookup')
adjust_param()
print('Done')

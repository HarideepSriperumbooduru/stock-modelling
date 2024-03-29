import datetime

import config

import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

df = pd.read_csv('action_history_full_data.csv')

df1 = df.groupby('model_name').agg({'return_val': 'mean'})
df1 = df1.sort_values(by=['return_val'], ascending=False)
print(" Following is the average return value for any action taken under different models")
print()
print(df1)
print("**************************************************************************")
print()

df2 = df.groupby(by=['model_name', 'tic']).agg({'return_val': 'mean'})

print(" Following is the average return value for any action taken under different models for individual stocks")
print()
print(df2)
print("**************************************************************************")
print()

df5 = df.groupby(by=['model_name', 'sector']).agg({'return_val': 'sum'})
df5 = df5['return_val'].groupby('model_name', group_keys=False)
print(" Top 3 performing sectors under different models in terms of total returns ")
print()
print(df5.nlargest(3))
print("**************************************************************************")
print()


def timed_return_ratio(t, tic, m_name, flag):
    d = t * 30
    start_date = config.TEST_START_DATE
    temp = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = temp + timedelta(days=d)
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    df3 = df.loc[df['model_name'] == m_name]
    df3 = df3.loc[df['tic'] == tic]
    df3 = df3.loc[df3['transaction_date'] >= start_date]
    df3 = df3.loc[df3['transaction_date'] <= end_date]
    # df3 = df3.head(d) if d <= len(df3) else df3
    if flag:
        return df3['return_val'].mean()
    else:

        try:
            cumulative_return = df3['return_val'].sum()
            price_lst = list(df3['share_price'])
            # print('len of price list is ', len(price_lst))
            initial_price = price_lst[0]
            final_price = price_lst[-1]
            df3 = df3.loc[df3['action'] == 'buy']
            invested_amount = df3['amount_for_action'].sum()
            idle_return = (invested_amount // initial_price) * final_price
        except Exception as e:
            print("There has been an exception")
            print(e)
            print('tic is ', tic, ' and the model is ', m_name)
            print('start date is ', start_date, ' and the end date is ', end_date)
            print(df3)
            return None, None
        return cumulative_return, idle_return


returns_dict = {}
if 'tic' not in returns_dict:
    returns_dict['tic'] = []

if 'time_period_in_months' not in returns_dict:
    returns_dict['time_period_in_months'] = []

if 'model' not in returns_dict:
    returns_dict['model'] = []

if 'avg return' not in returns_dict:
    returns_dict['avg return'] = []

if 'total return' not in returns_dict:
    returns_dict['total return'] = []

if 'idle return' not in returns_dict:
    returns_dict['idle return'] = []
time_list = [1, 3, 6, 12, 18, 24]
models = ['sac', 'td3', 'ppo', 'ddpg']
for model in models:
    for tic in config.TICKERS_LIST:
        for t in time_list:
            avg_return = timed_return_ratio(t, tic, model, True)
            total_return, idle_return_in_t = timed_return_ratio(t, tic, model, False)

            if total_return and idle_return_in_t:
                returns_dict['tic'].append(tic)
                returns_dict['model'].append(model)
                returns_dict['time_period_in_months'].append(t)
                returns_dict['avg return'].append(avg_return)
                returns_dict['total return'].append(total_return)
                returns_dict['idle return'].append(idle_return_in_t)
    #         print()
    #         print(f"average return value from {tic} for last {t} months under {model} model is {avg_return}")
    #         print(f'Total return value from {tic} for last {t} months under {model} model is {total_return}')
    #         print()
    #     print()
    #
    # print("************************************************************************************")
    # print()
returns_dict_df = pd.DataFrame(returns_dict)
print(returns_dict_df)
print()
print()
print('*************************************************************************')
returns_dict_df.to_csv('returns_analysis.csv')

# top ten performing stocks
models = ['sac', 'td3', 'ppo', 'ddpg']
for model in models:
    for t in [1, 6, 12]:
        df4 = returns_dict_df.loc[returns_dict_df['time_period_in_months'] == t]
        df4 = df4.loc[df4['model'] == model]
        df4 = df4.sort_values(by=['total return'], ascending=False)

        print('top ten performing stocks under ', model, ' for the past ', t, ' months are')
        print()
        print(df4.head(10))
        print()

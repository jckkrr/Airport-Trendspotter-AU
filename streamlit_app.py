############## Constistuent.Online #################
####### Code-free analysis for curious folk. ######

### An application for ...

## streamlit run "C:\Users\Jack\Documents\Python_projects\streamlit_apps\airport_trendspotter\streamlit_app.py"

### --------------------------------------- IMPORTS 

import datetime
import json
import math
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import re
import requests
import streamlit as st

import customChartDefaultStyling

pd.set_option('display.max_columns', None)

### 
headers = {
    "content-type": "application/json"
}

css = 'body, html, p, h1, .st-emotion-cache-1104ytp h1, [class*="css"] {font-family: "Inter", sans-serif;}'
st.markdown( f'<style>{css}</style>' , unsafe_allow_html= True)

### ---------------------------------------- FUNCTIONS   

#import project_functions 

def make_monthMatrix(value_column):

    icaos = df_month['ICAO'].unique()
    df_month_matrix = pd.DataFrame()

    for icao in icaos:
        dfx = df_month.loc[(df_month['ICAO'] == icao)][['month', value_column]].set_index('month', append = False)
        dfx.index.name = None
        dfx = dfx.rename(columns = {value_column: icao}).T   
        df_month_matrix = pd.concat([df_month_matrix, dfx])
        
    df_month_matrix = df_month_matrix
    df_month_matrix.index.name = 'ICAO'
    return df_month_matrix
    
def make_describe(df):
        
    def mini_dm(value_column):
        
        df_mini_dm = df_month.groupby(by = ['ICAO'])[value_column].describe()
        df_mini_dm = df_mini_dm[[x for x in df_mini_dm.columns if '%' not in x]]
        
        df_mini_dm.insert(2, 'median', df_month.groupby(by = ['ICAO'])[value_column].median())
        df_mini_dm['diff_minmax'] = df_mini_dm['max'] - df_mini_dm['min']
        df_mini_dm['diff_minmax_%'] = round(df_mini_dm['diff_minmax'] / df_mini_dm['min'] * 100, 2)

        
        if value_column == 'total_traffic':
            
            def get_month_data(icao, bookend_month):
                v = df_month.loc[(df_month['ICAO'] == icao) & (df_month['month'] == bookend_month), 'total_traffic']
                v = v.values[0] if len(v) > 0 else 0
                return v

            df_mini_dm['start_month_traffic'] = df_mini_dm.index.copy()
            df_mini_dm['start_month_traffic'] = df_mini_dm['start_month_traffic'].apply(lambda icao: get_month_data(icao, start_month))
            df_mini_dm['end_month_traffic'] = df_mini_dm.index.copy()
            df_mini_dm['end_month_traffic'] = df_mini_dm['end_month_traffic'].apply(lambda icao: get_month_data(icao, end_month))    
            df_mini_dm['diff_period'] = df_mini_dm['end_month_traffic'] - df_mini_dm['start_month_traffic']
            df_mini_dm['diff_period_%'] = df_mini_dm['diff_period'] / df_mini_dm['start_month_traffic'] * 100
            df_mini_dm['diff_period_%'] = round(df_mini_dm['diff_period_%'], 2)

        elif value_column == 'normalised_traffic':
            df_mini_dm.columns = [x + '_norm' if x != 'count' else x for x in df_mini_dm.columns ]

        return df_mini_dm.reset_index()
    
    df_mini_1 = mini_dm('total_traffic')
    df_mini_2 = mini_dm('normalised_traffic')
    df_describe = df_mini_1.merge(df_mini_2, on = ['ICAO', 'count'], how = 'outer')
    
    ### Add the total number flights at the airport across entire timeframe of the dataset
    df_alltime = df.groupby(by = ['ICAO'])['total_traffic'].sum().to_frame().rename(columns = {'total_traffic': 'alltime_traffic'})
    df_alltime['alltime_traffic'] = df_alltime['alltime_traffic'].astype(int)
    df_describe = df_alltime.merge(df_describe, on = 'ICAO', how = 'outer')
        
    ### Add details from the ICAO dataframe, including into the index
    df_describe = df_describe.merge(df_icao, on = 'ICAO', how = 'outer')
    df_describe = df_describe.set_index(['ICAO', 'airport', 'state'], append=False)
    
    return df_describe.fillna(0)



def plotData(airport, icao, bool_normalise, bool_daily, bool_monthly):
        
    fig = go.Figure()

    palette = {
        0: 'rgb(67, 121, 242)', 
    }
    line_color = palette[0]

    
    def plotIcao(df, x_col, icao):
        
        df_plot = df.copy()
        df_plot = df_plot[df_plot['ICAO'] == icao]           
        df_plot['total_normalised'] = df_plot['total_traffic'] / df_plot['total_traffic'].max()    
        
        y_col = 'total_traffic' if bool_normalise == False else 'total_normalised'
        
        if x_col == 'date':
                    
            fig.add_trace(
                go.Bar(
                    name = 'daily',
                    x = df_plot[x_col],
                    y = df_plot[y_col],
                    marker =  dict(
                        color = 'black',
                    )
                )
            )
    
        elif x_col == 'month':
                    
            fig.add_trace(
                go.Scatter(
                    name = 'monthly',
                    x = df_plot[x_col],
                    y = df_plot[y_col],
                    line_shape='hvh',
                    marker =  dict(
                        color = line_color, 
                        size  = 10
                    )
                )
            )
            
    fig.update_layout(bargap = 0)
    
    if bool_daily:
        plotIcao(df, 'date', icao)
    if bool_monthly:
        plotIcao(df_month, 'month', icao)
    
    
    customChartDefaultStyling.styling(fig)
    fig.update_layout(height=500, width=1200)
    norm_text = '' if bool_normalise == False else ' (normalised)'
    fig.update_layout(title=dict(text=f"<b>{returned_airport} ({icao})</b> | Total airport traffic per month (and day){norm_text}"))
    fig.update_layout(xaxis=dict(title=dict(text=None)))
    fig.update_layout(yaxis=dict(title=dict(text=f"Departures + Arrivals{norm_text}")))

    #fig.show()
    
    ### Display   
    st.plotly_chart(fig, use_container_width=True)

    
    
    
    
    
### ========================================= PRELOAD

icao_file = 'C:/Users/Jack/Documents/Python_projects/streamlit_apps/airport_trendspotter/iata-icao.csv'
icao_file = 'https://raw.githubusercontent.com/jckkrr/Airport-Trendspotter-AU/refs/heads/main/iata-icao.csv'
df_icao = pd.read_csv(icao_file)
df_icao = df_icao.loc[df_icao['country_code'] == 'AU']
df_icao = df_icao.rename(columns = {'icao': 'ICAO' ,'region_name': 'state'})
df_icao['airport'] = df_icao['airport'].apply(lambda x: x.replace('Airport','').replace('International','').replace('  ',' ').strip())
states_abbrs = {'New South Wales': 'NSW', 'Victoria': 'VIC', 'Queensland': 'QLD', 'Western Australia': 'WA', 'South Australia': 'SA', 'Tasmania': 'TAS', 'Australian Capital Territory': 'ACT', 'Northern Territory': 'NT'}
df_icao['state'] = df_icao['state'].apply(lambda x: states_abbrs[x])
df_icao = df_icao[['ICAO', 'airport', 'state', 'latitude', 'longitude']]
    
    
### --------------------------------------- RUN 

st.markdown("**Open Investigation Tools** | [constituent.online](%s)" % 'http://www.constituent.online')
    
st.title('Airport Trendspotter (AU)')
st.write('Uncover trends in aviation data.')


### 

latest_data = 'C:/Users/Jack/Documents/Python_projects/streamlit_apps/airport_trendspotter/latest_data.csv'
latest_data = 'https://raw.githubusercontent.com/jckkrr/Airport-Trendspotter-AU/refs/heads/main/latest_data.csv'
df = pd.read_csv(latest_data)
df.insert(2, 'month', df['timecode'].apply(lambda x: datetime.datetime.utcfromtimestamp(x).strftime('%Y-%m')))

months = list(df.month.unique())
month_names = {'01': 'January', '02': 'Febuary', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
col1, col2 = st.columns(2)
with col1:
    start_month = st.selectbox('Select starting month', (reversed(months)))
    start_month_year, start_month_name = start_month.split('-')
    start_month_name = month_names[start_month_name]
with col2:
    end_month = st.selectbox('Select ending month', (months))
    end_month_year, end_month_name = end_month.split('-')
    end_month_name = month_names[end_month_name]
if start_month > end_month:
    st.write("You can't start after you end.")
df = df.loc[(df['month'] >= start_month) & (df
                                            ['month'] <= end_month)]
st.write(f'This analysis for the period {start_month_name} {start_month_year} to {end_month_name} {end_month_year} inclusive.')


###

df_month = df.groupby(['ICAO', 'month'])['total_traffic'].sum().to_frame().reset_index()
dfx = df_month.groupby(['ICAO'])['total_traffic'].max().to_frame().rename(columns = {'total_traffic': 'max_icao'})
df_month = df_month.merge(dfx, on = 'ICAO', how = 'outer')
df_month['normalised_traffic'] = df_month['total_traffic'] / df_month['max_icao']
df_month = df_month.drop(['max_icao'], axis=1)
df_month.tail()

df_describe = make_describe(df_month)

##

alltime_values = df_describe['alltime_traffic'].values
lo, hi = int(alltime_values.min()), int(alltime_values.max())
alltime_range = st.slider("Assessing airports with total aircraft traffic for the period between:", lo, hi, (lo, hi))

st.write('States:')
col1, col2 = st.columns(2)
chosen_states = []
with col1:
    
    for state in list(states_abbrs.values())[0:4]:
        option_state = st.checkbox(state, True)
        if option_state == True:
            chosen_states.append(state) 

with col2:
    
    for state in list(states_abbrs.values())[4:]:
        option_state = st.checkbox(state, True)
        if option_state == True:
            chosen_states.append(state)    

st.write()
            
df_describe = df_describe.sort_values(by = ['max'], ascending = False)
df_describe = df_describe.loc[(df_describe['alltime_traffic'] >= alltime_range[0]) & (df_describe['alltime_traffic'] <= alltime_range[1])]
df_describe = df_describe[df_describe.index.get_level_values('state').isin(chosen_states)]




def print_analysis(col, bool_ascending, descriptor):
    dfx = df_describe.sort_values(by = col, ascending = bool_ascending)[0:3]
    returned_airport = dfx.index[0][1]
    returned_icao = dfx.index[0][0]
    st.write(f'\nThe airport with the {descriptor} in that period was {returned_airport} ({returned_icao}), with {dfx.iloc[0][col]}')
    st.dataframe(dfx[[col]])
    
    return returned_airport, returned_icao

st.write('')
col1, col2 = st.columns(2)
with col1:
    selectable_columns = ['alltime_traffic', 'min', 'max', 'diff_minmax', 'diff_minmax_%', 'start_month_traffic', 'end_month_traffic', 'diff_period', 'diff_period_%']
    selected_column = st.selectbox('Select column to assess', (selectable_columns))

with col2:
    select_ascending = [False, True]
    selected_ascending = st.selectbox('From low to high?', (select_ascending))
    
st.write(' ')
returned_airport, returned_icao = print_analysis(selected_column, selected_ascending, f'most/least {selected_column}')

plotData(returned_airport, returned_icao, False, True, True)

st.markdown("""<style>.small-font {font-size:8px !important; padding: 0; margin: 0; line-height: 6px;}</style>""", unsafe_allow_html=True)
st.markdown(f'<p class="small-font">(Note: ....)</p>', unsafe_allow_html=True)

st.write('---')
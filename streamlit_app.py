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

#import customChartDefaultStyling

pd.set_option('display.max_columns', None)

### 
headers = {
    "content-type": "application/json"
}

css = 'body, html, p, h1, .st-emotion-cache-1104ytp h1, [class*="css"] {font-family: "Inter", sans-serif;}'
st.markdown( f'<style>{css}</style>' , unsafe_allow_html= True)

### ---------------------------------------- FUNCTIONS   

#import project_functions 

def make_monthmatrix(value_column):

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
    
def make_descriptionMatrix(df, value_column):

    df_month_dm = df_month.groupby(by = ['ICAO'])[value_column].describe()

    df_month_dm.insert(2, 'median', df_month.groupby(by = ['ICAO'])[value_column].median())
    df_month_dm['diff'] = df_month_dm['max'] - df_month_dm['min']
    df_month_dm['range'] = df_month_dm['75%'] - df_month_dm['25%']

    ### Add the total number flights at the airport across entire timeframe of the dataset
    df_alltime = df.groupby(by = ['ICAO'])['total_traffic'].sum().to_frame().rename(columns = {'total_traffic': 'alltime_traffic'})
    df_month_dm = df_month_dm.merge(df_alltime, on = 'ICAO', how = 'outer')

    ### Add value of all months
    df_matrix = make_monthmatrix(value_column)
    df_month_dm = df_month_dm.merge(df_matrix, on = 'ICAO', how = 'outer')

    ### Add details from the ICAO dataframe, including into the index
    #df_month_dm = df_month_dm.merge(df_icao, on = 'ICAO', how = 'outer')
    #df_month_dm = df_month_dm.set_index(['ICAO', 'airport', 'state', 'latitude', 'longitude'], append=False)
    
    return df_month_dm.fillna(0).sort_values(by = 'alltime_traffic', ascending = False)


### ========================================= PRELOAD

#df_icao = pd.read_csv('iata-icao.csv')
#df_icao = df_icao.loc[df_icao['country_code'] == 'AU']
#df_icao = df_icao[['icao', 'airport', 'region_name', 'latitude', 'longitude']].rename(columns = {'icao': 'ICAO' ,'region_name': 'state'})

    
    
### --------------------------------------- RUN 

st.markdown("**Open Investigation Tools** | [constituent.online](%s)" % 'http://www.constituent.online')
    
st.title('Airport Trendspotter (AU)')
st.write('Uncover trends in aviation data.')


import os
c = os.getcwd() 
print(c)

### !!! Need to make load directly
uploaded_file = st.file_uploader("Upload file here &#x2935;", type={"csv"})

uploaded_file = pd.read_csv('latest_data.csv')

if  uploaded_file:

    df = pd.read_csv(uploaded_file)
    df.insert(2, 'month', df['timecode'].apply(lambda x: datetime.datetime.utcfromtimestamp(x).strftime('%Y-%m')))

    months = list(df.month.unique())

    st.write('')
    
    col1, col2 = st.columns(2)

    with col1:
        start_month = st.selectbox('Select starting month', (reversed(months)))

    with col2:
        end_month = st.selectbox('Select ending month', (months))
        
    if start_month > end_month:
        st.write("You can't start after you end.")
    
    df = df.loc[(df['month'] >= start_month) & (df['month'] <= end_month)]
        
    #st.write(df.shape)
    #st.write('---')
    
    df_month = df.groupby(['ICAO', 'month'])['total_traffic'].sum().to_frame().reset_index()
    dfx = df_month.groupby(['ICAO'])['total_traffic'].max().to_frame().rename(columns = {'total_traffic': 'max_icao'})
    df_month = df_month.merge(dfx, on = 'ICAO', how = 'outer')
    df_month['normalised_traffic'] = df_month['total_traffic'] / df_month['max_icao']
    df_month = df_month.drop(['max_icao'], axis=1)
    df_month.tail()

    #st.dataframe(df_month)
    #st.write(df_month.shape)
    #st.write('---')
    
    value_column = 'normalised_traffic'
    df_month_dm = make_descriptionMatrix(df_month, value_column)
    
    st.dataframe(df_month_dm)
    st.markdown("""<style>.small-font {font-size:8px !important; padding: 0; margin: 0; line-height: 6px;}</style>""", unsafe_allow_html=True)
    st.markdown(f'<p class="small-font">(Note: most data is proportionally normalised to 1.)</p>', unsafe_allow_html=True)
    st.write(df_month_dm.shape)
    
    st.write('---')
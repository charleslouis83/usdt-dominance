import os
import streamlit as st
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

st.title('USDT Dominance Signal Dashboard')

signals_path = os.path.join(DATA_DIR, 'signals_summary.csv')
class_path = os.path.join(DATA_DIR, 'classification_summary.csv')
backtest_path = os.path.join(DATA_DIR, 'backtest_results.csv')

if not os.path.exists(signals_path):
    st.warning('No signals data found.')
    st.stop()

signals = pd.read_csv(signals_path)
classes = pd.read_csv(class_path) if os.path.exists(class_path) else pd.DataFrame()
backtest = pd.read_csv(backtest_path) if os.path.exists(backtest_path) else pd.DataFrame()

symbols = sorted(signals['symbol'].unique())
timeframes = sorted(signals['timeframe'].unique())

symbol = st.selectbox('Symbol', symbols)
timeframe = st.selectbox('Timeframe', timeframes)

filtered = signals[(signals['symbol'] == symbol) & (signals['timeframe'] == timeframe)]
st.subheader('Correlation Signals')
st.write(filtered)

if not classes.empty:
    st.subheader('Classified Signals')
    st.write(classes[(classes['symbol'] == symbol) & (classes['timeframe'] == timeframe)])

if not backtest.empty:
    st.subheader('Backtest Results')
    st.write(backtest[backtest['symbol'] == symbol])

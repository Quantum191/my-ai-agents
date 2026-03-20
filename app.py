import streamlit as st
from utils.gpu_temp import get_gpu_temp
from utils.cpu_usage import get_cpu_usage
import pandas as pd
import time

# Set page title
st.title("Modern Web GUI Dashboard")

# Metric cards for GPU Temp and CPU Usage
gpu_temp = get_gpu_temp()
cpu_usage = get_cpu_usage()

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="GPU Temperature", value=f"{gpu_temp}°C")
    with col2:
        st.metric(label="CPU Usage", value=f"{cpu_usage}%")

# Line charts for GPU Temp and CPU Usage history
st.subheader("History of GPU Temperature and CPU Usage")
gpu_history = pd.read_csv('data/gpu_history.csv')
cpu_history = pd.read_csv('data/cpu_history.csv')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(gpu_history.set_index('timestamp'))
    with col2:
        st.line_chart(cpu_history.set_index('timestamp'))

# Function to update the history data
def update_history():
    gpu_temp = get_gpu_temp()
    cpu_usage = get_cpu_usage()
    
    # Append new data to CSV files
    with open('data/gpu_history.csv', 'a') as f:
        f.write(f"{time.time()},{gpu_temp}\n")
    with open('data/cpu_history.csv', 'a') as f:
        f.write(f"{time.time()},{cpu_usage}\n")

# Streamlit refresh cycle
while True:
    update_history()
    time.sleep(2)
import os
import pandas as pd

DATA_DIR = "data"

def load_data():
    """සියලුම දත්ත ගොනු ආරක්ෂාකාරීව පූරණය කිරීම"""
    try:
        users_df = pd.read_csv(os.path.join(DATA_DIR, "users.csv")) if os.path.exists(os.path.join(DATA_DIR, "users.csv")) else None
        results_df = pd.read_csv(os.path.join(DATA_DIR, "exam_results.csv")) if os.path.exists(os.path.join(DATA_DIR, "exam_results.csv")) else None
        master_df = pd.read_csv(os.path.join(DATA_DIR, "piriven_master.csv")) if os.path.exists(os.path.join(DATA_DIR, "piriven_master.csv")) else None
        aip_df = pd.read_csv(os.path.join(DATA_DIR, "aip_financial.csv")) if os.path.exists(os.path.join(DATA_DIR, "aip_financial.csv")) else None
        peqi_df = pd.read_csv(os.path.join(DATA_DIR, "peqi_standards.csv")) if os.path.exists(os.path.join(DATA_DIR, "peqi_standards.csv")) else None
        
        return users_df, results_df, master_df, aip_df, peqi_df
    except Exception as e:
        print(f"Database Error: {e}")
        return None, None, None, None, None
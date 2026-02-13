import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def handle_ovrflw(df, integer=False):
    """
    Convert OVRFLW strings present in data to an integer which corresponds to the maximum fluorescence readable by the instrument used.
    Note that this is a place holder value and should be processed accordingly. 
    In other words, artificially replacing OVRFLW values with an integer does not supplement real data. 
    It is recommended to re-run the experiment at a different gain setting to get accurate fluorescence measurements at all time points. 
    However, this makes downstream data handling easier. 

    Parameters:
        df (pd.DataFrame): DataFrame containing optical density or fluroescence time-course data
        integer (int): optional argument to specify what to replace OVRFLW cells with

    Returns:
        pd.DataFrame: DataFrame with OVRFLW cells replaced with NA or a specified integer
    """
    for j,col in enumerate(df.columns):
        if j > 1:
            for i in df.index:
                if(df.iloc[i,j]=="OVRFLW"):
                    if integer != False:
                        df.iloc[i,j] = integer 
                    else:
                        df.iloc[i,j] = pd.NA
    return df


def index_to_time(df):
    """
    Set the index of a dataframe to the time of measurement

    Parameters:
        df (pd.DataFrame): DataFrame with a column "Time" which has a time stamp for each measurement in hh:mm:ss format
    
    Returns:
        pd.DataFrame: DataFrame with the index set to an equivalent time for each row. 
    """
    hours_elapsed = []
    df = df.dropna()

    for time in df.loc[:,"Time"]:
        hours, minutes, seconds = time.hour, time.minute, time.second
        duration = timedelta(days=0,hours=hours,minutes=minutes,seconds=seconds)
        total_hours = duration.total_seconds() / 3600
        hours_elapsed.append(total_hours)
    df["hours elapsed"] = hours_elapsed

    df.set_index("hours elapsed", inplace=True)

    return df



def normalize_by_OD(df_od, df_fl):
    """
    Normalizes fluorescence time-course data by optical density, allowing well-to-well comparisons.

    Parameters:
        df_od (pd.DataFrame): DataFrame with time-course optical density data
        df_fl (pd.DataFrame): DataFrame with time-course fluorescence data with the exact same rows and columns as df_od

    Returns:
        pd.DataFrame: DataFrame with optical density-normalized fluorescence for each column. 
    """
    df_norm = df_fl.iloc[:,2:]/df_od.iloc[:,2:]
    return df_norm


def rename_sample_columns(df, rename_map):
    """
    Rename the columns of a DataFrame according to a mapping dictionary.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with original well names as columns.
        rename_map (dict): Mapping of original well names to desired names.
    
    Returns:
        pd.DataFrame: DataFrame with renamed columns.
    """
    return df.rename(columns=rename_map)


def average_replicates(df, conditions):
    """
    Average replicate columns based on the renamed condition names.
    
    Parameters:
        df (pd.DataFrame): DataFrame with column names set to sample names.
        rename_map (dict): Mapping of original well names to condition names.
    
    Returns:
        pd.DataFrame: DataFrame with averaged columns for each condition.
    """
    # Extract unique condition names
    conditions = set(conditions)
    df_avg = pd.DataFrame(index=df.index)

    for cond in conditions:
        # Select all columns that start with this condition name
        replicate_cols = [col for col in df.columns if col.startswith(cond)]
        if replicate_cols:
            df_avg[cond] = df[replicate_cols].mean(axis=1)
    
    return df_avg


def rename_and_average(df, rename_map, conditions):
    """
    Rename the columns of a DataFrame according to a mapping dictionary then average replicate columns based on the renamed condition names.

    Parameters: 
        df (pd.DataFrame): DataFrame with original well names as columns
        rename_map (dict): Mapping of original well names to condition/sample names

    Returns:
        pd.DataFrame: DataFrame with averaged columns for each specified condition.
    """
    # Rename first
    df_renamed = df.rename(columns=rename_map)
    conditions = set(conditions)
    df_avg = pd.DataFrame(index=df.index)
    for cond in conditions:
        replicate_cols = [col for col in df_renamed.columns if col.startswith(cond)]
        if replicate_cols:
            df_avg[cond] = df_renamed[replicate_cols].mean(axis=1)
    return df_avg


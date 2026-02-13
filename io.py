import pandas as pd
import openpyxl as op

def load_xlsx(file_path, sheet_name):
    """
    Reads in time-course well plate data as an .xlsx file. 

    Parameters:
        file_path: local path to the desired .xlsx file
        sheet_name: name of sheet containing relevant data

    Returns:
        pd.DataFrame: DataFrame containing the available data from the specified sheet of an Excel file 
    """

    workbook = op.load_workbook(file_path)
    ws = workbook[sheet_name]
    data = pd.DataFrame(ws.values)
    workbook.close()
    data.columns = data.iloc[0]
    data = data[1:].reset_index(drop=True)
    return data
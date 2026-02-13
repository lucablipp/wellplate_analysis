
import pandas as pd
import numpy as np
import scipy.stats as ss
import matplotlib.pyplot as plt
import os

def rfu_to_mefl(df, fluor_conc_uM, well_volume_uL, fluorescein_wells, background_well=False):
    """
    Converts column values from relative fluorescence units (RFUs) to molecules of equivalent fluorescein (MEFL) using 
    a fluorescein calibration curve. The protocol to make a fluorescein calibration curve in your well plates can be 
    found here: https://static.igem.org/mediawiki/2019/e/ed/Plate_Reader_Fluorescence_v3.pdf

    Parameters:
        df (pd.DataFrame): DataFrame with time-course fluorescence measurements of sample wells with original well names
        fluorescein_wells: list of columns names associated with wells that had the fluorescein calibration curve
        background_well: default is False, otherwise is the column name of the well without any fluroescein (e.g. 200 uL of PBS)
        fluor_conc_uM: list of fluorescein concentration in micromolar
        well_volume_uL: volume in the fluorescein calibration wells in microliters

    Returns: 
        pd.DataFrame: DataFrame with columns converted to MEFL
    """
    # convert from micromolar to number of fluorescein molecules 
    well_volume = well_volume_uL * 10**-6
    avogadro = 6.022*(10**23)
    fluor_conc_uM = np.array(fluor_conc_uM)
    fluor_molecules = fluor_conc_uM * well_volume * avogadro

    # extract relative fluorescence units from dataframe associated with the above fluorescein concentrations
    rfus = list(df[fluorescein_wells].mean().values)
    
    # Normalize to background (an empty well)
    if background_well != False:
        rfus = rfus - df[background_well].mean()

    # Linear regression
    LR = ss.linregress(x=rfus, y=fluor_molecules)
    intercept = LR.intercept
    slope = LR.slope
    r_squared = LR.rvalue**2

    df_MEFL = df.copy()
    for col in df_MEFL.columns:
        if col.startswith('A') or col.startswith('B') or col.startswith('C') or col.startswith('D') or col.startswith('E') or col.startswith('F') or col.startswith('G') or col.startswith('H'):
            df_MEFL.loc[:,col] = (df.loc[:,col]*slope) + intercept
    
    return df_MEFL, rfus, fluor_molecules, slope, intercept, r_squared


def plot_calibration(rfus, fluor_molecules, slope, intercept, r_squared, output_folder, filename):
    """
    Plots the RFU to MEFL conversion function created within this module's rfu_to_mefl function. 
    It is recommended to perform a linear regression using rfu_to_mefl, then use the output of that function as part of the input to this function. 

    Parameters:
        rfus (list): List of RFU values measured by the well plate reader for wells containing the fluorescein calibration curve - this is the second variable, a list, returned by rfu_to_mefl
        fluor_molecules (list): List of molecules of equivalent fluorescein obtained by converting from micromolar fluorescein to number of molecules - this is the third variable, a list, returned by rfu_to_mefl
        slope: Slope of the linear regression from RFU to MEFL - this is the fourth variable returned by rfu_to_mefl
        intercept: Intercept of the linear regression from RFU to MEFL - this is the fifth variable returned by rfu_to_mefl
        r_squared: R-squared of the linear regression from RFU to MEFL - this is the sixth variable returned by rfu_to_mefl
        output_folder: path to output folder for figure

    Returns:
        A plot
    """
    plt.figure(figsize=(8,6))
    plt.scatter(rfus, fluor_molecules, color='blue')
    plt.axline(xy1=[0,intercept], slope=slope, color='black', alpha=0.7)
    plt.xlabel('Relative fluorescence units (RFU)')
    plt.ylabel('Molecules of equivalent fluorescein (MEFL)')
    plt.title('RFU to MEFL Linear Regression')
    textstr = f"Slope = {slope:.2e}\nIntercept = {intercept:.2e}\nR² = {r_squared:.6f}"
    plt.gca().text(
    0.05, 0.95,
    textstr,
    transform=plt.gca().transAxes,
    fontsize=10,
    verticalalignment='top')
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, filename))
    plt.show()
    plt.close()


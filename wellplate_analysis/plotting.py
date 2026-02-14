import matplotlib.pyplot as plt
import os

def plot_columns(df, columns, title, units, output_folder, filename="file_name.png", colors=None, labels=None ):
    """
    Plots the specified columns from a time-course microwell plate experiment as line graphs. 

    Parameters:
        df (pd.DataFrame): DataFrame with sample-specific column names, may contain the following measurements:
            1. optical density (OD)
            2. relative fluorescence units (RFU)
            3. normalized relative fluorescence units (RFU/OD)
            4. molecules of equivalent fluorescein (MEFL)
            5. normalized molecules of equivalent fluorescein (MEFL/OD)
        columns (list): Sample-specific column names which can be found in the above DataFrame
        labels (list): Strings with which to label the plotted curves
        title (string): Title of the plot
        units (string): Units of the values plotted from the above DataFrame
        output_folder: path to output folder for figure
        filename (string): name of file for the figure

    Returns:
        This function does not return a variable, rather it creates a figure (png)
    """
    if labels is None:
        labels = columns
    if colors is None:
        import matplotlib.cm as cm
        colors = cm.tab10.colors[:len(columns)]

    plt.figure(figsize=(8,6))
    for col, color, label in zip(columns, colors, labels):
        plt.plot(df.index, df.loc[:,col], color=color, label=label, linewidth=1.2, alpha=1)
    plt.title(title)
    plt.xlabel("Time (hours)")
    plt.ylabel(units)
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, filename))
    plt.show()
    plt.close()

    return(df)

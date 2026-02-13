import yaml
import os
import logging

from .io import load_xlsx
from .processing import handle_ovrflw, index_to_time, normalize_by_OD, rename_sample_columns, average_replicates 
from .calibration import rfu_to_mefl, plot_calibration
from .plotting import plot_columns

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline(config_path: str) -> dict:
    """
    Run full well plate analysis pipeline from a YAML config file.
    Plots normalized MEFL (MEFL/OD600) over time for the specified plotting samples in a YAML config file.  
    """
    # Load config file
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    required_sections = ["file_path", "sheets", "rename_map", "plotting"]
    for section in required_sections:
        if section not in config:
            raise KeyError(f"Missing required config section: {section}")


    file_path = config["file_path"]
    output_folder = config.get("output_folder", "results")
    os.makedirs(output_folder, exist_ok=True)

    # Load data sheets for optical density (OD) and fluorescence (RFU) time-course data
    df_od600 = load_xlsx(file_path, config["sheets"]["od600"])
    df_sfGFP = load_xlsx(file_path, config["sheets"]["fluorescence"])

    if not df_od600.index.equals(df_sfGFP.index):
        raise ValueError("OD600 and fluorescence time axes do not match.")

    logging.info("Data imported.")

    # clean fluorescence data
    replacement = config.get("clean", {}).get("replacement", False)
    df_sfGFP = handle_ovrflw(df_sfGFP, integer=replacement)

    logging.info("Fluorescence data cleaned.")

    # set index to fraction of hour
    df_od600 = index_to_time(df_od600)
    df_sfGFP.index = df_od600.index

    logging.info("Time indices set.")

    # convert from RFU to MEFL if calibration provided
    calibration_cfg = config.get("calibration", None)

    if calibration_cfg:
        fluor_wells = calibration_cfg["fluorescein_calibration_wells"]
        background = calibration_cfg.get("background_well", False)
        fluor_conc_uM = calibration_cfg["fluorescein_micromolar_concentration"]
        well_volume = calibration_cfg["microliters_in_wells"]

        df_MEFL, RFU, MEFL, Slope, Intercept, R_squared = rfu_to_mefl(
            df_sfGFP, fluor_conc_uM, well_volume, fluor_wells, background
            )
        df_MEFL.to_csv(os.path.join(output_folder, "MEFL.csv"))
        logging.info(f"MEFL data saved to {output_folder}/MEFL.csv")

        conversion_file = calibration_cfg["calibration_plot"]

        plot_calibration(RFU, MEFL, Slope, Intercept, R_squared, output_folder, conversion_file)

        logging.info("Calibration complete.")

    else:
        df_MEFL = None
        Slope = Intercept = R_squared = None
        logging.info("No calibration performed; using raw RFU values.")

    # Rename the sample columns
    rename_map = config["rename_map"]
    df_od600 = rename_sample_columns(df_od600, rename_map)
    df_sfGFP = rename_sample_columns(df_sfGFP, rename_map)
    if df_MEFL is not None:
        df_MEFL = rename_sample_columns(df_MEFL, rename_map)

    logging.info("Samples named.")

    # Normalize RFU and MEFL data by optical density
    df_norm_sfGFP = normalize_by_OD(df_od600, df_sfGFP)
    logging.info("RFU normalized by optical density.")

    if df_MEFL is not None:
        df_norm_MEFL = normalize_by_OD(df_od600, df_MEFL)
        logging.info("MEFL normalized by optical density.")

        # locally save normalized MEFL data as CSV files
        df_norm_MEFL.to_csv(os.path.join(output_folder, "normalized_MEFL_replicates.csv"))
        logging.info(f"normalized MEFL data saved to {output_folder}/normalized_MEFL_replicates.csv")

    # Create dataframe of averages of technical replicates for fluorescence time-course measurements
    df_od600_avg = None
    df_sfGFP_avg = None
    df_norm_sfGFP_avg = None
    df_MEFL_avg = None
    df_norm_MEFL_avg = None

    conditions = config.get("conditions", False)
    if conditions:
        df_od600_avg = average_replicates(df_od600, conditions)
        df_od600_avg.to_csv(os.path.join(output_folder, "OD_replicate_averages.csv"))
        logging.info(f"Averaged OD600 replicate data saved to {output_folder}/OD_replicate_averages.csv")
        
        df_sfGFP_avg = average_replicates(df_sfGFP, conditions)
        df_sfGFP_avg.to_csv(os.path.join(output_folder, "RFU_replicate_averages.csv"))
        logging.info(f"Averaged RFU replicate data saved to {output_folder}/RFU_replicate_averages.csv")

        df_norm_sfGFP_avg = average_replicates(df_norm_sfGFP, conditions)
        df_norm_sfGFP_avg.to_csv(os.path.join(output_folder, "normalized_RFU_replicate_averages.csv"))
        logging.info(f"Averaged normalized RFU replicate data saved to {output_folder}/normalized_RFU_replicate_averages.csv")

        if df_MEFL is not None:
            df_MEFL_avg = average_replicates(df_MEFL, conditions)
            df_MEFL_avg.to_csv(os.path.join(output_folder, "MEFL_replicate_averages.csv"))
            logging.info(f"Averaged MEFL replicate data saved to {output_folder}/MEFL_replicate_averages.csv")


        if df_norm_MEFL is not None:
            df_norm_MEFL_avg = average_replicates(df_norm_MEFL, conditions)
            df_norm_MEFL_avg.to_csv(os.path.join(output_folder, "normalized_MEFL_replicate_averages.csv"))
            logging.info(f"Averaged normalized MEFL replicate data saved to {output_folder}/normalized_MEFL_replicate_averages.csv")
        
        logging.info("Technical replicates averaged.")
    
    # Plot
    df_map = {
        "normalized MEFL average": df_norm_MEFL_avg,
        "normalized MEFL replicates": df_norm_MEFL,
        "MEFL average": df_MEFL_avg,
        "MEFL replicates": df_MEFL,
        "normalized RFU average": df_norm_sfGFP_avg,
        "normalized RFU replicates": df_norm_sfGFP,
        "RFU average": df_sfGFP_avg,
        "RFU replicates": df_sfGFP,
        "OD average": df_od600_avg,
        "OD replicates": df_od600
    }

    plot_configs = config.get("plotting", {}).get("plots",[])

    for plot_cfg in plot_configs:
        source = plot_cfg["source"]
        df_to_plot = df_map.get(source)
        if df_to_plot is None:
            raise ValueError(f"Plot source '{source}' requested but data not available")

        columns = plot_cfg["columns"]
        missing = [c for c in columns if c not in df_to_plot.columns]
        if missing:
            raise ValueError(
                f"Columns {missing} not found in dataframe for plot '{plot_cfg['name']}'"
            )
        
        plot_columns(
            df = df_to_plot,
            columns = columns,
            colors = plot_cfg.get("colors", None),
            labels = plot_cfg.get("labels", None),
            title = plot_cfg["title"],
            units = plot_cfg["units"],
            output_folder = output_folder,
            filename = plot_cfg["filename"]
            )

    logging.info("Requested data plotted.")
    logging.info("Pipeline completed successfully.")

    return {
    "normalized_MEFL_replicates": df_norm_MEFL,
    "normalized_MEFL_average": df_norm_MEFL_avg,
    "calibration": {
        "slope": Slope,
        "intercept": Intercept,
        "r_squared": R_squared
    }
    }
    
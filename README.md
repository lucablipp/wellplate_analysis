# wellplate_analysis
Well Plate Fluorescence Analysis

A modular, config-driven Python package for analyzing time-course microwell plate fluroescence data. 

This pipeline:
1. Imports Excel (.xlsx) well plate data
2. Cleans overflow values
3. Converts from RFU to MEFL using fluorescein calibration (optional)
4. Normalized fluroescence by optical density
5. Averages technical replicates (optional)
6. Generates publication-quality plots
7. Exports processed CSV files

Designed for reproducible fluorescence analysis workflows. 

## Installation

Clone the repository:

```bash
git clone https://github.com/lucablipp/wellplate_analysis.git
cd wellplate_analysis
```

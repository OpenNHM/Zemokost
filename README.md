# ZEMOKOST

ZEMOKOST is a hydrological precipitation–runoff model developed at the Institute for Natural Hazards of the Federal Research Centre for Forests (BFW) in Austria.
It is used for hazard zone planning and is based on detailed catchment and terrain data.

### ZEMOKOST Model

**ZEMOKOST (V2.0.1)** is implemented in Microsoft Excel with VBA macros.
The model enables the simulation of precipitation–runoff processes within a structured and user-guided workflow.

This repository provides:

- ZEMOKOST model (German and English)
- ZEMOKOST [user manual](zemokost_manual_de.md) (German)
- ZEMOKOST [user manual en](zemokost_user_manual.md)  (English)

### WLV pyQGIS Tool

To simplify the preparation of input data for the ZEMOKOST model, the 'WLV_pyqgis_ZEMOKOST' was developed.
The Python script **'WLV_pyqgis_ZEMOKOST'** automates the processing of geodata required by ZEMOKOST and generates the necessary catchment, flow path, and channel parameters.

The script is designed for use within the QGIS environment and utilizes WhiteboxTools to perform hydrological and geostatistical calculations.

This repository also includes:

- The WLV pyqgis preparation script
- The documentation for the preparation script: [Detailed documentation](toolbox_zemokost_de.md) (German)
- The documentation for the preparation script: [Detailed documentation](toolbox_zemokost_en.md) (English)


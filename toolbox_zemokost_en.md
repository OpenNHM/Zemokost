# Toolbox 'WLV_pyqgis_ZEMOKOST' 1.5.0
<!--
<style>
/* === USER MANUAL STANDARD STYLING === */

/* Schriftart und Basis */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* Überschriften-Hierarchie */
h1 { 
  font-size: 28px; 
  color: #2c3e50; 
  border-bottom: 3px solid #3498db; 
  padding-bottom: 10px;
  margin: 30px 0 20px 0;
}

h2 { 
  font-size: 22px; 
  color: #1f393b; 
  border-bottom: 1px solid #bdc3c7;
  padding-bottom: 5px;
  margin: 25px 0 15px 0;
}

h3 { 
  font-size: 18px; 
  color: #1f393b; 
  margin: 20px 0 12px 0;
}

h4 { 
  font-size: 16px; 
  color: #1f393b;
  margin: 15px 0 10px 0;
}

/* Text und Absätze */
p { 
  line-height: 1.7;
  margin-bottom: 16px;
  text-align: justify;
}

/* Listen (optimal für Anleitungen) */
ul, ol { 
  line-height: 1.6;
  margin: 15px 0;
  padding-left: 25px;
}

li {
  margin-bottom: 8px;
}

/* Verschachtelte Listen */
ul ul, ol ol {
  margin: 8px 0;
}

/* Tabellen (wichtig für Parameter) */
table { 
  border-collapse: collapse; 
  width: 100%;
  margin: 20px 0;
  font-size: 13px;
}

th, td { 
  border: 1px solid #ddd; 
  padding: 12px 8px;
  text-align: left;
}

th { 
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

/* Code und technische Begriffe */
code {
  background-color: #f1f2f6;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

/* Hervorhebungen */
strong { color: #2c3e50; }
em { color: #7f8c8d; }

/* Workflow-Pfeile und Navigation */
blockquote {
  border-left: 4px solid #3498db;
  margin: 20px 0;
  padding: 10px 20px;
  background-color: #f8f9fa;
  font-style: italic;
  font-size: 14px;
}

/* Trennlinien */
hr {
  border: none;
  border-top: 2px solid #ecf0f1;
  margin: 30px 0;
}

</style>
-->

### Table of Contents
- [Input Data](#input-data)
- [Tool Calculation Steps](#tool-calculation-steps)
- [OUTPUT](#output)


---
> Currently, the toolbox is available in **German only**. See the list below for parameter translations.
Note: The exported CSV is provided in German only. However, since only the data itself is copied and no textual labels are required, the values **can be directly transferred** to the English ZEMOKOST version in the worksheet “catchment-definition”.
**Attention: ZEMOKOST uses a comma (,) as the decimal separator.**

| German                  | English               | Description                                             |
|-------------------------|---------------------|---------------------------------------------------------|
| TEZG                    | Sub-basin            | Identifier of the sub-basin                             |
| K.O.                    | j.in      | Inflow point of the junction                             |
| K.U.                    | j.out     | Outflow point of the junction                            |
| Bezeichnung/Ergaenzung  | Name / Description   | Name or description of the sub-basin                    |
| Flaeche                 | Area                 | Area of the sub-basin [km²]                             |
| F-Laenge                | Flow Length          | Surface flow path length [m]                             |
| F-Neigung               | Flow Slope           | Average slope of the sub-basin                            |
| Nat. Ret.               | Natural Retention    | Retention percentage [%]                                  |
| Basisabfl.              | Baseflow             | Baseflow [m³/s]                                          |
| AKL                     | SRC | Surface runoff class                                     |
| RKL                     | RCC| Soil roughness coefficient                               |
| ZAF                     | IFF     | Interflow factor (classes 1–7)                           |
| ZAA                     | IFP     | Portion of interflow [%]                               |
| G-Laenge                | Channel Length       | Length of the main channel [m]                           |
| G-Neigung               | Channel Slope        | Slope of the main channel                                 |
| d90                     |  d90       | Characteristic grain diameter (d90) [m]                 |

Thus, the CSV provides an (almost) complete overview of all input data required for the rainfall-runoff model ZEMOKOST. The parameters are organized in the output file so that they can be directly transferred to the ZEMOKOST input interface via copy-paste.

# Manual for Python Script 'WLV_pyqgis_ZEMOKOST'


ZEMOKOST is a hydrological rainfall-runoff model developed at the Institute of Natural Hazards of the Federal Research Centre for Forests (BFW), which is used in Austria for hazard zone planning and is based on detailed catchment and terrain data.

The Python script **'WLV_pyqgis_ZEMOKOST'** was developed to automatically prepare the geodata required for ZEMOKOST and to provide the relevant catchment, flow path, and channel parameters in a results file. It was developed for use in the QGIS GIS environment. The script uses the WhiteboxTools environment to perform hydrological and geostatistical calculations.


## Input Data

1. **Digital Elevation Model (DEM)**
Raster layer with elevation information
- Recommended resolution: 10 m × 10 m
- Must have a valid coordinate system

2. **Subcatchment Areas (TEZG)**
Polygon shapefile with sub-basins
- Unique subb.nr
- Inflow junction (j.in)
- Outflow junction (j. out)
- Optional: designation

3. **Main Channel (Hauptgerinne)**
Line shapefile with one main channel branch per SUBB

4. **Detailed Channel Network (Feingerinne) (*optional*)**
Line shapefile with detailed channel network
- For more accurate calculation of flow path length

5. **Surface Runoff Coefficient Class Areas *SRC* (AKL)**
Polygon shapefile with areas of the same runoff class
- Attribute field with SRC value (0–6)

6. **Surface Roughness Class  Areas *RCC* (RKL)**
Polygon shapefile with areas of the same roughness class
- Attribute field with RCC value (1–6)

7. **Interflow Areas *IFF* (ZAF) (*optional*)**
Polygon shapefile with:
- IFF field (interflow factor, 0–7)

8. **Output Directory (Ausgabeverzeichnis)**
- Path to a folder where results will be saved
- Option: Save intermediate results

> **Note:** To use the script, the WhiteboxTools environment must be installed and correctly integrated in QGIS. WhiteboxTools is a powerful open-source GIS toolkit available through the QGIS 'Processing' plugin.

---

## Tool Calculation Steps

1. **X / Y – Centroid Coordinates**

For each SUBB, the geometry centroid is calculated. The X and Y coordinates of this point are stored as "ctr_x" and "ctr_y". These values represent the spatial location of the SUBB.

2. **Area [km²] - Sub-catchment Areas**

The area of each SUBB is calculated from the polygon geometry. The area is determined in square meters and then divided by 1,000,000 to obtain the value in km².

**Result field:** "Flaeche [km²]"

3.**F-Length [m] – Flow Path Length**

The mean flow path length is calculated using the "downslope_distance_to_stream" function from the WhiteboxTools package. The distance from the highest point (ridge) to the channel (stream) is determined on a raster basis.

#### Calculation of F-Length [m] Depending on Main and Detailed Channel

If no detailed channel network is specified, the main channel is used. If a detailed channel network is available, it is preferred for calculating flow paths as it represents a more detailed channel network.

The selected channel network (main or detailed channel) is clipped to the area of the SUBB. If the coordinate system of the channel network differs from the DEM, it is reprojected.

The channel network is rasterised using the `wbt.rasterize_streams` tool, with the raster alignment matching the DEM. Result: A binary raster containing the location of channel cells. The DEM is hydrologically corrected (`fill_depressions_wang_and_liu`). Flow directions and flow accumulation are determined.

Using the `downslope_distance_to_stream` tool (WhiteboxTools), the distance to the nearest channel cell is calculated for each raster cell. This produces a flow path length raster containing the overland flow length for each cell.

To identify the relevant flow paths, the flow path length raster is multiplied by a reclassified flow accumulation raster that contains only cells at ridgetops (watersheds). Result: A raster with flow path lengths from ridgetops to the channel.

For each SUBB, the mean flow path length is calculated from the above raster. This is done using `qgis:zonalstatistics`, extracting the mean value.

**Result field:** "F-Laenge [m]"

4. **F-Slope [1] – Surface Slope**

The slope is calculated from the digital elevation model (DEM) using the GDAL "slope" tool. The output is in percent but is divided by 100 to obtain the dimensionless value (e.g., 0.12 for 12%). The mean slope per SUBB is also determined using zonal statistics.

**Result field:** "F-Neigung [1]"

5. **Derivation of Surface Runoff Classes (SRC) and Roughness Coefficient Classes (RCC)**

The polygon shapefiles SRC layer (areas of equal runoff coefficient class) and RCC layer (areas of equal roughness class) contain an attribute field with the respective classification values SRC and RCC (SRC values: 0 to 6; RCC values: 1 to 6). Both attributes can also be present together in a single file.

The SUBB layer is reprojected if necessary to match the coordinate system to the SRC or RCC layer. Then a geometric intersection is performed between the SUBB layer and the respective classification layer.

For each combination of SUBB and SRC/RCC class, the intersected area is calculated. The area is determined in square meters and aggregated by class.

The calculated area fractions per class are stored in a dictionary. For each SUBB-ID, the area fractions are stored as follows: SRC-0, SRC-1, ..., SRC-6; RCC-1, ..., RCC-6

> **Note:** The use of shapefiles is recommended, as GPKG files are not fully supported according to the script.

6. **Derivation of Interflow Factor (IFP) and Interflow Fraction (IFF)**

Optionally, a polygon layer with areas of equal IFP and IFF values can be loaded. IFP: values from 0 to 7 (factor); IFF: values from 0 to 1 (fraction).

Both attributes are converted into separate rasters:
- IFP raster: contains the interflow factors
- IFF raster: contains the interflow fractions

The raster resolution corresponds to the cell size of the DEM.

#### Reclassification of IFP and Masking of IFF

IFP is reduced to four classes: Classes 1 to 4 are retained, classes >4 are set to NoData (-9999).

IFF is masked so that only cells with IFP > 0 are considered.

#### Calculation of Weighted Means - Weighted IFP (wIFP)

$$\text{wIFP} = \frac{\sum(\text{IFP} \times \text{IFF})}{\sum \text{IFF}}$$

**Implementation:** Multiplication of IFP and IFF rasters. Zonal statistics per SUBB provides the sum product and the sum of IFF.

#### Calculation of Weighted Means - Weighted IFF (wIFF)

$$\text{wIFF} = \frac{\sum(\text{IFF} \times \text{cell size})}{\text{total area IFF}} \times 100$$

**Implementation:** Multiplication of IFF by cell size. Zonal statistics provides sum product and cell count.

In the script, the original very slow interflow factor values (IFP) >4 are replaced with NoData values. This reclassification eliminates all areas with IFP>4, so that only "faster" IFP areas remain. The weighted averaging thus avoids overestimation of very slow interflow.

The masking ensures that only cells with valid IFP-IFF combinations are used.

7. **C-Length [m] – Channel Length**

The channel length of a sub-catchment is determined by intersecting the main channel with the respective sub-area. After geometric merging (dissolve) per SUBB-ID, the length of the resulting channel line is calculated directly from the geometry.

8.** C-Slope [1] – Channel Slope**

In the script, the channel slope per sub-catchment is determined by first intersecting the channel network with the SUBB and merging it into one line per area. For this channel line, the length is calculated and in parallel the minimum and maximum elevation are derived from the DEM. The channel slope is then calculated as a dimensionless value from the elevation difference and line length (elevation difference divided by channel length).

---

## OUTPUT

The output of the script is a CSV file named `import_zemokost.csv`, which summarizes the most important hydrological and geometric parameters for each sub-catchment (SUBB). Contents include:

- **Identifiers:** SUBB number, junctions top/bottom, name, centroid coordinates
- **Area attributes:** size in km² and mean slope
- **Flow paths:** mean flow length (F-Laenge) and channel length (C-Laenge)
- **Channel attributes:** channel slope
- **Runoff and roughness classes:** SRC, RCC with area fractions
- **Interflow parameters:** weighted IFP, IFF (if specified)

Thus, the CSV provides an (almost) complete overview of all input data required for the rainfall-runoff model ZEMOKOST. The parameters are organized in the output file so that they can be directly transferred to the ZEMOKOST input interface via copy-paste.

> **Note:** Direct derivation of the D90 [m] parameter, which is essential for modeling with ZEMOKOST, is currently not possible and not implemented. This value must be entered separately.
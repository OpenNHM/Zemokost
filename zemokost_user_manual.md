# ZEMOKOST v2.0.1

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
- [About ZEMOKOST](#about-zemokost)
- [Setup and Activation](#setup-and-activation)
- [Colour Code](#colour-code)
- [Definition of Catchment Parameters](#definition-of-catchment-parameters)
- [Rainfall Input](#rainfall-input-for-hydrological-simulation)
- [Simulation and Results](#scenario-simulation-and-design-discharge-calculation)
- [File Management](#file-management-and-export)

---

# USER MANUAL

### An optimized travel time method originally developed by Zeller and later modified by Kohl and Stepanek, designed for flood assessment in small catchments.

**Bernhard Kohl**  
📧 bernhard.kohl@bfw.gv.at  

**Contributors:**  
Adrian Maldet, Leopold Stepanek 


## About ZEMOKOST

The simulation program ZEMOKOST (v2.0.1en) is a rainfall-runoff model specifically designed for flood estimation in small torrent catchments. In practical applications, catchment areas for ZEMOKOST analyses range from small plots of less than 100 m² to larger catchments of approximately 100 km². ZEMOKOST is based on the travel time method developed by Zeller and later modified by Kohl and Stepanek (Kohl and Stepanek, 2005; Kohl, 2012).

This guide serves as the user manual for ZEMOKOST v2.0.1. It explains all the steps that must be carried out in sequence. Each button and input field for the next step will only appear once the previous step has been completed:

- Catchment definition
- Rainfall data input
- Simulation and results

## Setup and Activation

ZEMOKOST (V2.0.1en) is implemented in Microsoft Excel 2013, using a comprehensive set of Visual Basic for Applications (VBA) macros. ZEMOKOST is compatible with all current desktop versions of Microsoft Excel, including Excel 2013, Excel 2016, Excel 2019, Excel 2021, and Microsoft 365 Excel.

The program is structured across multiple worksheets, which are dynamically shown or hidden depending on the current step in the simulation workflow. Users begin in the main worksheet, define simulation parameters, and proceed through a guided sequence of inputs and calculations.

The file ZEMOKOST-2_0_1en.xlsm is a macro-enabled Excel workbook, and macros must be activated for the program to function correctly.

### Activation Macros

This can be done via:

**File → Options → Trust Center → Trust Center Settings → Macro Settings.**

Other changes that could be required, enabling controls via:

**File → Options → Trust Center → Trust Center Settings → ActiveX-settings → Prompt me before enabling all controls with minimal restrictions**

### Colour Code

The interface employs a color-coded system to indicate the status of data entry:


| Colour | Type | Description |
|-------|------|-------------|
| <span style="background-color: #FF80FF; color: white; padding: 2px 8px;">**Magenta**</span> | Button | Dataset incomplete or contains missing mandatory entries |
| <span style="background-color: #00ff00; color: white; padding: 2px 8px;">**Bright Green**</span> | Button | All required data have been successfully provided |
| <span style="background-color: #c6e0b4; color: white; padding: 2px 8px;">**Pale Green**</span> | Field | Obligatory input data |
| <span style="background-color: #ffe699; color: black; padding: 2px 8px;">**Yellow**</span> | Field | Optional data or parameters to enter |
| <span style="background-color: #f8cbad; color: black; padding: 2px 8px;">**Light Orange**</span> | Field | User input required |

Each parameter is accompanied by comment fields (<span style="color: #FF0000 !important; font-weight: bold !important;">◄</span>) that provide contextual annotations and guidance for data entry.

## Definition of Catchment Parameters

The user starts at the primary worksheet main by describing the catchment and initially saving the file giving it a specific file name.

The initial step in utilizing the ZEMOKOST modelling framework involves the comprehensive definition of the catchment area and its associated hydrological parameters. This is initiated via the define catchment button on the first main worksheet, which opens the corresponding worksheet interface.

To reset the model to its initial state, the clear ZEMOKOST button on the main worksheet restores the original, unpopulated template file.

### Worksheet Catchment definition:

**Main → define catchment → Catchment definition**

#### Show fields

Within the worksheet titled catchment definition, users can selectively activate or deactivate various input fields to tailor the model to specific hydrological scenarios.

### Required Parameters (green fields)

The core parameters required for simulation include:

### Catchment structure

#### Subcatchment definition

ZEMOKOST subdivides the catchment into sub-basins connected by junction points to simulate water flow routing. The model supports up to 300 sub-basins, although simulations can also be conducted for a single, unified catchment. Each sub-basin represents an area with similar hydrological characteristics and is defined by three parameters:

Each sub-basin is defined by a triplet:

- **Sub-basin number (subb.nr.):** Unique identifier for each sub-basin (1, 2, 3, ...)
- **inflow junction (j. in):** Junction where water enters the sub-basin
- **outflow junction (j. out):** Junction where water leaves the sub-basin

#### Simple example:

- **Sub-basin 1** → Junction Inflow: 0 (inlet) → Junction Outflow: 1
- **Sub-basin 2** → Junction Inflow: 1 → Junction Outflow: 2
- **Sub-basin 3** → Junction Inflow: 2 → Junction Outflow: 3 (outlet)

#### Flow logic:

This creates a sequential water flow path where sub-basin 1 (headwater area) discharges to junction 1, sub-basin 2 receives this flow and discharges to junction 2, and sub-basin 3 receives the combined flow and discharges to the catchment outlet (junction 3).

#### Delineation guidelines

- Sub-basins should reflect areas with similar land use, slope, or hydrological behaviour
- Channel segments should align with sub-basin boundaries
- Consider the 300 sub-basin limit when planning your catchment subdivision

#### Essential rules for junction structure:

- **Unique numbering:** Each sub-basin and junction must have a unique number
- **Headwater areas:** Sub-basins without upstream input use inflow junction "0" (this value can be used multiple times)
- **Flow direction:** Every inflow junction must connect to exactly one outflow junction
- **Network connectivity:** All sub-basins must eventually drain to a single outlet
- **No loops:** Circular flow paths are not allowed - water must flow in one direction only

> **Validation tip:** Trace the water flow from each sub-basin to ensure it reaches the outlet without creating loops or dead ends.

### Areal data

Sub-basin boundaries and areas can be delineated manually using topographic maps or digitally using GIS tools. 

> See **[WLV_pyqgis_ZEMOKOST](toolbox_zemokost_en.md)** for more information.

The following parameters are typically extracted:

- **Area [km²]:** Projected area of the sub-basin.
- **Length [m]:** Surface flow path length (Lsur) refers to the average terrain-parallel distance that surface runoff travels from the watershed boundary to the nearest stream or channel. It represents the maximum projected flow length across the land surface before water enters the drainage network.
- **Slope [1]:** Surface slope as a dimensionless gradient, calculated as the ratio of vertical elevation change to horizontal distance (Δh/Δx). Typical values range from 0 (flat) to 1 (very steep).

In ZEMOKOST, the surface flow path length (Lsur) is directly influenced by the detail of the stream network—a finer network results in shorter Lsur values. The balance between Lsur and channel flow length (Lch) affects the overall hydrograph shape and peak timing. It is a key input for calculating surface runoff concentration time and is typically derived from topographic maps or digital elevation models using GIS.

#### Area segmentation surface runoff classes SRC and area segmentation roughness coefficient classes RCC

- **Surface Runoff Coefficient Class (SRC) [–]:** Scale from 0 to 6, where 0 = no surface runoff and 6 = 100% surface runoff.
- **Surface Roughness Class (RCC) [–]:** Scale from 0 to 6, where 0 = very smooth surface and 6 = extremely rough surface.

The SRC defines the runoff disposition based on land cover and soil type, while the RCC characterizes the hydraulic resistance of the surface. Both classes are selected from predefined categories based on field assessments or mapping guidelines and are input as either percentage values or area per sub-basin. Since ZEMOKOST averages the values per sub-basin internally, the choice of input format does not affect the outcome.

A drop-down menu allows the user to select whether the SRC or RCC classes are represented by their mean (m), default, or by their bottom (b) or top (t) boundaries for further modelling. These parameters are essential for calculating surface flow velocity and concentration time. 

Detailed information how to assess SRC and RCC can be found here:

https://www.researchgate.net/publication/273761280_A_Simple_Code_of_Practice_for_the_Assessment_of_Surface_Runoff_Coefficients_for_Alpine_Soil-Vegetation_Units_in_Torrential_Rain_Version_20 

### Channel topology

- **length [m]:** Total length of the main drainage channel (Lch) within the sub-basin. Influences the routing of water within the drainage network and affects hydrograph shape and timing.
- **slope [1]:** Dimensionless slope of the main stream, calculated as the ratio of vertical elevation change to horizontal distance (Δh/Δx). Typical values range from 0 (flat) to 1 (very steep).
- **d90 [m]:** Characteristic Grain Diameter Grain size for which 90% of the sediment is finer (D90). Describes the dominant roughness of the stream channel and is crucial for estimating flow resistance and velocity using the empirical Rickenmann formula.

In ZEMOKOST, Lch represents the distance over which water is routed through the channel and is used to calculate channel flow time. D90 is essential for modelling flow velocity and the translation of runoff through the channel network.

## Optional Parameters (yellow fields)

Optional parameters can significantly enhance model accuracy and allow for a more detailed representation of hydrological processes. While not strictly required for basic simulation, they provide additional flexibility to capture complex system behaviour and improve the realism of the results.

### Coordinates of sub-basins

In ZEMOKOST, the coordinates of sub-basins can be used to model spatially variable rainfall input by defining a central rainfall cell (typically the most affected sub-basin) and calculating the mean distance of each sub-basin from this center. These distances are then used to apply distance-dependent rainfall attenuation functions (e.g., Lorenz & Skoda or Blöschl) to simulate realistic spatial rainfall gradients. This approach allows the model to account for the decreasing intensity of precipitation with increasing distance from the rainfall centre.

### Areal data: Natural retention and base flow

Natural retention refers in ZEMOKOST to the temporary storage and delay of runoff caused by natural landscape features such as wetlands, saturated soils, colluvial deposits, moraines, and vegetated depressions. These areas reduce peak discharge and extend runoff duration by either retaining water volume or slowing flow velocity through surface roughness and infiltration.

To incorporate natural retention into the model, the retentive effect is quantified as a percentage of the sub-basin area. This value represents the proportion of the sub-basin that contributes to flow damping and is entered in the model accordingly. By assigning this percentage, ZEMOKOST can simulate the attenuation of hydrograph peaks and improve the realism of flood modelling.

A base flow value (in m³/s) can be defined individually for each sub-basin to represent constant groundwater or spring discharge. However, it is important to ensure that the cumulative base flow across all sub-basins remains hydrologically plausible and does not lead to unrealistic total discharge values at the outlet.

### Interflow (recommended)

In ZEMOKOST, interflow is directly coupled with surface runoff and thus also with rainfall intensity. The stronger the rainfall, the greater the surface runoff, and consequently, the lower is the potential for interflow, since less water infiltrates. Conversely, under lower rainfall intensities, infiltration increases, and interflow becomes more dominant.

The two parameters - Interflow Portion (IFP) and Interflow Factor (IFF) - work together to simulate subsurface lateral flow:

The Interflow Portion (IFP) defines the percentage of the sub-basin area that contributes to interflow. The Interflow Factor (IFF) represents the hydraulic resistance of the subsurface and determines the velocity of interflow. It is based on substrate permeability and influences how quickly infiltrated water reaches the stream network.

| IFF | Description | Permeability [m/s] | Permeability [cm/h] |
|-----|-------------|-------------------|-------------------|
| 1 | Very highly permeable | > 1×10⁻² | 3600 |
| 2 | Very highly to highly permeable | 5.5×10⁻³ | 1980 |
| 3 | Highly permeable | 1×10⁻³ | 360 |
| 4 | Highly to moderately permeable | 5.5×10⁻⁴ | 198 |
| 5 | Moderately permeable | 1×10⁻⁵ | 3.6 |
| 6 | Slightly permeable | 1×10⁻⁷ | 0.036 |
| 7 | Very slightly permeable | > 1×10⁻⁸ | 0.0036 |

The dynamic coupling of rainfall, surface runoff and interflow ensures that ZEMOKOST reflects the inverse relationship between surface runoff and interflow, allowing for more realistic simulation of hydrological responses under varying rainfall conditions.

### Measures

The consideration of technical measures in ZEMOKOST includes the integration of retention-basins, which can be modelled in two ways: either as fixed storage volumes, where a defined amount of water is retained and subtracted from the runoff, or via a V/Q relationship, which simulates the dynamic behaviour of the retention-basin by linking the stored volume (V) to the outflow discharge (Q). This allows for a more realistic representation of retention-basin hydraulics, including delayed release and peak flow attenuation. Additionally, inlets and outlets can be defined to control how water enters and exits the retention-basin, enabling the simulation of regulated flow systems and engineered discharge structures.

### System status

**Drop Down system status ("-6" – "6")**

To account for varying initial moisture conditions, ZEMOKOST introduces the System State Index (SZI). The default value of SZI is zero, representing an average conditions for runoff generation. Increasing the SZI shifts the intercept of the runoff coefficient–abstraction time relationship proportionally, implying improved hydrological conditions and delayed runoff onset. Values above 6 indicate exceptionally favorable system states, while negative SZI values (down to –6) reflect increasingly dry antecedent conditions. Values below –6 are considered implausible.

## Finalization and Upload of catchment parameters

Once all relevant parameters in catchment definition have been defined, the dataset can be uploaded using the upload catchment definition button. This action returns the user to the main interface.

If any required fields are incomplete or contain invalid entries, ZEMOKOST will generate specific error messages to assist in troubleshooting and correction.

## Rainfall Input for Hydrological Simulation

Accurate rainfall input is a fundamental prerequisite for precipitation–runoff modelling. Once the catchment has been defined, the main worksheet displays dedicated input buttons for rainfall data entry.

ZEMOKOST offers flexibility in rainfall specification to simulate both uniform and spatially variable precipitation scenarios. This is particularly important for modelling convective storm events or complex topography in alpine catchments.

### Two main methods:

- **Design rainfall:** Statistical rainfall for flood estimation (most common)
- **Observed rainfall:** Manual time series input for specific events

### Two input levels:

- **Catchment:** Apply rainfall to entire catchment → opens distribution worksheet with spatial options (common)
- **Sub-catchment:** Define rainfall individually per sub-basin → no additional distribution needed (optional)

## Design rainfall input

**Main → load design rainfall → Catchment or sub-catchment → uw-series input**

Design rainfall is typically used for flood estimation in small, ungauged alpine catchments, which is the primary application domain of ZEMOKOST. The users can enter choose between two input options:

- **p1-/p100- series input**, where p1 is the rainfall depth for a 1-year return period and p100 for a 100-year return period
- **u- /w-series input**, where u is the mean rainfall and w the standard deviation) to generate design rainfall curves for simulation.

Both options are used to generate design rainfall curves for simulation. The p1-/p100-series defines the intensity–duration–frequency (IDF) relationship for a location, while the u-/w-series provides mean and standard deviation values for the same purpose.

At least three duration–depth pairs (or three u-/w-pairs) are required to generate a valid rainfall curve. Once the data are entered, the user can visualize the rainfall distribution. A drop-down menu allows the selection of the Curve Shape, while the visualization automatically adapts to the selected Return Period and Rainfall Duration. The selected curve shape is inherited for simulation, although the visualization itself does not directly influence simulation settings.

The load design-series button redirects to uw-series distribution worksheet (only for catchment not sub-catchment).
## Design precipitation catchment distributed (for catchment option only)

Applies to both rainfall input methods when catchment was selected:

- **→ load p- series → p-series distribution**
- **→ load design- series → uw-series distribution**

The worksheet uw-series distribution allows users to define the spatial allocation of rainfall using one of the following methods: These functions reflect the empirical observation that rainfall intensity decreases with increasing distance from the rainfall centre, and with increasing catchment area.

### Reduction Methods (mandatory - select one):

- **None:** Uniform rainfall across the entire catchment.
- **Manual input:** User-defined reduction values per sub-basin [%].
- **Radial distance:** Reduction based on distance from a central rainfall cell.
- **Radial (XY-coordinates)** (only if xy defined in catchment definition): Reduction based on geographic coordinates of a defined rainfall centre.

*This option requires that X and Y coordinates of sub-basins have been entered in the catchment definition worksheet.*

### Reduction strength (only for radial distance and radial xy coordinates):

- **Slight reduction:** Based on Lorenz & Skoda (2001), corrected by Drexel (2009).
- **Strong reduction:** Based on Blöschl (2009), suitable for larger catchments or convective rainfall events.

## Temporal Offset and Event Simulation

An optional time offset can be applied to simulate the movement of a storm cell across the catchment. This feature allows for dynamic rainfall scenarios, such as convective events with spatial and temporal variability.


## Rainfall event input

**Main → load rainfall series → catchment or sub-catchment**

Rainfall series for a single event can be loaded here, with two options- design rainfall or manual input- which open the P-Series Input worksheet when the apply design rainfall button is pressed.

### Design rainfall → apply rainfall series → p-series input

Enter the rainfall intensity (mm/h) and duration (min), then select the rainfall curve shape from the dropdown menu. With the load p-design series button redirects to the p-series distribution worksheet.

### Manual input → apply rainfall series → p-series input

A manually entered rainfall time series allows full control over the temporal distribution. Rainfall data should be entered at one-minute intervals, starting from the onset of rainfall to ensure proper alignment of runoff generation and hydrograph development. A rainfall intensity value must be provided for each minute; enter 0 for any pause in rainfall.

The load p-series button redirects to the p-series distribution worksheet (only for catchment not sub-catchment), where reduction, strength, and offset can be adjusted as described under Design Rainfall Input.



**Final step:** Once the areal and temporal distribution settings are defined, the rainfall data can be loaded into the simulation using the load data button redirecting to the main worksheet.

## Scenario Simulation and Design Discharge Calculation

After defining the catchment parameters and selecting the rainfall input, the main worksheet displays buttons for simulation. The available option depends on your rainfall input type:

- **Scenario Simulation** is used when a manual rainfall series is loaded. This option allows running event-based simulations for a specific rainfall time series.
- **Design Discharge Calculation** is used when a design rainfall series is loaded. This option calculates discharges based on statistically derived rainfall for a selected return period (e.g., T = 100 years).

The appropriate simulation button—perform scenario or perform design—appears automatically. Both simulation types can be linked to specific observational junctions for targeted analysis.

### Simulation Workflow

Depending on the selected rainfall input method, the workflow proceeds as follows:

**For manual rainfall series:**
Select junction → perform scenario

**For design rainfall input:**
- calculate specific events select return period and rainfall duration → perform design
- calculate design event select return period → perform design

## Results and Output

After simulation, the main worksheet displays:

### Peak Discharge Table and Graph:

- A table lists the peak discharge, time to peak, runoff volume, and rainfall volume for each simulated rainfall duration.
- The model automatically identifies the critical rainfall duration, i.e., the duration that produces the maximum peak discharge.
- A corresponding graph visualizes the peak discharge across all tested durations, allowing for quick identification of the most critical scenario.

### Detailed Simulation Results for the Critical Duration:

- Below the peak discharge summary, detailed results for the selected critical rainfall duration are shown.
- These include hydrograph shapes, discharge volumes, and timing for each junction and sub-basin, enabling spatial analysis of runoff dynamics.

## Additional Output Worksheets

### hydrographs subbasins

Contains individual hydrographs for each sub-basin, showing discharge over time. This allows for comparison of runoff behaviour across different landscape units.

### hydrographs junctions

Displays hydrographs for each defined junction (node) in the catchment structure. These are useful for evaluating cumulative discharge and flow routing at key control points.

### design results

Includes hydrographs for all simulated rainfall durations at the selected observational junction. This worksheet supports sensitivity analysis and helps assess how different rainfall durations affect discharge at a specific location.

## File Management and Export

The **export** button allows all results to be copied into a separate Excel workbook for documentation or further analysis.

To manage file size, especially in simulations involving many sub-basins, the **delete results** button can be used. This retains the catchment and rainfall input but removes all simulation results, reducing the file size for storage or sharing.

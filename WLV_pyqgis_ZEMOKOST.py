 
# -*- coding: utf-8 -*-

"""
Toolbox:        WLV_Tools
Script:			Aufbereitung ZEMOKOST mit Zwischenabfluss, Version 1.4.0

Author:         KS, NC, BT (ms.gis,); JK(WLV); BK(BFW)
QGIS Version:   > 3.40.9
Created:        2020-04-14
Last updated:   2025-08-20

-----------
Change log:
v1.4.0
    - Corrected wZAF calculation
    - Corrected some changed issues from v1.3.0
v1.3.0
    - Updated wZAF calculation
    - Added a check for areas of Teileinzugsgebiet less than 100 m². If this condition is met, a warning message will be displayed at the end of processing
v1.2.0
    - Replace Saga Tools with WhiteboxTool
v1.1.3
    - Change import gdal -> from osgeo import gdal
    - Delete unused import
v1.1.2
    - Removed 1m DEM as default input
    - Assigning EPSG 31287 to dem if input is "M:\BMLF\WLK\RASTER\DGM\ALS_DGM_1m_AT_COG_20210111.tif"
v1.1.1
    - New DEM (replaced old DEM)
v1.1.0
    - Internal checker for the output of the Overland flow distance to channel network calculation. If the internal checker fails, the inputs 
    for the saga tool will be aligned (e.g. same cell size, same resolution and same spatial extent
    - Store the output of the dissolve function in the temp folder explicitly (e.g. QgsProcessingUtils.tempFolder())

"""

## Imports Tool
import csv
import os
import uuid
import sys
import random
import contextlib
import io


# Import the WhiteboxTools module
home_dir = os.path.expanduser("~")
script_path = os.path.join(home_dir, "AppData", "Roaming", "QGIS", "QGIS3", "profiles", "default", "processing", "scripts")
sys.path.append(script_path)

from WBT.whitebox_tools import WhiteboxTools

import shutil
from PyQt5.QtCore import (QCoreApplication, QVariant)
from osgeo import gdal
from qgis import processing
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterField,
                       QgsRasterLayer,
                       QgsField,
                       QgsCoordinateReferenceSystem,
                       QgsVectorFileWriter,
                       QgsProcessingParameterBoolean,
                       QgsProcessingException,
                       QgsProcessingUtils,
                       QgsVectorLayer)

from qgis.PyQt.QtWidgets import QMessageBox

def delete_temp_files(temp_folder):
    for item in os.listdir(temp_folder):
        item_path = os.path.join(temp_folder, item)
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
            except PermissionError:
                pass
        elif os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
            except PermissionError:
                pass



class ZEMOKOST_GISDaten(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    DEM = 'DEM'
    TEZG = 'TEZG'
    TEZG_ID = 'TEZG_ID'
    KNT_UPPER = 'KNTO'
    KNT_LOWER = 'KNTU'
    NAME = 'NAME'
    CHANNEL_MAIN = 'CHANNEL_MAIN'
    CHANNEL_HIGHRES = 'CHANNEL_HIGHRES'
    DISCHARGE_COEFF = 'DISCHARGE_COEFF'
    DISCHARGE_COEFF_VAL = 'DISCHARGE_COEFF_VAL'
    ROUGHNESS_COEFF = 'ROUGHNESS_COEFF'
    ROUGHNESS_COEFF_VAL = 'ROUGHNESS_COEFF_VAL'
    INTERFLOW = 'INTERFLOW'
    INTERFLOW_FACTOR = 'INTERFLOW_FACTOR'
    INTERFLOW_PROP = 'INTERFLOW_PROP'
    PROJECTPATH = 'PROJECTPATH'
    KEEPDATA = 'KEEPDATA'

    def tr(self, string):
        """
		Returns a translatable string with the self.tr() function.
		"""
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ZEMOKOST_GISDaten()

    def name(self):
        """
		Returns the algorithm name, used for identifying the algorithm. This
		string should be fixed for the algorithm, and must not be localised.
		The name should be unique within each provider. Names should contain
		lowercase alphanumeric characters only and no spaces or other
		formatting characters.
		"""
        return 'zemokost'

    def displayName(self):
        """
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
        return self.tr('Aufbereitung ZEMOKOST')

    def group(self):
        """
		Returns the name of the group this algorithm belongs to. This string
		should be localised.
		"""
        return self.tr('WLV Tools')

    def groupId(self):
        """
		Returns the unique ID of the group this algorithm belongs to. This
		string should be fixed for the algorithm, and must not be localised.
		The group id should be unique within each provider. Group id should
		contain lowercase alphanumeric characters only and no spaces or other
		formatting characters.
		"""
        return 'scripts'

    def shortHelpString(self):
        """
		Returns a localised short helper string for the algorithm. This string
		should provide a basic description about what the algorithm does and the
		parameters and outputs associated with it..
		"""
        return self.tr(
            "Aufbereitung der Grundlagendaten für das NA Modell ZEMOKOST. Es werden Angaben zu Teileinzugsgebietsflächen, Abflussbeiwert, Rauhigkeitsbeiwert, Gerinne und ein DHM benötigt. Die zusätzliche Angabe eines Feingerinnes sowie Informationen zu Zwischenabflussfaktor und -anteil sind optional. \n\n \n--- HINWEIS --- \n- Berechnungen und optionale Datenausgabe erfolgen im Koordinatensystem des angegeben Höhenmodells. \n- Die Verwendung von SHAPEFILES als Dateninput ist empfohlen; das Tool ist derzeit nicht für GPKG-Daten geeignet.\n\n\n\n\n--- Eingabehilfe ---\n\nHöhenmodell - Höhenmodell (Raster) auswählen. Es wird eine 10x10m Auflösung empfohlen.\n\n\nTeileinzugsgebietsflächen (TEZG) - Polygon-Shapefile mit den Teileinzugsgebietsflächen (TEZG). Jedes Polygon muss eine ID sowie jeweils einen Zufluss- und Abflussknoten haben; die Angabe einer TEZG-Bezeichnung ist optional.\n\nTEZG-ID - Attribut mit eindeutiger ID je TEZG.\n\n\nTEZG Knoten oben - Attribut mit oberem Knoten (Zuflussknoten) je TEZG.\n\n\nTEZG Knoten unten - Attribut mit unterem Knoten (Abflussknoten) je TEZG.\n\n\nTEZG Bezeichnung [optional] - Attribut mit Name/Bezeichnung je TEZG.\n\n\nHauptgerinne - Linien-Shapefile mit einem Hauptgerinneast je TEZG.\n\n\nFeingerinne [optional] - Linien-Shapefile mit dem Feingerinnenetz vom gesamten Einzugsgebiet zur Berechnung des mittleren Oberflächenfließweges (können beliebig viele Gerinneäste sein).\n\n\nAbflussbeiwert (AKL) - Polygon-Shapefile mit den Flächen gleicher Abflussbeiwerteklasse (AKL).\n\n\nAKL-Feld - Attribut mit AKL-Wert (0-6)\n\nRauigkeitsbeiwert (RKL) - Polygon-Shapefile mit den Flächen gleicher Rauigkeitsbeiwerteklasse (RKL).\n\n\nRKL-Feld - Attribut mit RKL-Wert (1-5).\n\n\n Zwischenabluss [optional] - Polygon-Shapefile mit Flächen gleichen Faktors (ZAF) und Anteils (ZAA). \n\n\nZAF-Feld (verpflichtend, wenn Zwischenabfluss-Layer angegeben wird) - Attribut mit ZAF-Wert (0-7). \n\n\nZAA-Feld (verpflichtend, wenn Zwischenabfluss-Layer angegeben wird) - Attribut mit ZAA-Wert (0-1). \n\nPfad zu Verzeichnis, in welchem Ausgabeordner mit Ergebnissen gespeichert werden.")

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def initAlgorithm(self, config=None):
        """
		Here we define the inputs and output of the algorithm, along
		with some other properties.
		"""

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('Höhenmodell'),
                optional=False
            ))

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TEZG,
                self.tr('Teileinzugsgebietsflächen (TEZG)'),
                [QgsProcessing.TypeVectorPolygon],
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.TEZG_ID,
                self.tr('TEZG-ID'),
                '',
                self.TEZG,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.KNT_UPPER,
                self.tr('TEZG - Knoten oben'),
                '',
                self.TEZG,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.KNT_LOWER,
                self.tr('TEZG - Knoten unten'),
                '',
                self.TEZG,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.NAME,
                self.tr('TEZG - Bezeichnung'),
                '',
                self.TEZG,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CHANNEL_MAIN,
                self.tr('Hauptgerinne'),
                [QgsProcessing.TypeVectorLine],
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CHANNEL_HIGHRES,
                self.tr('Feingerinne'),
                [QgsProcessing.TypeVectorLine],
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.DISCHARGE_COEFF,
                self.tr('Abflussbeiwert (AKL)'),
                [QgsProcessing.TypeVectorPolygon],
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.DISCHARGE_COEFF_VAL,
                self.tr('AKL-Feld'),
                '',
                self.DISCHARGE_COEFF,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.ROUGHNESS_COEFF,
                self.tr('Rauigkeitsbeiwert (RKL)'),
                [QgsProcessing.TypeVectorPolygon],
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.ROUGHNESS_COEFF_VAL,
                self.tr('RKL-Feld'),
                '',
                self.ROUGHNESS_COEFF,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INTERFLOW,
                self.tr('Zwischenabfluss (ZAF, ZAA)'),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.INTERFLOW_FACTOR,
                self.tr('ZAF-Feld'),
                '',
                self.INTERFLOW,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.INTERFLOW_PROP,
                self.tr('ZAA-Feld'),
                '',
                self.INTERFLOW,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.PROJECTPATH,
                self.tr('Pfad zum Ausgabeordner'),
                QgsProcessingParameterFile.Folder,
                optional=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.KEEPDATA,
                self.tr('Zwischenergebnisse/ Berechnungsgrundlagen speichern'),
                defaultValue=False
            )
        )

    def checkParameterValues(self, parameters, context):
        paramInterflow = self.parameterAsVectorLayer(parameters, self.INTERFLOW, context)
        paramZAF = self.parameterAsString(parameters, self.INTERFLOW_FACTOR, context)
        paramZAA = self.parameterAsString(parameters, self.INTERFLOW_PROP, context)

        if paramInterflow and (len(paramZAF) == 0 or len(paramZAA) == 0):
            return False, self.tr(
                'Achtung: Bei Angabe eines Zwischenabfluss-Layers müssen auch Feld ZAF und Feld ZAA befüllt sein.')

        return super(ZEMOKOST_GISDaten, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback, my_callback=None):
        """
		Here is where the processing itself takes place.
		"""

        ## --------------------------
        # Pass parameters to script
        wbt = WhiteboxTools()
        # wbt.set_verbose_mode(False)

        dgm = self.parameterAsRasterLayer(parameters, self.DEM, context)
        tezgSrc = self.parameterAsVectorLayer(parameters, self.TEZG, context)
        tezgNr = self.parameterAsString(parameters, self.TEZG_ID, context)
        knotenO = self.parameterAsString(parameters, self.KNT_UPPER, context)
        knotenU = self.parameterAsString(parameters, self.KNT_LOWER, context)
        bezeichnung = self.parameterAsString(parameters, self.NAME, context)
        gerinne = self.parameterAsVectorLayer(parameters, self.CHANNEL_MAIN, context)
        feingerinne = self.parameterAsVectorLayer(parameters, self.CHANNEL_HIGHRES, context)
        beiwert = self.parameterAsVectorLayer(parameters, self.DISCHARGE_COEFF, context)
        beiwertVal = self.parameterAsString(parameters, self.DISCHARGE_COEFF_VAL, context)
        rauhigkeit = self.parameterAsVectorLayer(parameters, self.ROUGHNESS_COEFF, context)
        rauhigkeitVal = self.parameterAsString(parameters, self.ROUGHNESS_COEFF_VAL, context)
        zaSrc = self.parameterAsVectorLayer(parameters, self.INTERFLOW, context)
        zafVal = self.parameterAsString(parameters, self.INTERFLOW_FACTOR, context)
        zaaVal = self.parameterAsString(parameters, self.INTERFLOW_PROP, context)
        wDir = self.parameterAsString(parameters, self.PROJECTPATH, context)
        keepDataBOOL = self.parameterAsBool(parameters, self.KEEPDATA, context)

        # New 1m ASL DEM has no CRS defined. Therefore we define it here, based on the file name
        if os.path.basename(dgm.source()) == 'ALS_DGM_1m_AT_COG_20240110.tif':
            dgm.setCrs(QgsCoordinateReferenceSystem(31287 , QgsCoordinateReferenceSystem.EpsgCrsId))
        else:
            pass


        ## --- Check that crs critical input layers have GDAL/OGR 3.0.4 conform crs information (necessary since 3.10.X)

        critInputError = []
        critInputLyr = [dgm, gerinne, feingerinne, beiwert, rauhigkeit, zaSrc]

        for inLyr in critInputLyr:
            try:  # Catch AttributeError in case no parameter feingerinne or zaSrc defined
                if inLyr.crs().authid() == '' and inLyr.source() not in critInputError:
                    critInputError.append(inLyr.source())
            except AttributeError:
                pass

        # Message content
        MessageContent = ''
        for l in critInputError:
            MessageContent += "\n{}".format(l)

        # Raise error message
        if len(critInputError) > 0:
            raise QgsProcessingException(
                '!!ACHTUNG!!: \nDas Koordinatenbezugssystem folgender Layer kann nicht korrekt gelesen werden:\n' + MessageContent + '\n\n Bitte z.B. durch Exportieren der Layer zu neuen Datensätzen korrigieren.\n')

        ## -----------------------
        # -   START PROCESSING   -
        # ------------------------

        feedback.pushInfo("\nSTARTING ......................")

        ## Get dem cellsize
        ras = gdal.Open(dgm.source())
        cellsize = int(ras.GetGeoTransform()[1])

        ## Get crs of input layer
        crsDEM = dgm.crs().authid().split(':')[1]
        crsGer = gerinne.crs().authid().split(':')[1]
        if feingerinne:
            crsFGer = feingerinne.crs().authid().split(':')[1]
        crsAKL = beiwert.crs().authid().split(':')[1]
        if beiwert.crs().mapUnits() != 0:
            raise QgsProcessingException(
                '!!ACHTUNG!!: Die Karteneinheit des Layers Abflussbeiwert ist nicht in Meter. Bitte ändern.')
        crsRKL = rauhigkeit.crs().authid().split(':')[1]
        if rauhigkeit.crs().mapUnits() != 0:
            raise QgsProcessingException(
                '!!ACHTUNG!!: Die Karteneinheit des Layers Rauigkeitsbeiwert ist nicht in Meter. Bitte ändern.')
        if zaSrc:
            crsZA = zaSrc.crs().authid().split(':')[1]
            if zaSrc.crs().mapUnits() != 0:
                raise QgsProcessingException(
                    '!!ACHTUNG!!: Die Karteneinheit des Layers Zwischenabfluss ist nicht in Meter. Bitte ändern.')

        ### --- CUSTOM FUNCTIONS --- ###

        # Define a utility function to get the URI of a QgsRasterLayer
        def my_callback(value):
            if not "%" in value:
                print(value)

        ## Set paths and variables
        rasDir = os.path.join(wDir, 'rasters')
        shpDir = os.path.join(wDir, 'shps')

        srcGer = os.path.join(shpDir, 'Gerinne.shp')
        srcFGer = os.path.join(shpDir, 'Feingerinne.shp')
        tezgGer_dis = os.path.join(shpDir, 'Gerinne_dissolved.shp')

        demClp = os.path.join(rasDir, 'dgm{}m.tif'.format(cellsize))
        demSlp = os.path.join(rasDir, 'dgm{}m_slopePerc.tif'.format(cellsize))
        demFilled = os.path.join(rasDir, 'dgm{}m_filled.sdat'.format(cellsize))
        demFDir = os.path.join(rasDir, 'dgm{}m_flowdir.sdat'.format(cellsize))
        demFAcc = os.path.join(rasDir, 'dgm{}m_flowacc.sdat'.format(cellsize))
        demFAccRecl = os.path.join(rasDir, 'dgm{}m_flowacc_Ridges.sdat'.format(cellsize))
        demFLen = os.path.join(rasDir, 'dgm{}m_flowlength.sdat'.format(cellsize))
        demFLenRidges = os.path.join(rasDir, 'dgm{}m_flowlength_Ridges.sdat'.format(cellsize))

        rasDrain = os.path.join(rasDir, 'Gerinne_ras.sdat')
        rasTezgGer = os.path.join(rasDir, 'TEZGGerinne_ras.sdat')

        tezg = os.path.join(shpDir, 'TEZG_Stats.shp')
        tezgAKL = os.path.join(shpDir, 'TEZG_AKL.shp')
        tezgRKL = os.path.join(shpDir, 'TEZG_RKL.shp')
        tezgGer = os.path.join(shpDir, 'TEZG_Gerinne.shp')
        tezgGerStats = os.path.join(shpDir, 'TEZG_GerinneStats.csv')

        tezgZA = os.path.join(shpDir, 'TEZG_ZA.shp')
        rasTezgZAF = os.path.join(rasDir, 'ZAF_{}m_ras.tif'.format(cellsize))
        rasTezgZAF_recl = os.path.join(rasDir, 'ZAF_{}m_rasRecl.tif'.format(cellsize))
        rasTezgZAA = os.path.join(rasDir, 'ZAA_{}m_ras.tif'.format(cellsize))
        rasTezgZAA_recl = os.path.join(rasDir, 'ZAA_{}m_rasRecl.tif'.format(cellsize))
        ras_rZAF_x_rZAA = os.path.join(rasDir, 'rasCalc_rZAF_x_rZAA.tif')
        ras_cellsize_x_rZAA = os.path.join(rasDir, 'rasCalc_cellsize_x_rZAA.tif')

        # Define the temporary folder for wbt outputs
        temp_folder = QgsProcessingUtils.tempFolder()

        # List for vlyr und rlyr, to save at end if required
        lyrList = []

        # Create dictionary for data to save in result csv
        dictCsv = {}

        ## Create directories
        feedback.pushInfo("\n   ... creating output directory")

        os.makedirs(wDir, exist_ok=True)

        if keepDataBOOL:
            os.makedirs(rasDir, exist_ok=True)
            os.makedirs(shpDir, exist_ok=True)

        ## --- MAKE A COPY OF EZG FOR STATS ---
        feedback.pushInfo("... making a copy of TEZG")

        res3 = processing.run("native:reprojectlayer", {
            'INPUT': tezgSrc,
            'TARGET_CRS': dgm,  # dgm crs determines project crs
            'OUTPUT': 'TEMPORARY_OUTPUT'})
        vlyr_tezg = res3['OUTPUT']
        vlyr_tezg.setName('vlyr_tezg')
        lyrList.append(vlyr_tezg)

        # Iterate through the features of the vlyr_tezg layer
        small_area_threshold = 100.0  # threshold in square meters
        has_small_area = False

        for feature in vlyr_tezg.getFeatures():
            geom = feature.geometry()
            area = geom.area()
            if area < small_area_threshold:
                has_small_area = True
                break  # Exit the loop if any area is smaller than the threshold

        # --- ADD UNIQUE TEZG_ID_ZK FIELD AND CENTROIDS to TEZG SHP ---

        # Add TEZG_ID_ZK field, likely unique over all input layer
        feedback.pushInfo("... adding fields for TEZG_ID and centroids ")
        idField = QgsField('TEZG_ID_ZK', QVariant.String)

        # Add fields for centroid coordinates to tezgs
        xField = QgsField('ctr_x', QVariant.Double)
        yField = QgsField('ctr_y', QVariant.Double)

        vlyr_tezg.dataProvider().addAttributes([idField, xField, yField])
        vlyr_tezg.updateFields()

        # Calculate x,y coordinates of ezg centroids and transfer tezgNr
        feedback.pushInfo("... calculating TEZG_ID and centroids")

        vlyr_tezg.startEditing()
        feats = vlyr_tezg.getFeatures()
        for feat in feats:
            feat['ctr_x'] = feat.geometry().centroid().asPoint().x()
            feat['ctr_y'] = feat.geometry().centroid().asPoint().y()
            feat['TEZG_ID_ZK'] = int(feat[tezgNr])
            vlyr_tezg.updateFeature(feat)
        vlyr_tezg.commitChanges()

        # Add EZG data to output dictionary
        feedback.pushInfo("... adding catchment attributes to dictionary")


        feats = vlyr_tezg.getFeatures()
        fidVal = []
        for feat in feats:
            fid = int(feat['TEZG_ID_ZK'])
            fidVal.append(fid)
            dictCsv[fid] = {}
            # feedback.pushInfo(f"Value: {fid}, Type: {type(fid)}")

            dictCsv[fid]['TEZG Nr.'] = fid
            dictCsv[fid]['K.O.'] = str(feat[knotenO]).replace('.', ',')
            dictCsv[fid]['K.U.'] = str(feat[knotenU]).replace('.', ',')
            dictCsv[fid]['X'] = str(feat['ctr_x']).replace('.', ',')
            dictCsv[fid]['Y'] = str(feat['ctr_y']).replace('.', ',')

            if bezeichnung != '':
                dictCsv[fid]['Bezeichnung/Ergaenzung'] = feat[bezeichnung]

            # Calculate area for feat
            featArea = feat.geometry().area()
            dictCsv[fid]['Flaeche [km2]'] = str(round(featArea / 1000000, 4)).replace('.', ',')



        ## --- CREATE COPY OF FLOWPATHS IN DGM CRS ---

        # -- Gerinne --

        # Reproject TEZG to crsGer if different crs
        if crsDEM != crsGer:
            res16 = processing.run("native:reprojectlayer", {
                'INPUT': vlyr_tezg,
                'TARGET_CRS': gerinne,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            clipTEZG = res16['OUTPUT']
        else:
            clipTEZG = vlyr_tezg

        # Clip gerinne to TEZG
        gerinne_path = os.path.join(temp_folder, f"gerinne_{uuid.uuid4().hex}.shp")
        res17 = processing.run("native:clip", {
            'INPUT': gerinne,
            'OVERLAY': clipTEZG,
            'OUTPUT': gerinne_path})
        vlyr_srcGer = QgsVectorLayer(res17['OUTPUT'], 'vlyr_srcGer', 'ogr')

        # Reproject gerinne to crsDEM if different crs
        if crsDEM != crsGer:
            res1 = processing.run("native:reprojectlayer", {
                'INPUT': res17['OUTPUT'],
                'TARGET_CRS': dgm,  # dgm crs determines project crs
                'OUTPUT': gerinne_path})
            vlyr_srcGer = QgsVectorLayer(res1['OUTPUT'], 'vlyr_srcGer', 'ogr')


        # Set layer name and add to lyrList
        vlyr_srcGer.setName('vlyr_srcGer')
        lyrList.append(vlyr_srcGer)

        # -- Feingerinne --

        if not feingerinne:
            drainage = vlyr_srcGer
            drainage_path = gerinne_path

        else:
            # Reproject TEZG to crsFGer if different crs
            if crsDEM != crsFGer:
                res18 = processing.run("native:reprojectlayer", {
                    'INPUT': vlyr_tezg,
                    'TARGET_CRS': feingerinne,
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
                clipTEZG = res18['OUTPUT']
            else:
                clipTEZG = vlyr_tezg

            # Clip feingerinne to TEZG
            feingerinne_path = os.path.join(temp_folder, f"feingerinne_{uuid.uuid4().hex}.shp")
            res19 = processing.run("native:clip", {
                'INPUT': feingerinne,
                'OVERLAY': clipTEZG,
                'OUTPUT': feingerinne_path})

            # Reproject feingerinne to crsDEM if different crs
            feingerinne_path_reproj = os.path.join(temp_folder, f"feingerinne_reproj_{uuid.uuid4().hex}.shp")
            if crsDEM != crsFGer:
                res2 = processing.run("native:reprojectlayer", {
                    'INPUT': QgsVectorLayer(feingerinne_path, 'vlyr_srcFGer', 'ogr'),
                    'TARGET_CRS': dgm,  # dgm crs determines project crs
                    'OUTPUT': feingerinne_path_reproj})
                vlyr_srcFGer = QgsVectorLayer(feingerinne_path_reproj, 'vlyr_srcFGer', 'ogr')
                drainage_path = feingerinne_path_reproj
            else:
                vlyr_srcFGer = QgsVectorLayer(feingerinne_path, 'vlyr_srcFGer', 'ogr')
                drainage_path = feingerinne_path
            # Set layer name and add to lyrList
            # vlyr_srcFGer.setName('vlyr_srcFGer')
            lyrList.append(vlyr_srcFGer)
            drainage = vlyr_srcFGer


        # --- CLIP DEM TO TEZG BOUNDARY ---

        # Clip DEM
        feedback.pushInfo("... clipping dem to area of interest")
        
        res4 = processing.run("gdal:cliprasterbymasklayer", {
            'INPUT': dgm,
            'MASK': vlyr_tezg,
            #'TARGET_CRS': dgm.crs().authid(),
            'NODATA': 99999,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 6,  # Float32
            'OUTPUT': 'TEMPORARY_OUTPUT'})
        rlyr_demClp = QgsRasterLayer(res4['OUTPUT'], "rlyr_demClp", "gdal")
        lyrList.append(rlyr_demClp)

        # --- CALCULATE HYDROLOGICAL Rasters ---
        feedback.pushInfo("... calculating hydrological rasters")
        # Redirect stdout to avoid the NoneType error in flush()
        with contextlib.redirect_stdout(io.StringIO()):
            # Create a hydrologically corrected DEM (Digital Elevation Model)
            corrected_dem_path = os.path.join(temp_folder, f"DEM_Corrected_{uuid.uuid4().hex}.tif")
            # Perform depression filling on DEM to create a hydrologically corrected DEM
            wbt.fill_depressions_wang_and_liu(
                dem=rlyr_demClp.dataProvider().dataSourceUri(),
                output=corrected_dem_path,
                fix_flats=True,
                flat_increment=None,
                callback = my_callback
            )
            rlyr_demFilled = QgsRasterLayer(corrected_dem_path, "rlyr_demFilled", "gdal")
            lyrList.append(rlyr_demFilled)

            # Calculate flow accumulation raster (for ridge detection)
            flow_accumulation_path = os.path.join(temp_folder, f"Flow_Accumulation_{uuid.uuid4().hex}.tif")

            # Calculate flow accumulation raster using D8 algorithm
            wbt.d8_flow_accumulation(
                corrected_dem_path,
                output=flow_accumulation_path,
                out_type="cells",  # Output type set to "cells" for cell-based flow accumulation
                log=False,
                clip=False,
                pntr=False,
                esri_pntr=False,
            )
            rlyr_demFAcc = QgsRasterLayer(flow_accumulation_path, "rlyr_demFAcc", "gdal")
            lyrList.append(rlyr_demFAcc)

            # Reclassify flowacc to get ridges (acc val = 1,2)
            stats = rlyr_demFAcc.dataProvider().bandStatistics(1)

            res4 = processing.run("native:reclassifybytable", {
                'INPUT_RASTER': rlyr_demFAcc,
                'RASTER_BAND': 1,
                'TABLE': ['1', '2', '1', '3', stats.maximumValue, '0'],
                'NO_DATA': 0, 'RANGE_BOUNDARIES': 2, 'NODATA_FOR_MISSING': False,
                'DATA_TYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            rlyr_demFAccRecl = QgsRasterLayer(res4['OUTPUT'], "rlyr_demFAccRecl", "gdal")
            lyrList.append(rlyr_demFAccRecl)


            # # --- OVERLAND FLOW LENGTH AT RIDGES---
            feedback.pushInfo("... calculating max flowlength from ridges")

            # Create a path for the rasterized streams output
            rasterized_streams_path = os.path.join(temp_folder, f"Rasterized_Streams_{uuid.uuid4().hex}.tif")

            # Rasterize streams based on the corrected DEM
            wbt.rasterize_streams(
                streams=drainage_path,
                base=corrected_dem_path,
                output=rasterized_streams_path,
                feature_id=False
            )
            rlyr_rasDrain = QgsRasterLayer(rasterized_streams_path, "rlyr_rasDrain", "gdal")
            lyrList.append(rlyr_rasDrain)

            # Create a path for the overland flow length output
            flow_length_path = os.path.join(temp_folder, f"Flow_Length_{uuid.uuid4().hex}.tif")

            # Calculate overland flow length
            wbt.downslope_distance_to_stream(
                dem=corrected_dem_path,
                streams=rasterized_streams_path,
                output=flow_length_path,
                dinf=False
            )
            rlyr_demFLen = QgsRasterLayer(flow_length_path, "rlyr_demFLen", "gdal")
            lyrList.append(rlyr_demFLen)

            # Multiply reclassified flowacc with flow length to overland flow length ridges
            multiplied_raster_path = os.path.join(temp_folder, f"Flow_Length_Ridges_{uuid.uuid4().hex}.tif")

            wbt.raster_calculator(
                output=multiplied_raster_path,
                statement=f'"{rlyr_demFLen.dataProvider().dataSourceUri()}" * "{rlyr_demFAccRecl.dataProvider().dataSourceUri()}"'
            )
            # Load the multiplied raster layer in QGIS
            rlyr_demFLenRidges = QgsRasterLayer(multiplied_raster_path, "rlyr_demFLenRidges", "gdal")
            lyrList.append(rlyr_demFLenRidges)



        ## --- Calculate TEZG Area Attributes ---
        feedback.pushInfo("... calculating TEZG area attributes and adding them to dictionary")

        # --- Slope ---
        res11 = processing.run("gdal:slope", {
            'INPUT': rlyr_demClp,
            'BAND': 1,
            'AS_PERCENT': True,
            'ZEVENBERGEN': False,
            # Tried both HORN (default) and ZEVENBERGEN & THORNE method, HORN closer to ArcGIS output.
            'OPTIONS': '',
            'OUTPUT': 'TEMPORARY_OUTPUT'})
        rlyr_demSlp = QgsRasterLayer(res11['OUTPUT'], "rlyr_demSlp", "gdal")
        lyrList.append(rlyr_demSlp)

        # Calculate statistics, adding mean slope to TEZG
        processing.run("qgis:zonalstatistics", {
            'INPUT_RASTER': rlyr_demSlp,
            'RASTER_BAND': 1,
            'INPUT_VECTOR': vlyr_tezg,
            'COLUMN_PREFIX': 'slpP',
            'STATS': [2]})  # Mean

        # Delete and reload vtezg with new attributes
        del vlyr_tezg
        vlyr_tezg = res3['OUTPUT']

        # Add slope data to output dictionary
        feats = vlyr_tezg.getFeatures()
        for feat in feats:
            fid = int(feat['TEZG_ID_ZK'])
            dictCsv[fid]['F-Neigung [1]'] = str(round(feat['slpPmean'] / 100, 3)).replace('.', ',')

        ##--- Average max flow length ---

        # Calculate statistics, adding mean slope to TEZG
        processing.run("qgis:zonalstatistics", {
            'INPUT_RASTER': rlyr_demFLenRidges,
            'RASTER_BAND': 1,
            'INPUT_VECTOR': vlyr_tezg,
            'COLUMN_PREFIX': 'flenM',
            'STATS': [0, 2, 5, 6]})  # Count, Mean, Min, Max

        # # Delete and reload vtezg with new attributes
        del vlyr_tezg
        vlyr_tezg = res3['OUTPUT']

        # Add average max flow length to output dictionary
        feats = vlyr_tezg.getFeatures()
        for feat in feats:
            fid = int(feat['TEZG_ID_ZK'])
            dictCsv[fid]['F-Laenge [m]'] = str(round(feat['flenMmean']))

        ## -------------------------------------------------
        # --- CALCULATE AKL & RKL DISTRIBUTION IN TEZGS ---
        feedback.pushInfo("... calculating AKL and RKL distribution and adding them to dictionary")

        # -- AKL -- #

        # Reproject TEZG to crsAKL if different crs
        if crsDEM != crsAKL:
            res12 = processing.run("native:reprojectlayer", {
                'INPUT': vlyr_tezg,
                'TARGET_CRS': beiwert,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            clipTEZG = res12['OUTPUT']
        else:
            clipTEZG = vlyr_tezg

        # Intersect TEZG and AKL
        res13 = processing.run("native:intersection", {
            'INPUT': beiwert,
            'OVERLAY': clipTEZG,
            'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [],
            'OUTPUT': 'TEMPORARY_OUTPUT'})

        # Reproject AKL to crsDEM if different crs
        if crsDEM != crsAKL:
            res20 = processing.run("native:reprojectlayer", {
                'INPUT': res13['OUTPUT'],
                'TARGET_CRS': dgm,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            vlyr_tezgAKL = res20['OUTPUT']
        else:
            vlyr_tezgAKL = res13['OUTPUT']

        # Set layer name and add to lyrList
        vlyr_tezgAKL.setName('vlyr_tezgAKL')
        lyrList.append(vlyr_tezgAKL)

        # Calculate area per AKLVal per TEZG and add to dictCsv
        aklVal = [0, 1, 2, 3, 4, 5, 6]
        for val in aklVal:
            for fid in fidVal:
                area = 0
                featsAKL = vlyr_tezgAKL.getFeatures()
                for feat in featsAKL:
                    if feat[beiwertVal] == val and int(feat['TEZG_ID_ZK']) == fid:
                        area += feat.geometry().area()
                    dictCsv[fid]['AKL-{}'.format(val)] = round(area)

        # -- RKL -- #

        # Reproject TEZG to crsRKL if different crs
        if crsDEM != crsRKL:
            res14 = processing.run("native:reprojectlayer", {
                'INPUT': vlyr_tezg,
                'TARGET_CRS': rauhigkeit,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            clipTEZG = res14['OUTPUT']
        else:
            clipTEZG = vlyr_tezg

        res15 = processing.run("native:intersection", {
            'INPUT': rauhigkeit,
            'OVERLAY': clipTEZG,
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': [],
            'OUTPUT': 'TEMPORARY_OUTPUT'})

        if crsDEM != crsRKL:
            res21 = processing.run("native:reprojectlayer", {
                'INPUT': res15['OUTPUT'],
                'TARGET_CRS': dgm,
                'OUTPUT': 'TEMPORARY_OUTPUT'})
            vlyr_tezgRKL = res21['OUTPUT']
        else:
            vlyr_tezgRKL = res15['OUTPUT']

        # Set layer name and add to lyrList
        vlyr_tezgRKL.setName('vlyr_tezgRKL')
        lyrList.append(vlyr_tezgRKL)

        # Calculate area per RKLVal per TEZG and add to dictCsv
        rklVal = [1, 2, 3, 4, 5, 6]
        for val in rklVal:
            for fid in fidVal:
                area = 0
                featsRKL = vlyr_tezgRKL.getFeatures()
                for feat in featsRKL:
                    if feat[rauhigkeitVal] == val and int(feat['TEZG_ID_ZK']) == fid:
                        area += feat.geometry().area()
                    dictCsv[fid]['RKL-{}'.format(val)] = round(area)

        ## ----------------------------------------------------
        # --- CALCULATE WEIGHTED MEAN ZAF AND ZAA PER TEZGS ---
        feedback.pushInfo("... calculating weighted mean ZAF and ZAA and adding them to dictionary")

        if zaSrc:
            # Reproject TEZG to crsZA if different crs
            if crsDEM != crsZA:
                res22 = processing.run("native:reprojectlayer", {
                    'INPUT': vlyr_tezg,
                    'TARGET_CRS': zaSrc,
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
                clipTEZG = res22['OUTPUT']
            else:
                clipTEZG = vlyr_tezg

            # Intersect TEZG and ZA
            res23 = processing.run("native:intersection", {
                'INPUT': zaSrc,
                'OVERLAY': clipTEZG,
                'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [],
                'OUTPUT': 'TEMPORARY_OUTPUT'})

            # Reproject ZA to crsDEM if different crs
            if crsDEM != crsZA:
                res24 = processing.run("native:reprojectlayer", {
                    'INPUT': res23['OUTPUT'],
                    'TARGET_CRS': dgm,
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
                vlyr_tezgZA = res24['OUTPUT']
            else:
                vlyr_tezgZA = res23['OUTPUT']

            vlyr_tezgZA.setName('vlyr_tezgZA')
            lyrList.append(vlyr_tezgZA)

            ## --- ZAF --- #

            # Create ZAF raster of DEM cellsize
            res25 = processing.run("gdal:rasterize",
                                   {'INPUT': vlyr_tezgZA,
                                    'FIELD': zafVal,
                                    'BURN': 0,
                                    'UNITS': 1,
                                    'WIDTH': cellsize,
                                    'HEIGHT': cellsize,
                                    'EXTENT': vlyr_tezgZA,
                                    'NODATA': -9999,
                                    'OPTIONS': '',
                                    'DATA_TYPE': 5,  # Float32
                                    'INIT': None, 'INVERT': False,
                                    'EXTRA': '-tap',  # Aligns raster to DEM cells
                                    'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_rasTezgZAF = QgsRasterLayer(res25['OUTPUT'], "rlyr_rasTezgZAF", "gdal")
            lyrList.append(rlyr_rasTezgZAF)

            # Reclassify ZAF raster
            res26 = processing.run("native:reclassifybytable", {
                'INPUT_RASTER': rlyr_rasTezgZAF,
                'RASTER_BAND': 1,
                'TABLE': [1, 1, 1, 2, 2, 2, 3, 3, 3],
                'NO_DATA': -9999,
                'RANGE_BOUNDARIES': 2,
                'NODATA_FOR_MISSING': True,
                'DATA_TYPE': 5,
                'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_rasTezgZAF_recl = QgsRasterLayer(res26['OUTPUT'], "rlyr_rasTezgZAF_recl", "gdal")
            lyrList.append(rlyr_rasTezgZAF_recl)

            ## --- ZAA --- #

            # Create raster of DEM cellsize
            res27 = processing.run("gdal:rasterize",
                                   {'INPUT': vlyr_tezgZA,
                                    'FIELD': zaaVal,
                                    'BURN': 0,
                                    'UNITS': 1,
                                    'WIDTH': cellsize,
                                    'HEIGHT': cellsize,
                                    'EXTENT': vlyr_tezgZA,
                                    'NODATA': -9999,
                                    'OPTIONS': '',
                                    'DATA_TYPE': 5,  # Float32
                                    'INIT': None, 'INVERT': False,
                                    'EXTRA': '-tap',
                                    'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_rasTezgZAA = QgsRasterLayer(res27['OUTPUT'], "rlyr_rasTezgZAA", "gdal")
            lyrList.append(rlyr_rasTezgZAA)

            # Reclassify raster according to values of reclassified ZAF
            res28 = processing.run("gdal:rastercalculator", {
                'INPUT_A': rlyr_rasTezgZAF_recl,
                'BAND_A': 1,
                'INPUT_B': rlyr_rasTezgZAA,
                'BAND_B': 1,
                'FORMULA': '(A > 0) * B',
                'NO_DATA': -9999,
                'RTYPE': 5,
                'OPTIONS': '', 'EXTRA': '',
                'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_rasTezgZAA_recl = QgsRasterLayer(res28['OUTPUT'], "rlyr_rasTezgZAA_recl", "gdal")
            lyrList.append(rlyr_rasTezgZAA_recl)

            ## --- Calculate weighted means for ZAF and ZAA per TEZG --- ##
            # Source: "P:\NR\BMLF\WLV\PROJEKTE\PYQGIS\Zemokost\DATA_IN\BMNT_20200316\Zemokost_Erweiterung Zwischenabfluss.docx"

            # -- ZAF  [Gew. rZAF = summenprodukt(rZAF * rZAA) / summe(rZAA)]

            # Calculate raster rZAF * rZAA
            res29 = processing.run("gdal:rastercalculator", {
                'INPUT_A': rlyr_rasTezgZAF_recl,
                'BAND_A': 1,
                'INPUT_B': rlyr_rasTezgZAA_recl,
                'BAND_B': 1,
                'FORMULA': 'A*B',
                'NO_DATA': -9999,
                'RTYPE': 5,
                'OPTIONS': '', 'EXTRA': '',
                'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_ras_rZAF_x_rZAA = QgsRasterLayer(res29['OUTPUT'], "rlyr_ras_rZAF_x_rZAA", "gdal")
            lyrList.append(rlyr_ras_rZAF_x_rZAA)

            # Calculate sumproduct(rZAF * rZAA) per TEZG (= SP1)
            processing.run("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_ras_rZAF_x_rZAA,
                'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'SP1_',
                'STATS': [1]})

            # Calculate sum(rZAA) per TEZG (= S1)
            processing.run("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_rasTezgZAA_recl,
                'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'S1_',
                'STATS': [1]})

            # -- ZAA  [Gew. rZAA = summenprodukt(cellsize* rZAA) / summe(cellsize of ZAA) * 100]

            # # Calculate raster cellsize * rZAA
            res30 = processing.run("gdal:rastercalculator", {
                'INPUT_A': rlyr_rasTezgZAA_recl,
                'BAND_A': 1,
                'FORMULA': '{}*A'.format(cellsize),
                'NO_DATA': -9999,
                'RTYPE': 5,
                'OPTIONS': '', 'EXTRA': '',
                'OUTPUT': 'TEMPORARY_OUTPUT'})

            rlyr_ras_cellsize_x_rZAA = QgsRasterLayer(res30['OUTPUT'], "rlyr_ras_cellsize_x_rZAA", "gdal")
            lyrList.append(rlyr_ras_cellsize_x_rZAA)

            # Calculate sumproduct(cellsize * rZAA) per TEZG (= SP2)
            processing.run("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_ras_cellsize_x_rZAA,
                'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'SP2_',
                'STATS': [1]})

            # Count grid cells ZAA (before reclassify) per TEZG  (= C2)
            processing.run("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_rasTezgZAA,
                'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'C2_',  # cell count x cell size = sum(cellsize)
                'STATS': [0]})

            # --- Calculate weighted means for ZAF and ZAA and add to dictionary
            featsZA = vlyr_tezg.getFeatures()
            for feat in featsZA:
                fid = int(feat['TEZG_ID_ZK'])
                if feat['s1_sum'] != 0:
                    # Weighted mean ZAF                
                    wZAF = feat['SP1_sum'] / feat['s1_sum']
                    dictCsv[fid]['ZAF 1 bis 7'] = str(round(wZAF, 4)).replace('.', ',')
                    # Weighted mean ZAA
                    wZAA = (feat['SP2_sum'] / (feat['C2_count'] * cellsize)) * 100
                    dictCsv[fid]['Anteil [%]'] = str(round(wZAA, 4)).replace('.', ',')

        # # -----------------------------------
        # --- CALCULATE CHANNEL STATISTICS ---
        feedback.pushInfo("... calculating channel attributes and adding them to dictionary")

        # Intersect coarse drainage with tezgs
        res16 = processing.run("native:intersection", {
            'INPUT': vlyr_srcGer,
            'OVERLAY': vlyr_tezg,
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': [],
            'OUTPUT': 'TEMPORARY_OUTPUT'})

        # Dissolve by tezg
        res17 = processing.run("native:dissolve", {
            'INPUT': res16['OUTPUT'],
            'FIELD': ['TEZG_ID_ZK'],
            'OUTPUT': QgsProcessingUtils.tempFolder() + '/OUTPUT' + str(random.getrandbits(128)) + '.shp'})
        vlyr_tezgGer_dis = QgsVectorLayer(res17['OUTPUT'], 'vlyr_tezgGer_dis', 'ogr')
        # vlyr_tezgGer_dis.setName('vlyr_tezgGer_dis')
        lyrList.append(vlyr_tezgGer_dis)

        # Calculate coarse drainage length per tezg and add to dictCsv

        featsGer = vlyr_tezgGer_dis.getFeatures()
        for feat in featsGer:
            fid = int(feat['TEZG_ID_ZK'])
            length = feat.geometry().length()
            dictCsv[fid]['G-Laenge [m]'] = str(round(length, 1)).replace('.', ',')

        # Rasterize vtezgGer    # GDAL and SAGA rasterize (s. res8) produce slightly different drainage raster, possibly necessary to align methods
        res18 = processing.run("gdal:rasterize", {
            'INPUT': vlyr_tezgGer_dis,
            'FIELD': 'TEZG_ID_ZK',
            'BURN': None,
            'UNITS': 1,
            'WIDTH': cellsize,
            'HEIGHT': cellsize,
            'EXTENT': rlyr_demFilled,
            'NODATA': None,
            'OPTIONS': '',
            'DATA_TYPE': 5,
            'INIT': None,
            'INVERT': False,
            'OUTPUT': 'TEMPORARY_OUTPUT'})
        rlyr_rasTezgGer = QgsRasterLayer(res18['OUTPUT'], "rlyr_rasTezgGer", "gdal")
        lyrList.append(rlyr_rasTezgGer)

        # Calculate channel altitude range in TEZGs
        res19 = processing.run("native:rasterlayerzonalstats", {
            'INPUT': rlyr_demClp,
            'BAND': 1,
            'ZONES': rlyr_rasTezgGer,
            'ZONES_BAND': 1,
            'REF_LAYER': 1,
            'OUTPUT_TABLE': 'TEMPORARY_OUTPUT'})
        vlyr_tezgGerStats = res19['OUTPUT_TABLE']
        vlyr_tezgGerStats.setName('vlyr_tezgGerStats')
        lyrList.append(vlyr_tezgGerStats)

        # Calculate channel slope
        feats = vlyr_tezgGerStats.getFeatures()
        for feat in feats:
            fid = int(float(feat['zone']))
            if fid != 0:
                elevRange = float(feat['max']) - float(feat['min'])
                length = float(dictCsv[fid]['G-Laenge [m]'].replace(',', '.'))
                chSlp = elevRange / length
                dictCsv[fid]['G-Neigung [1]'] = str(round(chSlp, 3)).replace('.', ',')

        ## --- CREATE OUTPUT CSV ---
        feedback.pushInfo("... saving dictionary in output csv")

        # Sort dictCSV in reversed order
        dictCsvRev = dict(sorted(dictCsv.items(), reverse=True))

        ## Write to csv

        outCsv = os.path.join(wDir, 'import_zemokost.csv')
        with open(outCsv, mode='w', newline='') as file:
            fieldnames = ['TEZG Nr.', 'K.O.', 'K.U.', 'Bezeichnung/Ergaenzung', 'X', 'Y', 'Flaeche [km2]',
                          'F-Laenge [m]',
                          'F-Neigung [1]', 'Nat. Ret.[%]', 'Basisabfl. [m3/s]', 'AKL-0', 'AKL-1', 'AKL-2', 'AKL-3',
                          'AKL-4', 'AKL-5', 'AKL-6', 'RKL-1', 'RKL-2', 'RKL-3', 'RKL-4', 'RKL-5', 'RKL-6',
                          'ZAF 1 bis 7', 'Anteil [%]', 'G-Laenge [m]', 'G-Neigung [1]', 'd90 [m]']
            writer = csv.DictWriter(file, delimiter=';', fieldnames=fieldnames)

            writer.writeheader()
            for key in dictCsvRev.keys():
                writer.writerow(dictCsvRev[key])
        
        ## --- WRITE TEMP DATA TO FOLDER ---

        if keepDataBOOL:
            feedback.pushInfo("... saving temp data to output folder")
            # feedback.pushInfo(f"... {lyrList}")
            for i in lyrList:
                if i.name().startswith('rlyr_'):
                    processing.run("gdal:translate", {
                        'INPUT': i,
                        'TARGET_CRS': i.crs(),
                        'NODATA': None, 'COPY_SUBDATASETS': False,
                        'OPTIONS': '', 'DATA_TYPE': 0,  # Use input layer data type
                        'OUTPUT': eval(i.name()[5:])})

                if i.name().startswith('vlyr_') and i.name() != 'vlyr_tezgGerStats':
                    QgsVectorFileWriter.writeAsVectorFormat(i, eval(i.name()[5:]), 'utf-8', i.crs(), 'ESRI Shapefile')

                if i.name() == 'vlyr_tezgGerStats':
                    QgsVectorFileWriter.writeAsVectorFormat(vlyr_tezgGerStats, tezgGerStats, 'utf-8', i.crs(), 'CSV')
        delete_temp_files(temp_folder)
        feedback.pushInfo("\nFINISHED ......................")

        results = {}
        results['OUTPUT'] = outCsv

        # Display a warning if any polygon is smaller than 100 m²
        if has_small_area:
            QMessageBox.warning(None, "Warning", "Eines oder mehrere Polygone im TEZG sind kleiner als 100 m².")
        return results
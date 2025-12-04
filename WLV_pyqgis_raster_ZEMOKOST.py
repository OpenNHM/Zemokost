# -*- coding: utf-8 -*-
"""
Toolbox: WLV_Tools
Script: Aufbereitung ZEMOKOST (Raster only), Version 1.0.0 (patched)
Author: BK(BFW); KS, NC, BT (ms.gis,); JK(WLV)
 Anpassung/Fix des WLV_pyqgis_ZEMOKOST_1_5_0.py an Rastereingabe
QGIS Version: >= 3.40.9
Created: 2025-10-15

Kurzbeschreibung
- TEZG (Polygon), Gerinne (Linie) und DEM (Raster) wie gehabt.
- AKL und RKL als Float-Raster: je TEZG lineare Aufteilung in Klassenanteile (AKL 0..6, RKL 1..6).
- ZAF (Raster): wZAF = Mittel aus ZAF<=4; ZAA [%] = Anteil ZAF<=4-Zellen je TEZG.
Hydrologie (wie WLV):
- Clip DEM -> Fill Depressions (Wang & Liu) -> D8 Flow Accumulation (cells)
 -> Ridge-Reklassifikation (1/2->1, sonst 0)
 -> Rasterize Streams (Haupt/optional Feingerinne)
 -> Downslope Distance to Stream
 -> FlowLen × Ridge
 -> Slope (%) -> Zonalstats (F-Länge, F-Neigung), Kanalstatistik (Länge/Gefälle)
"""
import csv
import os
import uuid
import sys
import random
import contextlib
import io
import shutil
import traceback
import platform
from PyQt5.QtCore import (QCoreApplication, QVariant)
from osgeo import gdal
from qgis import processing
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterBoolean,  # (historisch; hier nicht verwendet)
    QgsProcessingParameterFileDestination,  # Pflicht-Output (wie SmokeTest)
    QgsRasterLayer,
    QgsField,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsProcessingException,
    QgsProcessingUtils,
    QgsVectorLayer,
)

# --- Unterdrücke WhiteboxTools-Konsolenfenster unter Windows ---
if platform.system().lower().startswith("win"):
    os.environ.setdefault("WBT_HIDE_CONSOLE", "TRUE")
    os.environ.setdefault("WBT_DISABLE_PROGRESS_BAR", "TRUE")

# WhiteboxTools (wie im WLV-Skript)
home_dir = os.path.expanduser("~")
script_path = os.path.join(
    home_dir, "AppData", "Roaming", "QGIS", "QGIS3",
    "profiles", "default", "processing", "scripts"
)
sys.path.append(script_path)
from WBT.whitebox_tools import WhiteboxTools  # noqa: E402


def delete_temp_files(temp_folder: str):
    for item in os.listdir(temp_folder):
        item_path = os.path.join(temp_folder, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except PermissionError:
            # Ignoriere gesperrte Dateien
            pass


def _wbt_safecall(func, *args, **kwargs):
    """WhiteboxTools-Aufruf: stdout stummschalten + tolerant bzgl. unbekannter kwargs (z.B. callback)."""
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Falls die Wrapper-Version 'callback' o.ä. nicht kennt -> ohne erneut versuchen
            trimmed = dict(kwargs)
            changed = False
            for k in ("callback", "compress_rasters", "num_threads"):
                if k in trimmed:
                    trimmed.pop(k, None)
                    changed = True
            if changed:
                return func(*args, **trimmed)
            raise


class ZEMOKOST_GISDaten_RasterOnly(QgsProcessingAlgorithm):
    # Parameter-IDs
    DEM = 'DEM'
    TEZG = 'TEZG'
    TEZG_ID = 'TEZG_ID'
    KNT_UPPER = 'KNTO'
    KNT_LOWER = 'KNTU'
    NAME = 'NAME'
    CHANNEL_MAIN = 'CHANNEL_MAIN'
    CHANNEL_HIGHRES = 'CHANNEL_HIGHRES'
    AKL_RASTER = 'AKL_RASTER'
    RKL_RASTER = 'RKL_RASTER'
    ZAF_RASTER = 'ZAF_RASTER'
    OUTPUT_CSV = 'OUTPUT_CSV'

    def tr(self, s): return QCoreApplication.translate('Processing', s)
    def createInstance(self): return ZEMOKOST_GISDaten_RasterOnly()
    def name(self): return 'zemokost_rasteronly'
    def displayName(self): return self.tr('Aufbereitung ZEMOKOST (Raster only)')
    def group(self): return self.tr('WLV Tools')
    def groupId(self): return 'scripts'
    def flags(self):
        # Standard-Flags (ohne FlagNoThreading) -> Hintergrund-Thread erlaubt
        return super().flags()
    def shortHelpString(self):
        return self.tr(
            "Rasterbasierte Aufbereitung für ZEMOKOST:\n"
            "- AKL/RKL Float-Raster -> Klassenanteile je TEZG.\n"
            "- ZAF (Raster) -> wZAF aus ZAF<=4; ZAA [%] = Anteil ZAF<=4."
        )

    def initAlgorithm(self, config=None):
        # DEM + TEZG + Felder
        self.addParameter(QgsProcessingParameterRasterLayer(self.DEM, self.tr('Höhenmodell (DEM)')))
        self.addParameter(QgsProcessingParameterVectorLayer(self.TEZG, self.tr('Teileinzugsgebietsflächen (TEZG)'),
                                                           [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterField(self.TEZG_ID, self.tr('TEZG-ID'), '', self.TEZG))
        self.addParameter(QgsProcessingParameterField(self.KNT_UPPER, self.tr('TEZG – Knoten oben'), '', self.TEZG))
        self.addParameter(QgsProcessingParameterField(self.KNT_LOWER, self.tr('TEZG – Knoten unten'), '', self.TEZG))
        self.addParameter(QgsProcessingParameterField(self.NAME, self.tr('TEZG – Bezeichnung'), '', self.TEZG, optional=True))
        # Gerinne
        self.addParameter(QgsProcessingParameterVectorLayer(self.CHANNEL_MAIN, self.tr('Hauptgerinne'),
                                                            [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterVectorLayer(self.CHANNEL_HIGHRES, self.tr('Feingerinne (optional)'),
                                                            [QgsProcessing.TypeVectorLine], optional=True))
        # Raster-only Inputs
        self.addParameter(QgsProcessingParameterRasterLayer(self.AKL_RASTER, self.tr('AKL (Float-Raster)')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.RKL_RASTER, self.tr('RKL (Float-Raster)')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.ZAF_RASTER, self.tr('ZAF (Raster)')))
        # Pflicht-Output (FileDestination)
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT_CSV, self.tr('Ergebnis-CSV'), self.tr('CSV files (*.csv)'), optional=False
        ))

    # --- Utilities ---
    @staticmethod
    def _extent_string(layer_or_raster) -> str:
        if isinstance(layer_or_raster, (QgsRasterLayer, QgsVectorLayer)):
            ext = layer_or_raster.extent()
        else:
            ext = layer_or_raster
        return f"{ext.xMinimum()},{ext.xMaximum()},{ext.yMinimum()},{ext.yMaximum()}"

    def _align_to_dem(self, in_ras, rlyr_demClp, cellsize, name, categorical=False, run=None):
        """
        Reproject/Resample in_ras auf DEM-Ausdehnung/Auflösung.
        - RESAMPLING: nearest (kategorisch) / bilinear (kontinuierlich)
        - SRC_NODATA: aus dem Quellband ausgelesen (falls vorhanden)
        - DST_NODATA: -9999 (nur gesetzt, wenn SRC_NODATA erkannt)
        - Datentyp: NICHT erzwingen (Float bleibt Float; kein -ot Int32)
        """
        resampling = 1 if not categorical else 0
        runner = run if callable(run) else processing.run
        # Source-NoData robust ermitteln
        try:
            src_path = in_ras.source() if hasattr(in_ras, 'source') else str(in_ras)
            ds = gdal.Open(src_path)
            src_nd = ds.GetRasterBand(1).GetNoDataValue() if ds else None
        except Exception:
            src_nd = None
        params = {
            'INPUT': in_ras,
            'SOURCE_CRS': None,
            'TARGET_CRS': rlyr_demClp.crs(),
            'RESAMPLING': resampling,
            # kein DATA_TYPE -> Originaltyp bleibt erhalten
            'TARGET_RESOLUTION': float(cellsize),
            'OPTIONS': '',
            'TARGET_EXTENT': self._extent_string(rlyr_demClp),
            'TARGET_EXTENT_CRS': rlyr_demClp.crs(),
            'MULTITHREADING': True,
            'EXTRA': '-tap',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        if src_nd is not None:
            params['SRC_NODATA'] = src_nd
            params['DST_NODATA'] = -9999
        res = runner("gdal:warpreproject", params)
        return QgsRasterLayer(res['OUTPUT'], name, "gdal")

    # --- Main ---
    def processAlgorithm(self, parameters, context, feedback, my_callback=None):
        feedback.pushInfo("SCRIPT VERSION: 1.3.0 (patched)")

        # STEP helper
        step = {"n": 0}
        TOTAL_STEPS = 31

        def check_cancel():
            if feedback.isCanceled():
                raise QgsProcessingException("Abgebrochen durch Benutzer.")

        def mark(msg):
            check_cancel()
            step["n"] += 1
            feedback.pushInfo(f"[STEP {step['n']:02d}] {msg}")
            try:
                p = int(step["n"] / TOTAL_STEPS * 100)
                feedback.setProgress(min(p, 99))
                if hasattr(feedback, "setProgressText"):
                    feedback.setProgressText(msg)
            except Exception:
                pass

        def prun(alg_id, params):
            check_cancel()
            return processing.run(alg_id, params, context=context, feedback=feedback)

        # --- PSI->AKL Stützstellen (U7:V17) und Mapping ---
        X_POINTS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.625, 0.75, 0.875, 1.0]
        Y_POINTS = [0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]

        def psi_to_akl_value(psi: float) -> float:
            x, y = X_POINTS, Y_POINTS
            if psi <= x[0]:
                return y[0]
            if psi >= x[-1]:
                return y[-1]
            for i in range(len(x) - 1):
                if x[i] <= psi <= x[i + 1]:
                    x0, x1 = x[i], x[i + 1]
                    y0, y1 = y[i], y[i + 1]
                    t = 0.0 if x1 == x0 else (psi - x0) / (x1 - x0)
                    return y0 + t * (y1 - y0)
            return y[-1]

        # Versionsrobuste Hülle für native:rasterlayerzonalstats (OUTPUT vs OUTPUT_TABLE)
        def run_rasterlayerzonalstats(raster_layer, band, zones_raster, zones_band, ref_layer, name="zstats"):
            params_common = {
                'INPUT': raster_layer,
                'RASTER_BAND': band,
                'ZONES': zones_raster,
                'ZONES_BAND': zones_band,
            }
            if ref_layer is not None:
                params_common['REF_LAYER'] = ref_layer
            try:
                # bevorzugt Tabellen-Ausgabe
                res = prun("native:rasterlayerzonalstats", {**params_common, 'OUTPUT_TABLE': 'TEMPORARY_OUTPUT'})
                out = res.get('OUTPUT_TABLE', None) or res.get('OUTPUT', None)
                if isinstance(out, QgsVectorLayer):
                    return out
                if isinstance(out, str):
                    return QgsVectorLayer(out, name, 'ogr')
                for k, v in res.items():
                    if isinstance(v, QgsVectorLayer):
                        return v
                raise QgsProcessingException("Unerwartete Rückgabe (OUTPUT_TABLE).")
            except Exception:
                res = prun("native:rasterlayerzonalstats", {**params_common, 'OUTPUT_TABLE': 'TEMPORARY_OUTPUT'})
                out = res.get('OUTPUT_TABLE', None) or res.get('OUTPUT', None)
                if isinstance(out, QgsVectorLayer):
                    return out
                if isinstance(out, str):
                    return QgsVectorLayer(out, name, 'ogr')
                for k, v in res.items():
                    if isinstance(v, QgsVectorLayer):
                        return v
                raise QgsProcessingException("Unerwartete Rückgabe (OUTPUT_TABLE).")

        try:
            # --- Whitebox init ---
            mark("Init WhiteboxTools")
            wbt = WhiteboxTools()
            try:
                if hasattr(wbt, "set_hide_console"):
                    wbt.set_hide_console(True)
            except Exception:
                pass
            try:
                wbt.set_verbose_mode(False)
            except Exception:
                pass
            if platform.system().lower().startswith("win"):
                os.environ["WBT_HIDE_CONSOLE"] = "TRUE"
                os.environ["WBT_DISABLE_PROGRESS_BAR"] = "TRUE"

            # Inputs
            mark("Read parameters")
            dgm = self.parameterAsRasterLayer(parameters, self.DEM, context)
            tezgSrc = self.parameterAsVectorLayer(parameters, self.TEZG, context)
            tezgNr = self.parameterAsString(parameters, self.TEZG_ID, context)
            knotenO = self.parameterAsString(parameters, self.KNT_UPPER, context)
            knotenU = self.parameterAsString(parameters, self.KNT_LOWER, context)
            bezeichnung = self.parameterAsString(parameters, self.NAME, context)
            gerinne = self.parameterAsVectorLayer(parameters, self.CHANNEL_MAIN, context)
            feingerinne = self.parameterAsVectorLayer(parameters, self.CHANNEL_HIGHRES, context)
            akl_ras_in = self.parameterAsRasterLayer(parameters, self.AKL_RASTER, context)
            rkl_ras_in = self.parameterAsRasterLayer(parameters, self.RKL_RASTER, context)
            zaf_ras_in = self.parameterAsRasterLayer(parameters, self.ZAF_RASTER, context)
            outCsv = self.parameterAsFileOutput(parameters, self.OUTPUT_CSV, context)
            feedback.pushInfo(f"OUTPUT_CSV path: {outCsv}")

            # DEM-CRS Fix
            mark("DEM CRS fix (if needed)")
            if os.path.basename(dgm.source()) == 'ALS_DGM_1m_AT_COG_20240110.tif':
                dgm.setCrs(QgsCoordinateReferenceSystem(31287, QgsCoordinateReferenceSystem.EpsgCrsId))

            # CRS-Checks
            mark("CRS checks")
            crit = [dgm, tezgSrc, gerinne, feingerinne, akl_ras_in, rkl_ras_in, zaf_ras_in]
            bad = []
            for lyr in crit:
                try:
                    if lyr and lyr.crs().authid() == '' and lyr.source() not in bad:
                        bad.append(lyr.source())
                except AttributeError:
                    pass
            if bad:
                raise QgsProcessingException('!!ACHTUNG!! CRS der folgenden Layer unlesbar:\n' + '\n'.join(bad))

            feedback.pushInfo("\nSTARTING (Raster only) ......................")

            # Zellgröße
            mark("Open DEM & cellsize")
            ds = gdal.Open(dgm.source())
            if ds is None:
                raise QgsProcessingException(f"DEM konnte nicht geöffnet werden: {dgm.source()}")
            cellsize = float(ds.GetGeoTransform()[1])

            # Temp-Ordner
            mark("Prepare temp folder")
            temp_folder = QgsProcessingUtils.tempFolder()
            lyrList = []

            # TEZG -> DEM-CRS
            mark("Reproject TEZG to DEM CRS")
            res3 = prun("native:reprojectlayer", {
                'INPUT': tezgSrc, 'TARGET_CRS': dgm, 'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            vlyr_tezg = res3['OUTPUT']; vlyr_tezg.setName('vlyr_tezg'); lyrList.append(vlyr_tezg)

            # kleine Flächen?
            mark("Check small polygons")
            has_small = any(f.geometry().area() < 100.0 for f in vlyr_tezg.getFeatures())

            # TEZG Felder
            mark("Add TEZG fields & centroids")
            prov = vlyr_tezg.dataProvider()
            prov.addAttributes([
                QgsField('TEZG_ID_ZK', QVariant.String),
                QgsField('ctr_x', QVariant.Double),
                QgsField('ctr_y', QVariant.Double)
            ])
            vlyr_tezg.updateFields(); vlyr_tezg.startEditing()
            for f in vlyr_tezg.getFeatures():
                c = f.geometry().centroid().asPoint()
                f['ctr_x'] = c.x(); f['ctr_y'] = c.y(); f['TEZG_ID_ZK'] = int(f[tezgNr])
                vlyr_tezg.updateFeature(f)
            check_cancel()
            vlyr_tezg.commitChanges()

            # CSV-Init
            mark("Init CSV dict")
            dictCsv = {}
            fid_list = []
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK'])
                fid_list.append(fid)
                dictCsv[fid] = {}
                dictCsv[fid]['TEZG Nr.'] = fid
                dictCsv[fid]['K.O.'] = str(f[knotenO]).replace('.', ',')
                dictCsv[fid]['K.U.'] = str(f[knotenU]).replace('.', ',')
                dictCsv[fid]['X'] = str(f['ctr_x']).replace('.', ',')
                dictCsv[fid]['Y'] = str(f['ctr_y']).replace('.', ',')
                if bezeichnung != '':
                    dictCsv[fid]['Bezeichnung/Ergaenzung'] = f[bezeichnung]
                dictCsv[fid]['Flaeche [km2]'] = str(round(f.geometry().area() / 1_000_000, 4)).replace('.', ',')

            # DEM clip
            mark("Clip DEM to TEZG")
            res4 = prun("gdal:cliprasterbymasklayer", {
                'INPUT': dgm, 'MASK': vlyr_tezg, 'NODATA': 99999,
                'CROP_TO_CUTLINE': True, 'DATA_TYPE': 6, 'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            rlyr_demClp = QgsRasterLayer(res4['OUTPUT'], "rlyr_demClp", "gdal"); lyrList.append(rlyr_demClp)

            # ------- Hydro -------
            mark("WBT fill_depressions_wang_and_liu")
            dem_corr = os.path.join(temp_folder, f"dem_corr_{uuid.uuid4().hex}.tif")
            _wbt_safecall(
                wbt.fill_depressions_wang_and_liu,
                rlyr_demClp.dataProvider().dataSourceUri(), dem_corr,
                True, None
            )
            rlyr_demFilled = QgsRasterLayer(dem_corr, "rlyr_demFilled", "gdal"); lyrList.append(rlyr_demFilled)

            mark("WBT d8_flow_accumulation")
            facc = os.path.join(temp_folder, f"facc_{uuid.uuid4().hex}.tif")
            _wbt_safecall(
                wbt.d8_flow_accumulation,
                dem_corr, facc, "cells"
            )
            rlyr_demFAcc = QgsRasterLayer(facc, "rlyr_demFAcc", "gdal"); lyrList.append(rlyr_demFAcc)

            mark("Reclassify ridges from FAC")
            stats = rlyr_demFAcc.dataProvider().bandStatistics(1)
            res_ridges = prun("native:reclassifybytable", {
                'INPUT_RASTER': rlyr_demFAcc, 'RASTER_BAND': 1,
                'TABLE': ['1', '2', '1', '3', stats.maximumValue, '0'],
                'NO_DATA': 0, 'RANGE_BOUNDARIES': 2, 'NODATA_FOR_MISSING': False,
                'DATA_TYPE': 5, 'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            rlyr_demFAccRecl = QgsRasterLayer(res_ridges['OUTPUT'], "rlyr_demFAccRecl", "gdal"); lyrList.append(rlyr_demFAccRecl)

            # Gerinne
            mark("Clip/reproject channels")
            crsDEM = dgm.crs().authid().split(':')[1]
            crsGer = gerinne.crs().authid().split(':')[1]
            if feingerinne:
                crsFGer = feingerinne.crs().authid().split(':')[1]

            if crsDEM != crsGer:
                res_te_reproj = prun("native:reprojectlayer", {'INPUT': vlyr_tezg, 'TARGET_CRS': gerinne, 'OUTPUT': 'TEMPORARY_OUTPUT'})
                clipTEZG_ger = res_te_reproj['OUTPUT']
            else:
                clipTEZG_ger = vlyr_tezg

            gerinne_path = os.path.join(temp_folder, f"gerinne_{uuid.uuid4().hex}.shp")
            res_g_clip = prun("native:clip", {'INPUT': gerinne, 'OVERLAY': clipTEZG_ger, 'OUTPUT': gerinne_path})
            vlyr_srcGer = QgsVectorLayer(res_g_clip['OUTPUT'], 'vlyr_srcGer', 'ogr')
            if crsDEM != crsGer:
                res_g_reproj = prun("native:reprojectlayer", {'INPUT': vlyr_srcGer, 'TARGET_CRS': dgm, 'OUTPUT': gerinne_path})
                vlyr_srcGer = QgsVectorLayer(res_g_reproj['OUTPUT'], 'vlyr_srcGer', 'ogr')
            lyrList.append(vlyr_srcGer)

            if feingerinne:
                if crsDEM != crsFGer:
                    res_te2 = prun("native:reprojectlayer", {'INPUT': vlyr_tezg, 'TARGET_CRS': feingerinne, 'OUTPUT': 'TEMPORARY_OUTPUT'})
                    clipTEZG2 = res_te2['OUTPUT']
                else:
                    clipTEZG2 = vlyr_tezg
                feingerinne_path = os.path.join(temp_folder, f"feingerinne_{uuid.uuid4().hex}.shp")
                res_fg = prun("native:clip", {'INPUT': feingerinne, 'OVERLAY': clipTEZG2, 'OUTPUT': feingerinne_path})
                if crsDEM != crsFGer:
                    feingerinne_path_reproj = os.path.join(temp_folder, f"feingerinne_reproj_{uuid.uuid4().hex}.shp")
                    res_fg2 = prun("native:reprojectlayer", {
                        'INPUT': QgsVectorLayer(feingerinne_path, 'vlyr_srcFGer', 'ogr'),
                        'TARGET_CRS': dgm, 'OUTPUT': feingerinne_path_reproj
                    })
                    vlyr_srcFGer = QgsVectorLayer(res_fg2['OUTPUT'], 'vlyr_srcFGer', 'ogr')
                else:
                    vlyr_srcFGer = QgsVectorLayer(feingerinne_path, 'vlyr_srcFGer', 'ogr')
                lyrList.append(vlyr_srcFGer)
                drainage_path = vlyr_srcFGer.source()
            else:
                drainage_path = vlyr_srcGer.source()

            mark("WBT rasterize_streams")
            rasStreams = os.path.join(temp_folder, f"streams_{uuid.uuid4().hex}.tif")
            _wbt_safecall(
                wbt.rasterize_streams,
                drainage_path, dem_corr, rasStreams, False
            )
            rlyr_rasDrain = QgsRasterLayer(rasStreams, "rlyr_rasDrain", "gdal"); lyrList.append(rlyr_rasDrain)

            mark("WBT downslope_distance_to_stream")
            flen = os.path.join(temp_folder, f"flen_{uuid.uuid4().hex}.tif")
            _wbt_safecall(
                wbt.downslope_distance_to_stream,
                dem_corr, rasStreams, flen, False
            )
            rlyr_demFLen = QgsRasterLayer(flen, "rlyr_demFLen", "gdal"); lyrList.append(rlyr_demFLen)

            mark("WBT raster_calculator (FlowLen×Ridge)")
            flen_ridges = os.path.join(temp_folder, f"flen_ridges_{uuid.uuid4().hex}.tif")
            _wbt_safecall(
                wbt.raster_calculator, flen_ridges,
                f'"{rlyr_demFLen.dataProvider().dataSourceUri()}" * '
                f'"{rlyr_demFAccRecl.dataProvider().dataSourceUri()}"'
            )
            rlyr_demFLenRidges = QgsRasterLayer(flen_ridges, "rlyr_demFLenRidges", "gdal"); lyrList.append(rlyr_demFLenRidges)

            # Slope/Zonal
            mark("GDAL slope")
            res_slope = prun("gdal:slope", {
                'INPUT': rlyr_demClp, 'BAND': 1, 'AS_PERCENT': True, 'ZEVENBERGEN': False,
                'OPTIONS': '', 'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            rlyr_demSlp = QgsRasterLayer(res_slope['OUTPUT'], "rlyr_demSlp", "gdal"); lyrList.append(rlyr_demSlp)

            mark("Zonalstats slope")
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_demSlp, 'RASTER_BAND': 1, 'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'slpP', 'STATS': [2]
            })
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK'])
                mean_val = f['slpPmean']
                dictCsv[fid]['F-Neigung [1]'] = str(round((mean_val / 100) if mean_val is not None else 0, 3)).replace('.', ',')

            mark("Zonalstats flowlen×ridge")
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_demFLenRidges, 'RASTER_BAND': 1, 'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'flenM', 'STATS': [0, 2, 5, 6]
            })
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK'])
                dictCsv[fid]['F-Laenge [m]'] = str(round(f['flenMmean'] if f['flenMmean'] is not None else 0)).replace('.', ',')

            # Kanalstatistik
            mark("Channel stats (length/slope)")
            res_g_inter = prun("native:intersection", {
                'INPUT': QgsVectorLayer(vlyr_srcGer.source(), 'vlyr_srcGer', 'ogr'),
                'OVERLAY': vlyr_tezg, 'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [],
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            res_g_diss = prun("native:dissolve", {
                'INPUT': res_g_inter['OUTPUT'], 'FIELD': ['TEZG_ID_ZK'],
                'OUTPUT': QgsProcessingUtils.tempFolder() + '/OUTPUT' + str(random.getrandbits(128)) + '.shp'
            })
            vlyr_tezgGer_dis = QgsVectorLayer(res_g_diss['OUTPUT'], 'vlyr_tezgGer_dis', 'ogr'); lyrList.append(vlyr_tezgGer_dis)
            for f in vlyr_tezgGer_dis.getFeatures():
                fid = int(f['TEZG_ID_ZK']); L = f.geometry().length()
                dictCsv[fid]['G-Laenge [m]'] = str(round(L, 1)).replace('.', ',')

            res_g_ras = prun("gdal:rasterize", {
                'INPUT': vlyr_tezgGer_dis, 'FIELD': 'TEZG_ID_ZK',
                'BURN': None, 'UNITS': 1, 'WIDTH': cellsize, 'HEIGHT': cellsize,
                'EXTENT': rlyr_demFilled, 'NODATA': None, 'OPTIONS': '',
                'DATA_TYPE': 5, 'INIT': None, 'INVERT': False,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            rlyr_rasTezgGer = QgsRasterLayer(res_g_ras['OUTPUT'], "rlyr_rasTezgGer", "gdal"); lyrList.append(rlyr_rasTezgGer)

            # Zonalstats entlang Gerinne (OUTPUT_TABLE bevorzugt)
            vtab = run_rasterlayerzonalstats(
                raster_layer=rlyr_demClp, band=1,
                zones_raster=rlyr_rasTezgGer, zones_band=1, ref_layer=None,
                name="vtab"
            )
            lyrList.append(vtab)
            for f in vtab.getFeatures():
                fid = int(float(f['zone']))
                if fid != 0 and 'G-Laenge [m]' in dictCsv.get(fid, {}):
                    elevRange = float(f['max']) - float(f['min'])
                    length = float(dictCsv[fid]['G-Laenge [m]'].replace(',', '.'))
                    dictCsv[fid]['G-Neigung [1]'] = str(round(elevRange / length if length > 0 else 0.0, 3)).replace('.', ',')

            # ----------------------------- AKL (PSI -> AKL via Stützstellen -> Klassenflächen)
            mark("AKL zonal mean -> class shares")
            rlyr_psi = self._align_to_dem(akl_ras_in, rlyr_demClp, cellsize, "rlyr_psi_aligned", categorical=False, run=prun)
            lyrList.append(rlyr_psi)
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_psi, 'RASTER_BAND': 1, 'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'psi_', 'STATS': [2]
            })
            for fid in fid_list:
                for cls in [0, 1, 2, 3, 4, 5, 6]:
                    dictCsv[fid][f'AKL-{cls}'] = 0
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK']); area_m2 = f.geometry().area()
                m_psi = f['psi_mean']
                if m_psi is None:
                    continue
                akl_cont = psi_to_akl_value(float(m_psi))
                if akl_cont <= 0:
                    dictCsv[fid]['AKL-0'] = int(round(area_m2))
                elif akl_cont >= 6:
                    dictCsv[fid]['AKL-6'] = int(round(area_m2))
                else:
                    k = int(akl_cont // 1)
                    w_up = akl_cont - k
                    w_lo = 1.0 - w_up
                    dictCsv[fid][f'AKL-{k}'] = int(round(area_m2 * w_lo))
                    dictCsv[fid][f'AKL-{k + 1}'] = int(round(area_m2 * w_up))

            # ----------------------------- RKL
            mark("RKL zonal mean -> class shares")
            rlyr_rkl = self._align_to_dem(rkl_ras_in, rlyr_demClp, cellsize, "rlyr_rkl_aligned", categorical=False, run=prun)
            lyrList.append(rlyr_rkl)
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_rkl, 'RASTER_BAND': 1, 'INPUT_VECTOR': vlyr_tezg,
                'COLUMN_PREFIX': 'rkl_', 'STATS': [2]
            })
            for fid in fid_list:
                for cls in [1, 2, 3, 4, 5, 6]:
                    dictCsv[fid][f'RKL-{cls}'] = 0
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK']); area_m2 = f.geometry().area(); m = f['rkl_mean']
                if m is None:
                    continue
                if m <= 1:
                    dictCsv[fid]['RKL-1'] = int(round(area_m2))
                elif m >= 6:
                    dictCsv[fid]['RKL-6'] = int(round(area_m2))
                else:
                    k = int(m // 1); k = max(1, min(5, k)); w_up = m - k; w_lo = 1 - w_up
                    dictCsv[fid][f'RKL-{k}'] = int(round(area_m2 * w_lo))
                    dictCsv[fid][f'RKL-{k + 1}'] = int(round(area_m2 * w_up))

            # --- ZAF -> wZAF (<=4) & ZAA [%] ---
            mark("Align ZAF to DEM (resample)")
            # ZAF kategorisch (nearest), damit keine bilinearen Mischwerte entstehen
            rlyr_zaf = self._align_to_dem(zaf_ras_in, rlyr_demClp, cellsize, "rlyr_zaf_aligned", categorical=True, run=prun)
            lyrList.append(rlyr_zaf)
            if not rlyr_zaf.isValid():
                raise QgsProcessingException(f"Aligned ZAF raster invalid. Source: {zaf_ras_in.source()}")

            # ZAF <= 4: Maske erstellen (1/0) via GDAL rastercalculator (nur Klassen 1..4)
            mark("ZAF mask (A in [1..4]) via GDAL rastercalculator")
            mask_path = os.path.join(temp_folder, f"zaf_mask_le4_{uuid.uuid4().hex}.tif")
            res_mask = prun("gdal:rastercalculator", {
                'INPUT_A': rlyr_zaf, 'BAND_A': 1,
                'FORMULA': '((A >= 1) * (A <= 4))',
                'NO_DATA': -9999, 'RTYPE': 5,  # Float32
                'EXTRA': '', 'OUTPUT': mask_path
            })
            rlyr_zaf_le4_mask = QgsRasterLayer(res_mask['OUTPUT'], "rlyr_zaf_le4_mask", "gdal")
            lyrList.append(rlyr_zaf_le4_mask)
            if not rlyr_zaf_le4_mask.isValid():
                raise QgsProcessingException("ZAF<=4 mask invalid (gdal:rastercalculator).")

            # Werte-Raster: A * Maske (für wZAF)
            mark("ZAF values A*mask via GDAL rastercalculator")
            vals_path = os.path.join(temp_folder, f"zaf_vals_le4_{uuid.uuid4().hex}.tif")
            res_vals = prun("gdal:rastercalculator", {
                'INPUT_A': rlyr_zaf, 'BAND_A': 1,
                'INPUT_B': rlyr_zaf_le4_mask, 'BAND_B': 1,
                'FORMULA': 'A*B',
                'NO_DATA': -9999, 'RTYPE': 5,
                'EXTRA': '', 'OUTPUT': vals_path
            })
            rlyr_zaf_le4_vals = QgsRasterLayer(res_vals['OUTPUT'], "rlyr_zaf_le4_vals", "gdal")
            lyrList.append(rlyr_zaf_le4_vals)
            if not rlyr_zaf_le4_vals.isValid():
                raise QgsProcessingException("ZAF<=4 values raster invalid (gdal:rastercalculator).")

            # 0 -> NoData (für wZAF-Mittelbildung)
            mark("Zero->NoData via GDAL rastercalculator")
            recl_path = os.path.join(temp_folder, f"zaf_le4_nodata_{uuid.uuid4().hex}.tif")
            res_nodata = prun("gdal:rastercalculator", {
                'INPUT_A': rlyr_zaf_le4_vals, 'BAND_A': 1,
                'FORMULA': '((A==0)*(-9999) + (A!=0)*A)',
                'NO_DATA': -9999, 'RTYPE': 5,
                'EXTRA': '', 'OUTPUT': recl_path
            })
            rlyr_zaf_le4 = QgsRasterLayer(res_nodata['OUTPUT'], "rlyr_zaf_le4", "gdal")
            lyrList.append(rlyr_zaf_le4)

            # --- ZONALSTATS ---
            mark("Zonal mean ZAF<=4 and ZAA%")
            # wZAF: Mittel der Werte <=4
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_zaf_le4, 'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg, 'COLUMN_PREFIX': 'zaf_', 'STATS': [2]  # mean
            })
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK']); m = f['zaf_mean']
                if m is not None:
                    dictCsv[fid]['ZAF 1 bis 7'] = str(round(m, 4)).replace('.', ',')

            # ZAA[%] = mean(0/1-Maske)*100 -> garantiert in [0,100]
            prun("qgis:zonalstatistics", {
                'INPUT_RASTER': rlyr_zaf_le4_mask, 'RASTER_BAND': 1,
                'INPUT_VECTOR': vlyr_tezg, 'COLUMN_PREFIX': 'zaale4_', 'STATS': [2]  # mean
            })
            for f in vlyr_tezg.getFeatures():
                fid = int(f['TEZG_ID_ZK'])
                mean_le4 = f['zaale4_mean'] if f['zaale4_mean'] is not None else 0.0
                zaa_pct = float(mean_le4) * 100.0
                # Clamp auf [0, 100] (Numerik-Toleranzen abfangen)
                if zaa_pct < 0.0:
                    zaa_pct = 0.0
                elif zaa_pct > 100.0:
                    zaa_pct = 100.0
                dictCsv[fid]['Anteil [%]'] = str(round(zaa_pct, 4)).replace('.', ',')

            # CSV schreiben
            mark("Write CSV")
            fieldnames = ['TEZG Nr.', 'K.O.', 'K.U.', 'Bezeichnung/Ergaenzung', 'X', 'Y', 'Flaeche [km2]',
                          'F-Laenge [m]', 'F-Neigung [1]', 'Nat. Ret.[%]', 'Basisabfl. [m3/s]',
                          'AKL-0', 'AKL-1', 'AKL-2', 'AKL-3', 'AKL-4', 'AKL-5', 'AKL-6',
                          'RKL-1', 'RKL-2', 'RKL-3', 'RKL-4', 'RKL-5', 'RKL-6',
                          'ZAF 1 bis 7', 'Anteil [%]', 'G-Laenge [m]', 'G-Neigung [1]', 'd90 [m]']
            try:
                os.makedirs(os.path.dirname(outCsv), exist_ok=True)
            except Exception:
                pass
            with open(outCsv, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames)
                w.writeheader()
                for k in sorted(dictCsv.keys(), reverse=True):
                    w.writerow(dictCsv[k])

            # Finish & checks
            mark("Cleanup & finish")
            delete_temp_files(temp_folder)
            feedback.pushInfo(f"\nCSV geschrieben: {outCsv}")
            try:
                feedback.pushInfo(f"CSV existiert: {os.path.isfile(outCsv)} Größe: {os.path.getsize(outCsv)} Bytes")
            except Exception:
                pass
            feedback.pushInfo("\nFINISHED (Raster only) ......................")
            if has_small:
                feedback.pushInfo("Hinweis: Eines oder mehrere Polygone im TEZG sind kleiner als 100 m².")

            # QGIS-konformer Return (FileDestination)
            return {self.OUTPUT_CSV: outCsv}

        except Exception as e:
            tb = traceback.format_exc()
            feedback.reportError(f"\n[ERROR] at STEP {step['n']:02d}: {e}\n{tb}")
            raise

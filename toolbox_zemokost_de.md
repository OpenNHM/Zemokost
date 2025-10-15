# Toolbox 'WLV_pyqgis_ZEMOKOST' 1.0
<!--
<style>
/* === USER MANUAL STANDARD STYLING === */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
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
p { 
  line-height: 1.7;
  margin-bottom: 16px;
  text-align: justify;
}
ul, ol { 
  line-height: 1.6;
  margin: 15px 0;
  padding-left: 25px;
}
li {
  margin-bottom: 8px;
}
ul ul, ol ol {
  margin: 8px 0;
}
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
code {
  background-color: #f1f2f6;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}
strong { color: #2c3e50; }
em { color: #7f8c8d; }
blockquote {
  border-left: 4px solid #3498db;
  margin: 20px 0;
  padding: 10px 20px;
  background-color: #f8f9fa;
  font-style: italic;
  font-size: 14px;
}
hr {
  border: none;
  border-top: 2px solid #ecf0f1;
  margin: 30px 0;
}
</style>
-->

### Table of Contents
- [Eingabedaten](#eingabedaten)
- [Berechnungsschritte des Tools](#berechnungsschritte-des-tools)
- [OUTPUT](#output)


---

# Anleitung zum Python-Skript 'WLV_pyqgis_ZEMOKOST'


ZEMOKOST ist ein hydrologisches Niederschlags-Abfluss-Modell, entwickelt am Institut für Naturgefahren des
Bundesforschungszentrums für Wald (BFW), das in Österreich zur Gefahrenzonenplanung eingesetzt wird und auf
detaillierten Einzugsgebiets- und Geländedaten basiert.

Das Python-Skript **'WLV_pyqgis_ZEMOKOST'** wurde entwickelt, um die für ZEMOKOST benötigten Geodaten
automatisiert aufzubereiten und die relevanten Einzugsgebiets-, Fließweg- und Gerinneparameter in einer Ergebnisdatei
bereitzustellen. Es wurde für die Anwendung in der GIS-Umgebung QGIS entwickelt. Das Skript nutzt die
WhiteboxTools-Umgebung zur Durchführung hydrologischer und geostatistischer Berechnungen.

## Eingabedaten

1. **Höhenmodell (DEM)**: Rasterlayer mit Höheninformationen
   - Empfohlene Auflösung: 10 m × 10 m; muss ein gültiges Koordinatensystem besitzen

2. **Teileinzugsgebietsflächen (TEZG)**: Polygon-Shapefile mit Einzugsgebieten
   - eindeutige TEZG-ID
   - Zuflussknoten (Knoten oben)
   - Abflussknoten (Knoten unten)
   - optional: Bezeichnung

3. **Hauptgerinne**: Linien-Shapefile mit einem Hauptgerinneast je TEZG

4. **Feingerinne** (*optional*): Linien-Shapefile mit detailliertem Gerinnenetz
   - Für genauere Berechnung der Fließweglänge

5. **Abflussbeiwertflächen (AKL)**: Polygon-Shapefile mit Flächen gleicher Abflussklasse
   - Attributfeld mit AKL-Wert (0–6)

6. **Rauheitsflächen (RKL)**: Polygon-Shapefile mit Flächen gleicher Rauheitsklasse
   - Attributfeld mit RKL-Wert (1–6)

7. **Zwischenabflussflächen (ZAF/ZAA)** (*optional*): Polygon-Shapefile mit:
   - ZAF-Feld (Zwischenabflussfaktor, 0–7)
   - ZAA-Feld (Zwischenabflussanteil, 0–1)

8. **Ausgabeverzeichnis**
   - Pfad zu einem Ordner, in dem Ergebnisse gespeichert werden
   - *Option*: Zwischenergebnisse speichern

> **Hinweis**: Für die Nutzung des Skripts muss die WhiteboxTools-Umgebung in QGIS installiert und korrekt eingebunden
sein. WhiteboxTools ist ein leistungsfähiges Open-Source-GIS-Toolkit, das über das QGIS-Plugin 'Processing' verfügbar
ist.

## Berechnungsschritte des Tools

### 1. X / Y – Koordinaten des Schwerpunkts

Für jedes TEZG wird der Geometrie-Schwerpunkt (Centroid) berechnet. Die X- und Y-Koordinaten dieses Punkts werden als
„ctr_x" und „ctr_y" gespeichert. Diese Werte repräsentieren die Lage des TEZG im Raum.

### 2. Fläche [km²] - Teileinzugsgebietsflächen

Die Fläche jedes TEZG wird aus der Polygon-Geometrie berechnet. Die Fläche wird in Quadratmetern ermittelt und
anschließend durch 1.000.000 geteilt, um den Wert in km² zu erhalten. Ergebnisfeld: „Flaeche [km²]"

### 3. F-Länge [m] – Fließweglänge

Die mittlere Fließweglänge wird über die Funktion „downslope_distance_to_stream" aus dem WhiteboxTools-Paket berechnet.
Dabei wird die Entfernung vom höchsten Punkt (Ridge) bis zum Gerinne (Stream) rasterbasiert ermittelt.

#### Berechnung der F-Länge [m] abhängig von Haupt- und Feingerinne

Wenn kein Feingerinne angegeben ist, wird das Hauptgerinne verwendet. Wenn ein Feingerinne vorhanden ist, wird dieses
bevorzugt für die Berechnung der Fließwege verwendet, da es ein detaillierteres Gerinnenetz darstellt.

Das gewählte Gerinnenetz (Haupt- oder Feingerinne) wird auf die Fläche des TEZG geclippt. Falls das Koordinatensystem
des Gerinnenetzes vom DEM abweicht, wird es reprojiziert.

Das Gerinnenetz wird mit dem Tool `wbt.rasterize_streams` rasterisiert, wobei die Rasterausrichtung dem DEM entspricht.
Ergebnis: Ein binäres Raster, das die Lage der Gerinnezellen enthält. Das DEM wird hydrologisch korrigiert 
(`fill_depressions_wang_and_liu`). Die Fließrichtungen und Fließakkumulation werden bestimmt.

Mit dem Tool `downslope_distance_to_stream` (WhiteboxTools) wird für jede Rasterzelle die Entfernung zur nächsten
Gerinnezelle berechnet. Dies ergibt ein Fließweglängen-Raster, das die Überlandfließlänge für jede Zelle enthält.

Um die relevanten Fließwege zu identifizieren, wird das Fließweglängen-Raster mit einem reklassifizierten
Flow-Accumulation-Raster multipliziert, das nur Zellen an Ridgetops (Wasserscheiden) enthält. Ergebnis: Ein Raster mit
Fließweglängen von den Ridgetops bis zum Gerinne.

Für jedes TEZG wird die mittlere Fließweglänge aus dem oben genannten Raster berechnet. Dies geschieht mit
`qgis:zonalstatistics`, wobei der Mittelwert (mean) extrahiert wird. Ergebnisfeld: „F-Laenge [m]"

### 4. F-Neigung [1] – Flächenneigung

Die Neigung wird aus dem Höhenmodell (DEM) mit dem GDAL-Tool „slope" berechnet. Die Ausgabe erfolgt in Prozent, wird
aber durch 100 geteilt, um den dimensionslosen Wert (z. B. 0,12 für 12 %) zu erhalten. Die mittlere Neigung pro TEZG
wird ebenfalls über Zonenstatistik ermittelt. Ergebnisfeld: „F-Neigung [1]"

### 5. Ableitung der Abflussklassen (AKL) und Rauheitsklassen (RKL)

Die Polygon-Shapefiles AKL-Layer (Flächen gleicher Abflussbeiwertklasse) und RKL-Layer (Flächen gleicher Rauheitsklasse)
enthalten ein Attributfeld mit dem jeweiligen Klassifikationswerten AKL und RKL (AKL-Werte: 0 bis 6; RKL-Werte: 1 bis
6). Beide Attribute können auch gemeinsam in einem einzelnen File vorliegen.

Der TEZG-Layer wird ggf. reprojiziert, um das Koordinatensystem an den AKL- bzw. RKL-Layer anzupassen. Danach erfolgt
eine Geometrie-Schnittmenge (Intersection) zwischen dem TEZG-Layer und dem jeweiligen Klassifikationslayer.

Für jede Kombination aus TEZG und AKL/RKL-Klasse wird die Schnittfläche berechnet. Die Fläche wird in Quadratmetern
ermittelt und klassenspezifisch aggregiert.

Die berechneten Flächenanteile pro Klasse werden in einem Dictionary gespeichert. Für jede TEZG-ID werden die
Flächenanteile wie folgt abgelegt: AKL-0, AKL-1, ..., AKL-6; RKL-1, ..., RKL-6

> **Hinweis**: Die Verwendung von Shapefiles wird empfohlen, da GPKG-Dateien laut Skript nicht vollständig unterstützt
werden.

### 6. Ableitung von Zwischenabfluss Faktor (ZAF) und Zwischenabfluss-Anteil (ZAA)

Optional kann ein Polygon-Layer mit Flächen gleicher ZAF- und ZAA-Werte geladen werden. ZAF: Werte von 0 bis 7 (Faktor);
ZAA: Werte von 0 bis 1 (Anteil).

Beide Attribute werden in separate Raster umgewandelt:
- ZAF-Raster: enthält die Zwischenabflussfaktoren
- ZAA-Raster: enthält die Zwischenabflussanteile

Die Rasterauflösung entspricht der Zellgröße des DEM.

#### Reklassifizierung ZAF und Maskierung ZAA

ZAF wird auf vier Klassen reduziert: Die Klassen 1 bis 4 bleiben erhalten, die Klassen >4 werden auf NoData (-9999)
gesetzt.

ZAA wird maskiert, sodass nur Zellen mit ZAF > 0 berücksichtigt werden.

#### Berechnung gewichteter Mittelwerte - Gewichteter ZAF (wZAF)

$$\text{wZAF} = \frac{\sum(\text{ZAF} \times \text{ZAA})}{\sum \text{ZAA}}$$

**Umsetzung**: Multiplikation der ZAF- und ZAA-Raster. Zonenstatistik pro TEZG liefert das Summenprodukt und die Summe
von ZAA.

#### Berechnung gewichteter Mittelwerte - Gewichteter ZAA (wZAA)

$$\text{wZAA} = \frac{\sum(\text{ZAA} \times \text{Zellgröße})}{\text{Gesamtfläche ZAA}} \times 100$$

**Umsetzung**: Multiplikation von ZAA mit Zellgröße. Zonenstatistik liefert Summenprodukt und Zellanzahl.

Im Skript werden also die ursprünglichen sehr langsamen Zwischenabflussfaktor-Werte (ZAF) >4 durch NoData-Werte ersetzt.
Mit dieser Reklassifizierung werden alle Flächen mit ZAF>4 eliminiert, damit nur noch „schnellere" ZAF-Flächen
übrigbleiben. Durch die gewichtete Mittelung wird somit eine Überbewertung von sehr langsamem Interflow vermieden.

Die Maskierung stellt sicher, dass nur Zellen mit gültiger ZAF-ZAA-Kombination verwendet werden.

### 7. G-Laenge [m] – Gerinnelänge

Die Gerinnelänge eines Teileinzugsgebiets wird durch die Verschneidung des Hauptgerinnes mit dem jeweiligen Teilgebiet
ermittelt. Nach einer geometrischen Verschmelzung (Dissolve) pro TEZG-ID wird die Länge der resultierenden Gerinnelinie
direkt aus der Geometrie berechnet.

### 8. G-Neigung [1] – Gerinneneigung

Im Skript wird die Gerinne-Neigung je Teileinzugsgebiet ermittelt, indem zunächst das Gerinnenetz mit den TEZG
verschnitten und pro Gebiet zu einer Linie zusammengefasst wird. Für diese Gerinnelinie wird die Länge berechnet und
parallel dazu die minimale und maximale Höhe aus dem DEM abgeleitet. Aus der Höhendifferenz und der Linienlänge ergibt
sich anschließend die Gerinne-Neigung als dimensionsloser Wert (Höhendifferenz geteilt durch Gerinnelänge).

## OUTPUT

Der Output des Skripts ist eine CSV-Datei namens `import_zemokost.csv`, in der für jedes Teileinzugsgebiet (TEZG) die
wichtigsten hydrologischen und geometrischen Kennwerte zusammengefasst sind. Enthalten sind unter anderem:

- **Identifikatoren** (TEZG-Nummer, Knoten oben/unten, Name, Schwerpunktkoordinaten)
- **Flächenattribute** wie Größe in km² und mittlere Hangneigung
- **Fließwege** mit mittlerer Fließlänge (F-Laenge) und Gerinnelänge (G-Laenge)
- **Gerinneattribute** wie Gerinne-Neigung
- **Abfluss- und Rauigkeitsklassen** (AKL, RKL) mit Flächenanteilen
- **Zwischenabflussparameter** (gewichtetes ZAF, ZAA), sofern angegeben

Damit liefert die CSV eine (fast) vollständige Übersicht aller für das NA-Modell ZEMOKOST benötigten Eingangsdaten. Die
Parameter sind in der Output-Datei so organisiert, dass sie mittels copy-paste direkt in die Eingabemaske von ZEMOKOST
übernommen werden können.

> **Hinweis**: Eine direkte Ableitung des für die Modellierung mit ZEMOKOST unabdingbaren Parameters D90 [m] ist
derzeit nicht möglich und implementiert. Dieser Wert muss separat eingegeben werden.
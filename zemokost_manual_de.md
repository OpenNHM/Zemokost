
# ZEMOKOST v2.0.1
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
### Inhaltsverzeichnis
- [Über ZEMOKOST](#über-zemokost)
- [Einrichtung und Aktivierung](#einrichtung-und-aktivierung)
- [Farbcode](#farbcode)
- [Definition der Einzugsgebietsparameter](#definition-der-einzugsgebietsparameter)
- [Niederschlagseingabe](#niederschlagseingabe-für-die-hydrologische-simulation)
- [Simulation und Ergebnisse](#szenario-simulation-und-bemessungsabflussberechnung)
- [Dateimanagement und Export](#dateimanagement-und-export)

---

# HANDBUCH

### Eine optimierte Laufzeitmethode, nach Zeller modifiziert von Kohl und Stepanek, konzipiert für die Hochwasserabschätzung in kleinen Einzugsgebieten.

**Bernhard Kohl** 
📧 bernhard.kohl@bfw.gv.at  

**Mitwirkende:**  
Adrian Maldet, Leopold Stepanek


## Über ZEMOKOST

Das Simulationsprogramm ZEMOKOST (v2.0.1) ist ein Niederschlag-Abfluss-Modell, das speziell für die Hochwasserabschätzung in kleinen Wildbacheinzugsgebieten entwickelt wurde. In praktischen Anwendungen reichen die Einzugsgebietsflächen für ZEMOKOST-Analysen von kleinen Flächen unter 100 m² bis zu größeren Einzugsgebieten von etwa 100 km². ZEMOKOST basiert auf der von Zeller entwickelten und später von Kohl und Stepanek modifizierten Laufzeitmethode (Kohl und Stepanek, 2005; Kohl, 2012).

Diese Anleitung dient als Handbuch für ZEMOKOST v2.0.1. Die Bedienoberfläche ist schrittweise aufgebaut: Jede Schaltfläche und jedes Eingabefeld wird erst aktiviert, wenn der vorhergehende Schritt abgeschlossen ist. Die wichtigsten Arbeitsschritte sind:

- Definition der Einzugsgebietsdaten
- Eingabe der Niederschlagsdaten
- Simulation und Ergebnisse

## Einrichtung und Aktivierung

ZEMOKOST (V2.0.1) ist in Microsoft Excel 2013 implementiert und verwendet einen umfassenden Satz von Visual Basic for Applications (VBA)-Makros. ZEMOKOST ist kompatibel mit allen aktuellen Desktop-Versionen von Microsoft Excel, einschließlich Excel 2013, Excel 2016, Excel 2019, Excel 2021 und Microsoft 365 Excel.

Das Programm ist über mehrere Arbeitsblätter strukturiert, die je nach aktuellem Schritt im Simulations-Workflow dynamisch ein- oder ausgeblendet werden. Benutzer beginnen im Hauptarbeitsblatt, definieren Simulationsparameter und durchlaufen eine geführte Sequenz von Eingaben und Berechnungen.

Die Datei ZEMOKOST-2_0_1.xlsm ist eine makrofähige Excel-Arbeitsmappe, und Makros müssen aktiviert werden, damit das Programm korrekt funktioniert.

### Makros aktivieren

Dies kann erfolgen über:

**Datei → Optionen → Trust Center → Einstellungen für das Trust Center → Makroeinstellungen**

Weitere möglicherweise erforderliche Änderungen, Aktivierung von Steuerelementen über:

**Datei → Optionen → Trust Center → Trust Center-Einstellungen → ActiveX-Einstellungen → Eingabeaufforderung anzeigen, bevor alle Steuerelemente mit minimalen Einschränkungen aktiviert werden**

## Farbcode

Die Benutzeroberfläche verwendet ein farbcodiertes System, um den Status der Dateneingabe anzuzeigen:


| Farbe | Typ | Beschreibung |
|-------|------|-------------|
| <span style="background-color: #FF80FF; color: white; padding: 2px 8px;">**Magenta**</span> | Schaltfläche  | Datensatz unvollständig oder enthält fehlende obligatorische Einträge |
| <span style="background-color: #00ff00; color: white; padding: 2px 8px;">**Hellgrün**</span> | Schaltfläche  | Alle erforderlichen Daten wurden erfolgreich bereitgestellt |
| <span style="background-color: #c6e0b4; color: white; padding: 2px 8px;">**Grün**</span> | Feld | Obligatorische Eingabedaten |
| <span style="background-color: #ffe699; color: black; padding: 2px 8px;">**Gelb**</span> | Feld | Optionale Dateneingabe|
| <span style="background-color: #f8cbad; color: black; padding: 2px 8px;">**Rot**</span> | Feld | Eingabe erforderlich |


Jeder Parameter wird von Kommentarfeldern (<span style="color: #FF0000 !important; font-weight: bold !important;">◄</span>) begleitet, die kontextbezogene Anmerkungen und Anleitungen für die Dateneingabe bieten.

## Definition der Einzugsgebietsparameter

Der Benutzer beginnt im erten Arbeitsblatt `main`, indem er das Einzugsgebiet beschreibt und die Datei zunächst mit einem spezifischen Dateinamen speichert.

Der erste Schritt bei der Verwendung des ZEMOKOST-Modellierungsrahmens besteht in der umfassenden Definition des Einzugsgebiets und seiner zugehörigen hydrologischen Parameter. Dies wird über die Schaltfläche **EZG festlegen** im ersten Hauptarbeitsblatt eingeleitet, welche die entsprechende Arbeitsblatt-Schnittstelle öffnet.

Um das Modell in seinen Ausgangszustand zurückzusetzen, stellt die Schaltfläche **ZEMOKOST leeren** im Hauptarbeitsblatt die ursprüngliche, leere Vorlagendatei wieder her.

### Arbeitsblatt Einzugsgebietsdefinition:

**Main → EZG festlegen**

#### Felder anzeigen

Im Arbeitsblatt mit dem Titel `EZG festlegen` können Benutzer verschiedene Eingabefelder selektiv aktivieren oder deaktivieren, um das Modell an spezifische hydrologische Szenarien anzupassen.

### Erforderliche Parameter (grüne Felder)

Die für die Simulation erforderlichen Kernparameter umfassen:

### Einzugsgebietsstruktur

#### Definition der Teileinzugsgebiete

ZEMOKOST unterteilt das Einzugsgebiet in Teileinzugsgebiete, die durch Knotenpunkte verbunden sind, um die Wasserfließrouting zu simulieren. Das Modell unterstützt bis zu 300 Teileinzugsgebiete, obwohl Simulationen auch für ein einzelnes, einheitliches Einzugsgebiet durchgeführt werden können. Jedes Teileinzugsgebiet repräsentiert einen Bereich mit ähnlichen hydrologischen Eigenschaften und wird durch drei Parameter definiert:

Jedes Teileinzugsgebiet wird durch ein Tripel definiert:

- **Teileinzugsgebietsnummer (TEZG.nr.):** Eindeutiger Identifikator für jedes Teileinzugsgebiet (1, 2, 3, ...)
- **Zuflussknoten (K.O.):** Knoten, an dem Wasser in das Teileinzugsgebiet eintritt
- **Abflussknoten (K.U.):** Knoten, an dem Wasser das Teileinzugsgebiet verlässt

#### Einfaches Beispiel:

- **Teileinzugsgebiet 1** → Knoten Zufluss: 0 (Einlass) → Knoten Abfluss: 1
- **Teileinzugsgebiet 2** → Knoten Zufluss: 1 → Knoten Abfluss: 2
- **Teileinzugsgebiet 3** → Knoten Zufluss: 2 → Knoten Abfluss: 3 (Auslass)

#### Fließlogik:

Dies erzeugt einen sequenziellen Wasserfließweg, bei dem Teileinzugsgebiet 1 (Quellgebiet) zu Knoten 1 abfließt, Teileinzugsgebiet 2 diesen Abfluss empfängt und zu Knoten 2 abfließt, und Teileinzugsgebiet 3 den kombinierten Abfluss empfängt und zum Einzugsgebietsauslass (Knoten 3) abfließt.

#### Abgrenzungsrichtlinien

- Teileinzugsgebiete sollten Bereiche mit ähnlicher Landnutzung, Neigung oder hydrologischem Verhalten widerspiegeln
- Gerinnestrecken sollten mit den Teileinzugsgebietsgrenzen übereinstimmen
- Berücksichtigen Sie die Grenze von 300 Teileinzugsgebieten bei der Planung Ihrer Einzugsgebietsunterteilung

#### Wesentliche Regeln für die Knotenstruktur:

- **Eindeutige Nummerierung:** Jedes Teileinzugsgebiet und jeder Knoten muss eine eindeutige Nummer haben
- **Quellgebiete:** Teileinzugsgebiete ohne Zufluss von oberhalb verwenden Zuflussknoten "0" (dieser Wert kann mehrfach verwendet werden)
- **Fließrichtung:** Jeder Zuflussknoten muss mit genau einem Abflussknoten verbunden sein
- **Netzwerkkonnektivität:** Alle Teileinzugsgebiete müssen schließlich zu einem einzigen Auslass entwässern
- **Keine Schleifen:** Kreisförmige Fließwege sind nicht erlaubt - Wasser muss nur in eine Richtung fließen

> **Validierungstipp:** Verfolgen Sie den Wasserfluss von jedem Teileinzugsgebiet, um sicherzustellen, dass er den Auslass ohne Schleifen oder Sackgassen erreicht.

### Flächendaten

Teileinzugsgebietsgrenzen und Flächen können manuell mit topografischen Karten oder digital mit GIS-Tools abgegrenzt werden.

> Siehe **[WLV_pyqgis_ZEMOKOST](toolbox_zemokost_de.md)** für weitere Informationen.

Die folgenden Parameter werden typischerweise extrahiert:

- **Fläche [km²]:** Projizierte Fläche des Teileinzugsgebiets.
- **Länge [m]:** Oberflächenfließweglänge (Lsur) bezieht sich auf die durchschnittliche geländeparallele Entfernung, die der Oberflächenabfluss von der Wasserscheidengrenze zum nächsten Bach oder Gerinne zurücklegt. Sie repräsentiert die maximale projizierte Fließlänge über die Landoberfläche, bevor Wasser in das Entwässerungsnetz eintritt.
- **Neigung [1]:** Oberflächenneigung als dimensionsloser Gradient, berechnet als Verhältnis von vertikaler Höhenänderung zu horizontaler Entfernung (Δh/Δx). Typische Werte reichen von 0 (flach) bis 1 (sehr steil).

In ZEMOKOST wird die Oberflächenfließweglänge (Lsur) direkt vom Detailgrad des Gewässernetzes beeinflusst - ein feineres Netz führt zu kürzeren Lsur-Werten. Das Gleichgewicht zwischen Lsur und Gerinnefließlänge (Lch) beeinflusst die Gesamtform der Ganglinie und das Spitzenzeit. Es ist eine Schlüsseleingabe zur Berechnung der Konzentrationzeit des Oberflächenabflusses und wird typischerweise aus topografischen Karten oder digitalen Höhenmodellen mittels GIS abgeleitet.

#### Flächensegmentierung Oberflächenabflussklassen AKL und Flächensegmentierung Rauheitskoeffizientenklassen RKL

- **Oberflächenabflussbeiwertklasse (AKL) [–]:** Skala von 0 bis 6, wobei 0 = kein Oberflächenabfluss und 6 = 100% Oberflächenabfluss.
- **Oberflächenrauheitsklasse (RKL) [–]:** Skala von 0 bis 6, wobei 0 = sehr glatte Oberfläche und 6 = extrem raue Oberfläche.

Der AKL definiert die Abflussdisposition basierend auf Landbedeckung und Bodenart, während der RKL den hydraulischen Widerstand der Oberfläche charakterisiert. Beide Klassen werden aus vordefinierten Kategorien basierend auf Feldbeurteilungen oder Kartierungsrichtlinien ausgewählt und entweder als Prozentwerte oder als Fläche pro Teileinzugsgebiet eingegeben. Da ZEMOKOST die Werte intern pro Teileinzugsgebiet mittelt, beeinflusst die Wahl des Eingabeformats das Ergebnis nicht.

Ein Dropdown-Menü ermöglicht es dem Benutzer zu wählen, ob die AKL- oder RKL-Klassen durch ihren Mittelwert (m), Standard oder durch ihre unteren (b) oder oberen (t) Grenzen für die weitere Modellierung dargestellt werden. Diese Parameter sind wesentlich für die Berechnung der Oberflächenfließgeschwindigkeit und Konzentrationzeit.

Detaillierte Informationen zur Bewertung von AKL und RKL finden Sie hier:

https://www.researchgate.net/publication/273761280_A_Simple_Code_of_Practice_for_the_Assessment_of_Surface_Runoff_Coefficients_for_Alpine_Soil-Vegetation_Units_in_Torrential_Rain_Version_20

### Gerinnetopologie

- **Länge [m]:** Gesamtlänge des Hauptentwässerungsgerinnes (Lch) innerhalb des Teileinzugsgebiets. Beeinflusst die Leitung des Wassers innerhalb des Entwässerungsnetzes und wirkt sich auf Ganglinienform und Zeitpunkt aus.
- **Neigung [1]:** Dimensionslose Neigung des Hauptbachs, berechnet als Verhältnis von vertikaler Höhenänderung zu horizontaler Entfernung (Δh/Δx). Typische Werte reichen von 0 (flach) bis 1 (sehr steil).
- **d90 [m]:** Charakteristischer Korndurchmesser - Korngröße, für die 90% des Sediments feiner ist (d90). Beschreibt die dominante Rauheit des Bachbettes und ist entscheidend für die Abschätzung des Fließwiderstands und der Geschwindigkeit unter Verwendung der empirischen Rickenmann-Formel.

In ZEMOKOST repräsentiert Lch die Entfernung, über die Wasser durch das Gerinne geleitet wird, und wird zur Berechnung der Gerinnefließzeit verwendet. d90 ist wesentlich für die Modellierung der Fließgeschwindigkeit und der Translation des Abflusses durch das Gerinnenetz.

## Optionale Parameter (gelbe Felder)

Optionale Parameter können die Modellgenauigkeit erheblich verbessern und ermöglichen eine detailliertere Darstellung hydrologischer Prozesse. Obwohl sie für eine grundlegende Simulation nicht streng erforderlich sind, bieten sie zusätzliche Flexibilität, um komplexes Systemverhalten zu erfassen und den Realismus der Ergebnisse zu verbessern.

### Koordinaten der Teileinzugsgebiete

In ZEMOKOST können die Koordinaten von Teileinzugsgebieten verwendet werden, um räumlich variable Niederschlagseingaben zu modellieren, indem eine zentrale Niederschlagszelle (typischerweise das am stärksten betroffene Teileinzugsgebiet) definiert und die mittlere Entfernung jedes Teileinzugsgebiets von diesem Zentrum berechnet wird. Diese Entfernungen werden dann verwendet, um entfernungsabhängige Niederschlagsabschwächungsfunktionen (z.B. Lorenz & Skoda oder Blöschl) anzuwenden, um realistische räumliche Niederschlagsgradienten zu simulieren. Dieser Ansatz ermöglicht es dem Modell, die abnehmende Niederschlagsintensität mit zunehmender Entfernung vom Niederschlagszentrum zu berücksichtigen.

### Flächendaten: Natürliche Retention und Basisabfluss

Natürliche Retention bezieht sich in ZEMOKOST auf die temporäre Speicherung und Verzögerung des Abflusses, verursacht durch natürliche Landschaftsmerkmale wie Feuchtgebiete, gesättigte Böden, kolluviale Ablagerungen, Moränen und bewachsene Senken. Diese Bereiche reduzieren den Spitzenabfluss und verlängern die Abflussdauer, indem sie entweder Wasservolumen zurückhalten oder die Fließgeschwindigkeit durch Oberflächenrauheit und Infiltration verlangsamen.

Um die natürliche Retention in das Modell zu integrieren, wird die retentive Wirkung als Prozentsatz der Teileinzugsgebietsfläche quantifiziert. Dieser Wert repräsentiert den Anteil des Teileinzugsgebiets, der zur Fließdämpfung beiträgt, und wird entsprechend in das Modell eingegeben. Durch die Zuweisung dieses Prozentsatzes kann ZEMOKOST die Abschwächung von Ganglinienspitzen simulieren und den Realismus der Hochwassermodellierung verbessern.

Ein Basisabflusswert (in m³/s) kann individuell für jedes Teileinzugsgebiet definiert werden, um konstanten Grundwasser- oder Quellabfluss darzustellen. Es ist jedoch wichtig sicherzustellen, dass der kumulative Basisabfluss über alle Teileinzugsgebiete hydrologisch plausibel bleibt und nicht zu unrealistischen Gesamtabflusswerten am Auslass führt.

### Zwischenabfluss (empfohlen)

In ZEMOKOST ist der Zwischenabfluss direkt mit dem Oberflächenabfluss und damit auch mit der Niederschlagsintensität gekoppelt. Je stärker der Niederschlag, desto größer der Oberflächenabfluss und folglich desto geringer das Potenzial für Zwischenabfluss, da weniger Wasser infiltriert. Umgekehrt, bei geringeren Niederschlagsintensitäten, nimmt die Infiltration zu und der Zwischenabfluss wird dominanter.

Die beiden Parameter -  Zwischenabflussfaktor (ZAF) und Zwischenabflussanteil - arbeiten zusammen, um den subsurface lateralen Abfluss zu simulieren:

Der Zwischenabflussanteil (IFP) definiert den Prozentsatz der Teileinzugsgebietsfläche, der zum Zwischenabfluss beiträgt. Der Zwischenabflussfaktor (ZAF) repräsentiert den hydraulischen Widerstand des Untergrunds und bestimmt die Geschwindigkeit des Zwischenabflusses. Er basiert auf der Substratdurchlässigkeit und beeinflusst, wie schnell infiltriertes Wasser das Gerinnenetz erreicht.

| ZAF | Beschreibung | Durchlässigkeit [m/s] | Durchlässigkeit [cm/h] |
|-----|--------------|----------------------|------------------------|
| 1 | Sehr stark durchlässig | > 1×10⁻² | 3600 |
| 2 | Sehr stark bis stark durchlässig | 5,5×10⁻³ | 1980 |
| 3 | Stark durchlässig | 1×10⁻³ | 360 |
| 4 | Stark bis mäßig durchlässig | 5,5×10⁻⁴ | 198 |
| 5 | Mäßig durchlässig | 1×10⁻⁵ | 3,6 |
| 6 | Schwach durchlässig | 1×10⁻⁷ | 0,036 |
| 7 | Sehr schwach durchlässig | > 1×10⁻⁸ | 0,0036 |

Die dynamische Kopplung von Niederschlag, Oberflächenabfluss und Zwischenabfluss stellt sicher, dass ZEMOKOST die inverse Beziehung zwischen Oberflächenabfluss und Zwischenabfluss widerspiegelt und eine realistischere Simulation hydrologischer Reaktionen unter variierenden Niederschlagsbedingungen ermöglicht.

### Maßnahmen

Die Berücksichtigung technischer Maßnahmen in ZEMOKOST umfasst die Integration von Rückhaltebecken, die auf zwei Arten modelliert werden können: entweder als feste Speichervolumen, bei denen eine definierte Wassermenge zurückgehalten und vom Abfluss abgezogen wird, oder über eine V/Q-Beziehung, die das dynamische Verhalten des Rückhaltebeckens simuliert, indem das gespeicherte Volumen (V) mit dem Abfluss (Q) verknüpft wird. Dies ermöglicht eine realistischere Darstellung der Rückhaltebeckenhydraulik, einschließlich verzögerter Freisetzung und Spitzenabflussdämpfung. Zusätzlich können Ein- und Auslässe definiert werden, um zu steuern, wie Wasser in das Rückhaltebecken eintritt und es verlässt, was die Simulation geregelter Fließsysteme und technischer Abflussstrukturen ermöglicht.

### Systemzustand

**Dropdown Systemzustand ("-6" – "6")**

Um variierende anfängliche Feuchtebedingungen zu berücksichtigen, führt ZEMOKOST den Systemzustandsindex (SZI) ein. Der Standardwert von SZI ist null und repräsentiert durchschnittliche Bedingungen für die Abflusserzeugung. Die Erhöhung des SZI verschiebt den Achsenabschnitt der Abflussbeiwert-Abstraktionszeit-Beziehung proportional, was verbesserte hydrologische Bedingungen und verzögerten Abflussbeginn impliziert. Werte über 6 deuten auf außergewöhnlich günstige Systemzustände hin, während negative SZI-Werte (bis -6) zunehmend trockene Vorbedingungen widerspiegeln. Werte unter -6 werden als unplausibel betrachtet.

## Abschluss und Upload der Einzugsgebietsparameter

Sobald alle relevanten Parameter in der Einzugsgebietsdefinition definiert wurden, kann der Datensatz mit der Schaltfläche **Gebietsdaten einlesen** hochgeladen werden. Diese Aktion führt den Benutzer zum `main` Arbietsblatt zurück.

Wenn erforderliche Felder unvollständig sind oder ungültige Einträge enthalten, generiert ZEMOKOST spezifische Fehlermeldungen zur Unterstützung bei der Fehlerbehebung und Korrektur.

## Niederschlagseingabe für die hydrologische Simulation

Eine genaue Niederschlagseingabe ist eine grundlegende Voraussetzung für die Niederschlag-Abfluss-Modellierung. Sobald das Einzugsgebiet definiert wurde, zeigt das Hauptarbeitsblatt dedizierte Eingabeschaltflächen für Niederschlagsdaten an.

ZEMOKOST bietet Flexibilität bei der Niederschlagsspezifikation, um sowohl einheitliche als auch räumlich variable Niederschlagsszenarien zu simulieren. Dies ist besonders wichtig für die Modellierung konvektiver Sturmereignisse oder komplexer Topographie in alpinen Einzugsgebieten.

### Zwei Hauptmethoden:

- **Bemessungsregen laden** Statistischer Niederschlag für Hochwasserabschätzung (üblich)
- **Niederschlagsreihe laden** Manuelle Zeitreiheneingabe für spezifische Ereignisse

### Zwei Eingabeebenen:

- **Einzugsgebiet:** Niederschlag auf gesamtes Einzugsgebiet anwenden → öffnet Verteilungsarbeitsblatt mit räumlichen Optionen (üblich)
- **Teileinzugsgebiet:** Niederschlag individuell pro Teileinzugsgebiet definieren → keine zusätzliche Verteilung erforderlich (optional)

## Bemessungsregen

**Main → Bemessungsregen laden → EZG oder TEZGe → u-/w-Reihen einlesen**

Bemessungsniederschlag wird typischerweise für die Hochwasserabschätzung in kleinen, nicht gemessenen alpinen Einzugsgebieten verwendet, was das primäre Anwendungsgebiet von ZEMOKOST ist. Die Benutzer können zwischen zwei Eingabeoptionen wählen:

- **N1-/N100-Reihen**, wobei N1 die Niederschlagshöhe für eine 1-jährige Wiederkehrperiode und N100 für eine 100-jährige Wiederkehrperiode ist
- **u-/w-Reihen**, wobei u der mittlere Niederschlag und w die Standardabweichung ist), um Bemessungsniederschlagskurven für die Simulation zu generieren.

Beide Optionen werden verwendet, um Bemessungsniederschlagskurven für die Simulation zu generieren. Die N1-/N100-Serie definiert die Intensität-Dauer-Häufigkeit (IDF)-Beziehung für einen Standort, während die u-/w-Serie Mittelwert- und Standardabweichungswerte für denselben Zweck bereitstellt.

Mindestens drei N1-/N100-Paare (oder drei u-/w-Paare) sind erforderlich, um eine gültige Niederschlagskurve zu generieren. Sobald die Daten eingegeben sind, kann der Benutzer die Niederschlagsverteilung visualisieren. Ein Dropdown-Menü ermöglicht die Auswahl der Kurvenform, während sich die Visualisierung automatisch an die ausgewählte Wiederkehrperiode und Niederschlagsdauer anpasst. Die ausgewählte Kurvenform wird für die Simulation übernommen, obwohl die Visualisierung selbst die Simulationseinstellungen nicht direkt beeinflusst.

Die Schaltfläche **u-/w-Reihen einlesen** leitet zum Arbeitsblatt `uw-Reihen verteilen` weiter.

## Bemessungsniederschlag für das gesamte Einzugsgebiet (nur für Einzugsgebietsoption)

Gilt für beide Niederschlagseingabemethoden, wenn Einzugsgebiet ausgewählt wurde:

- **→ load p-series → p-series distribution**
- **→ load design-series → uw-series distribution**

Das Arbeitsblatt `uw-Reihen Verteilen` ermöglicht es Benutzern, die räumliche Zuordnung des Niederschlags mit einer der folgenden Methoden zu definieren: Diese Funktionen spiegeln die empirische Beobachtung wieder, dass die Niederschlagsintensität mit zunehmender Entfernung vom Niederschlagszentrum und mit zunehmender Einzugsgebietsfläche abnimmt.

### Abminderungsmethoden (obligatorisch - eine auswählen):

- **Keine:** Einheitlicher Niederschlag über das gesamte Einzugsgebiet.
- **Handeingabe:** Benutzerdefinierte Reduktionswerte pro Teileinzugsgebiet [%].
- **radiale (Abstand):** Reduktion basierend auf der Entfernung von einer zentralen Niederschlagszelle.
- **Radial (XY-Koordinaten)** (nur wenn xy in der Einzugsgebietsdefinition definiert): Reduktion basierend auf geografischen Koordinaten eines definierten Niederschlagszentrums.

*Diese Option erfordert, dass X- und Y-Koordinaten von Teileinzugsgebieten im Arbeitsblatt Einzugsgebietsdefinition eingegeben wurden.*

### Abminderungsstärke (nur für radialen Abstand und radiale XY-Koordinaten):

- **Leichte Abminderung:** Basierend auf Lorenz & Skoda (2001), korrigiert von Drexel (2009).
- **Starke Abminderung:** Basierend auf Blöschl (2009), geeignet für größere Einzugsgebiete oder konvektive Niederschlagsereignisse.

## Zeitlicher Versatz und Ereignissimulation

Ein optionaler Zeitversatz kann angewendet werden, um die Bewegung einer Sturmzelle über das Einzugsgebiet zu simulieren. Diese Funktion ermöglicht dynamische Niederschlagsszenarien, wie konvektive Ereignisse mit räumlicher und zeitlicher Variabilität.


## Niederschlagsreihe

**Main → Niederschlagsreihen laden → EZG oder TEZGe**

Niederschlagsserien für ein einzelnes Ereignis können hier geladen werden, mit zwei Optionen - Bemessungsniederschlag oder manuelle Eingabe - die das Arbeitsblatt `N-Verteilung eingeben` öffnen, wenn **Niederschlagsreihen laden** gewählt wird.

### Design-Regen für EZG → Design-Regen definieren → Design-Regen wählen

Geben Sie die mittlere Regenintensität (mm/h) und Regendauer (min) ein, wählen Sie dann die Niederschlagskurvenform aus dem Dropdown-Menü. Mit der Schaltfläche **Design-Regen verwenden** wird zum Arbeitsblatt `N-Verteilung eingeben` weitergeleitet.

### Handeingabe für EZG → Regenreihe eigeben → N-Reihe eingeben

Eine manuell eingegebene Niederschlagszeitreihe ermöglicht volle Kontrolle über die zeitliche Verteilung. Niederschlagsdaten sollten in Ein-Minuten-Intervallen eingegeben werden, beginnend vom Niederschlagsbeginn, um eine ordnungsgemäße Ausrichtung der Abflusserzeugung und Ganglinienentwicklung sicherzustellen. Für jede Minute muss ein Niederschlagsintensitätswert angegeben werden; geben Sie 0 für jede Niederschlagspause ein.

Die Schaltfläche **N-Reihe Einlesen** leitet zum Arbeitsblatt `N-Verteilung eingeben` weiter (nur für Einzugsgebiet, nicht Teileinzugsgebiet), wo Reduktion, Stärke und Versatz angepasst werden können, wie unter Bemessungsniederschlagseingabe beschrieben.



**Letzter Schritt:** Sobald die räumlichen und zeitlichen Verteilungseinstellungen definiert sind, können die Niederschlagsdaten mit der Schaltfläche **Niederschlag einlesen** in die Simulation geladen werden, die zum Hauptarbeitsblatt weiterleitet.

## Szenario-Simulation und Bemessungsabflussberechnung

Nach der Definition der Einzugsgebietsparameter und der Auswahl der Niederschlagseingabe zeigt das Hauptarbeitsblatt Schaltflächen für die Simulation an. Die verfügbare Option hängt von Ihrem Niederschlagseingabetyp ab:

- **Szenario-Simulation** wird verwendet, wenn eine manuelle Niederschlagsserie geladen wird. Diese Option ermöglicht die Durchführung ereignisbasierter Simulationen für eine spezifische Niederschlagszeitreihe.
- **Bemessungsabflussberechnung** wird verwendet, wenn eine Bemessungsniederschlagsserie geladen wird. Diese Option berechnet Abflüsse basierend auf statistisch abgeleitetem Niederschlag für eine ausgewählte Wiederkehrperiode (z.B. T = 100 Jahre).

Die entsprechende Simulationsschaltfläche - **Szenario simulieren** oder **Bemessung durchführen** - erscheint automatisch. Beide Simulationstypen können mit spezifischen Beobachtungsknoten für gezielte Analysen verknüpft werden.

### Simulations-Workflow

Abhängig von der gewählten Niederschlagseingabemethode verläuft der Workflow wie folgt:

**Für manuelle Niederschlagsserie:**  
Knoten auswählen → Szenario simulieren

**Für Bemessungsregen:**
- Einzelereignis beregchnen: Jährlichkeit und Dauerstufe auswählen → Szenario simulieren
- Bemessungsereignis berechnen: Jährlichkeit auswählen → Bemessung durchführen

## Ergebnisse und Ausgabe

Nach der Simulation zeigt das Hauptarbeitsblatt:

### Spitzenabflusstabelle und Grafik:

- Eine Tabelle listet den Spitzenabfluss, die Zeit bis zum Spitzenabfluss, das Abflussvolumen und das Niederschlagsvolumen für jede simulierte Niederschlagsdauer auf.
- Das Modell identifiziert automatisch die kritische Niederschlagsdauer, d.h. die Dauer, die den maximalen Spitzenabfluss erzeugt.
- Eine entsprechende Grafik visualisiert den Spitzenabfluss über alle getesteten Dauern und ermöglicht eine schnelle Identifizierung des kritischsten Szenarios.

### Detaillierte Simulationsergebnisse für die kritische Dauer:

- Unterhalb der Spitzenabflusszusammenfassung werden detaillierte Ergebnisse für die ausgewählte kritische Niederschlagsdauer angezeigt.
- Diese umfassen Ganglinienformen, Abflussvolumen und Zeitpunkte für jeden Knoten und jedes Teileinzugsgebiet und ermöglichen eine räumliche Analyse der Abflussdynamik.

## Zusätzliche Ausgabearbeitsblätter

### Abflussreihen_TEZGe

Enthält individuelle Ganglinien für jedes Teileinzugsgebiet, die den Abfluss im Zeitverlauf zeigen. Dies ermöglicht den Vergleich des Abflussverhaltens über verschiedene Landschaftseinheiten.

### Abflussreihen_Knoten

Zeigt Ganglinien für jeden definierten Knoten (Punkt) in der Einzugsgebietsstruktur. Diese sind nützlich zur Bewertung des kumulativen Abflusses und der Fließleitung an wichtigen Kontrollpunkten.

### Bemessungsereignisse (nur bei Bemessungsregen einer bestimmten Jährlichkeit)

Enthält Ganglinien für alle simulierten Niederschlagsdauern am ausgewählten Beobachtungsknoten. Dieses Arbeitsblatt unterstützt Sensitivitätsanalysen und hilft bei der Beurteilung, wie verschiedene Niederschlagsdauern den Abfluss an einem bestimmten Standort beeinflussen.

## Dateimanagement und Export

Die Schaltfläche **Exportieren** ermöglicht es, alle Ergebnisse in eine separate Excel-Arbeitsmappe zu kopieren, um sie zu dokumentieren oder weiter zu analysieren.

Um die Dateigröße zu verwalten, insbesondere bei Simulationen mit vielen Teileinzugsgebieten, kann die Schaltfläche **Ergebnisse löschen** verwendet werden. Diese behält das Einzugsgebiet und die Niederschlagseingabe bei, entfernt jedoch alle Simulationsergebnisse und reduziert die Dateigröße für Speicherung oder Weitergabe.


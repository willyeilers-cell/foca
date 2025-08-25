# foca
beginner 
# Zum Compilieren mit PyInstaller
```shell
 C:\Users\vornmae.name\AppData\Local\Programs\Python\Python312\python.exe -m PyInstaller --onefile --noconsole 'C:\Users\vornmae.name\Desktop\python projekte\WLM3.5_GUI.py'
```

# Wirkleistungsrechner (Tkinter)

Ein einfaches Desktop‑Tool zur Berechnung der **Wirkleistung P** eines ohmschen Lastwiderstands aus **Spannung V** und **Widerstand R**, inklusive Vergleich mit einem **gemessenen/angezeigten Leistungswert**. Die App zeigt die **prozentuale Abweichung** farblich an (grün/gelb/rot), validiert Eingaben und bietet **Kopier‑Buttons** für die berechneten Werte.



<img width="1026" height="283" alt="wirkleistung_GUI_3 5" src="https://github.com/user-attachments/assets/4872516d-f79d-4d3a-a7b8-dbea0defb72b" />


## Funktionsweise

* **Berechnung**: $P_\text{calc} = \frac{V^2}{R}$ mit $R$ in **Ohm** (Eingabe in kΩ wird intern ×1000 umgerechnet).
* **Abweichung**: $\Delta\,[\%] = \frac{P_\text{calc} - P_\text{meas}}{P_\text{meas}} \times 100$.
* **Farblogik** (für |Δ|):

  * ≤ **2%** → **grün** (Good)
  * ≤ **5%** → **orange** (Warn)
  * > 5% → **rot** (Bad)

> Die App unterstützt sowohl **Komma** als auch **Punkt** als Dezimaltrennzeichen und normalisiert Eingaben automatisch.

---

## Features

* **Drei parallele Zeilen** für V, R (in kΩ), P(meas) und die berechneten P(calc)
* **Live‑Berechnung** während der Eingabe
* **Farbliche Abweichungsanzeige** (Good/Warn/Bad)
* **Tooltipps** mit Kurzhilfen
* **Kopieren‑Buttons** pro Zeile (P(calc) in Zwischenablage)
* **Eingabevalidierung** inkl. Markierung fehlerhafter Felder
* **Statusleiste** ("Bereit", "Berechnet", Fehlermeldungen)
* **Tastenkürzel**: `Enter` (Berechnen), `Ctrl+R` (Reset), `Esc` (Beenden)
* **Fenstergeometrie wird gemerkt** (persistente UI‑Größe/Position)

---

## Installation

Voraussetzungen:

* **Python 3.8+** (tkinter ist bei den meisten Python‑Distributionen enthalten)
* Getestet unter Windows und Linux (X11); macOS funktioniert in der Regel ebenfalls mit System‑Tk.

```bash
# (Optional) virtuelles Environment anlegen
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Keine zusätzlichen Abhängigkeiten notwendig
```

---

## Starten

Speichere die Datei als `wirkleistungsrechner.py` und starte sie:

```bash
python wirkleistungsrechner.py
```

---

## Bedienung

1. **V** (Volt) eingeben, z. B. `10`.
2. **R** in **kΩ** eingeben, z. B. `2` für 2 kΩ.
3. **P(meas)** (gemessene/angezeigte Leistung in W) eingeben, falls verfügbar.
4. Ergebnis erscheint automatisch: **P(calc)** und **Δ\[%]**.
5. Bei Bedarf **„P(n) kopieren“** klicken, um den Zahlenwert der Zeile in die Zwischenablage zu übernehmen.

**Beispiele**

* V = 10 V, R = 2 kΩ → $P_\text{calc} = 10^2 / 2000 = 0{,}05\,\text{W}$
* V = 5 V, R = 1 kΩ → $P_\text{calc} = 25 / 1000 = 0{,}025\,\text{W}$

---

## Tastenkürzel

| Taste      | Aktion    |
| ---------- | --------- |
| `Enter`    | Berechnen |
| `Ctrl + R` | Reset     |
| `Esc`      | Beenden   |

---

## Dateien & Persistenz

* Die Fenstergeometrie wird in der Datei

  * **`~/.wirkleistungsrechner_ui.json`** (Benutzer‑Home) gespeichert.

### .gitignore‑Hinweis

Falls du diese Datei **nicht** versionieren möchtest, ergänze:

```gitignore
.wirkleistungsrechner_ui.json
```

---

## Fehlerbehandlung & Validierung

* Ungültige Eingaben werden **rot hinterlegt**.
* Nicht‑positive Werte für **R** oder **P(meas)** werden abgelehnt.
* Bei Fehlern zeigt die Statusleiste **„Fehler in Eingaben“** und die Abweichung bleibt `—`.

---

## Projektstruktur (empfohlen)

```
repo/
├─ wirkleistungsrechner.py
├─ README.md
├─ LICENSE            # optional (z. B. MIT)
└─ .gitignore         # optional (.wirkleistungsrechner_ui.json)
```

---

## Lizenz

Empfohlen: **MIT License** (frei, unkompliziert). Lege eine `LICENSE`‑Datei an oder füge bei GitHub „Add a license“ hinzu.

---

## Beitrag & Feedback

Feedback ist willkommen! Erstelle gern ein **Issue** oder einen **Pull Request**:

* Bug entdeckt? Kurze Beschreibung + Schritte zum Reproduzieren
* Verbesserungsidee? Was soll sich ändern und warum?

---

## Roadmap‑Ideen (optional)

* Export der Ergebnisse (CSV/Clipboard für alle Zeilen)
* Einstellbare Schwellwerte für Farblogik
* Zusätzliche Zeilen / dynamische Anzahl
* Einheiten‑Umschalter (R in Ω/kΩ, P in mW/W)
* Mehrsprachigkeit (DE/EN)

---

## Haftungsausschluss

Dieses Tool richtet sich an Lern‑/Laborzwecke. Für sicherheitskritische Messungen sind **geeichte Messmittel** zu verwenden.

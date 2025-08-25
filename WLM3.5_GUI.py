import tkinter as tk
from tkinter import ttk
import os, json

# ----------------------------- Hilfen / Utils --------------------------------
def parse_num(s: str):
    return float(s.strip().replace(",", "."))

class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget, self.text, self.delay = widget, text, delay
        self.tipwin, self.after_id = None, None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, _=None):
        self.after_id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self.tipwin or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwin = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, padding=(6, 4))
        label.pack()

    def _hide(self, _=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tipwin:
            self.tipwin.destroy()
            self.tipwin = None

# ----------------------------- App-Setup -------------------------------------
root = tk.Tk()
root.title("Wirkleistungsrechner (mit Messwert, Abweichung & Farblogik)")

style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

# Schriften/Abstände
root.option_add("*Font", "Arial 10")
style.configure("TLabel", padding=(4, 2))
style.configure("TButton", padding=(10, 5))
style.configure("Header.TLabel", font=("Arial", 10, "bold"), anchor="center")

# Styles für farbige Diff-Labels
style.configure("Good.TLabel", foreground="green")
style.configure("Warn.TLabel", foreground="orange")
style.configure("Bad.TLabel",  foreground="red")
style.configure("Calc.TLabel", foreground="black")

# Entry-Styles (Validierung)
style.configure("Invalid.TEntry", fieldbackground="#ffe6e6")

# ----------------------------- Layout-Container ------------------------------
main = ttk.Frame(root, padding=12)
main.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Spalten flexibel + Mindestbreiten  (jetzt 6 Spalten inkl. Aktion)
# 0: V, 1: R, 2: Pcalc, 3: Pmeas, 4: Diff, 5: Aktion
min_widths = [120, 160, 160, 180, 200, 120]
for c, mw in enumerate(min_widths):
    main.grid_columnconfigure(c, weight=1, uniform="cols", minsize=mw)

# Datenzeilen leicht vertikal mitwachsen
for r in range(1, 4):  # Zeilen 1..3 (nach Header)
    main.grid_rowconfigure(r, weight=1)

# ----------------------------- Überschriften ---------------------------------
headers = [
    "Spannung V [V]",
    "Belastungswiderstand R [kΩ]",
    "Berechnete P [W]",
    "Angezeigte P (Gerät) [W]",
    "Differenz [(Pcalc−Pmeas)/Pmeas] [%]",
    "Aktion",
]
for c, text in enumerate(headers):
    wrap = 160 if c == 4 else None
    lbl = ttk.Label(main, text=text, style="Header.TLabel", wraplength=wrap, justify="center")
    lbl.grid(row=0, column=c, padx=6, pady=(0, 8), sticky="ew")

# ----------------------------- Variablen/Listen ------------------------------
vars_v, vars_r, vars_p_meas = [], [], []
labels_p_calc, labels_diff = [], []
entries_v, entries_r, entries_p = [], [], []

status = tk.StringVar(value="Bereit")

# ----------------------------- Validierung / Eingabe -------------------------
allowed = set("0123456789.,-")
def only_numeric_chars(P):
    return all(ch in allowed for ch in P)
vcmd = (root.register(only_numeric_chars), "%P")

def set_entry_valid(entry: ttk.Entry, ok: bool):
    entry.configure(style="TEntry" if ok else "Invalid.TEntry")

def normalize_decimal(event):
    w = event.widget
    if isinstance(w, ttk.Entry):
        txt = w.get()
        if "," in txt and "." in txt:
            txt = txt.replace(".", "").replace(",", ".")
            w.delete(0, "end")
            w.insert(0, txt)

# ----------------------------- Kopieren --------------------------------------
# ----------------------------- Kopieren --------------------------------------
def copy_value(index: int):
    """Berechnetes P der Zeile index in Zwischenablage kopieren (ohne ' W')."""
    txt = labels_p_calc[index].cget("text")
    # Nur Zahl extrahieren (vor Leerzeichen)
    num = txt.split()[0] if " " in txt else txt
    root.clipboard_clear()
    root.clipboard_append(num)
    status.set(f"P({index+1}) kopiert: {num}")
    root.after(2500, lambda: status.set("Bereit"))


# ----------------------------- Rechnen / Logik -------------------------------
def set_diff_style(label: ttk.Label, color: str):
    if color == "green":
        label.configure(style="Good.TLabel")
    elif color == "orange":
        label.configure(style="Warn.TLabel")
    elif color == "red":
        label.configure(style="Bad.TLabel")
    else:
        label.configure(style="TLabel")

def berechnen(*_):
    # Default: alles auf "normal" bis Fehler festgestellt wird
    for i in range(3):
        set_entry_valid(entries_v[i], True)
        set_entry_valid(entries_r[i], True)
        set_entry_valid(entries_p[i], True)
    any_error = False

    for i in range(3):
        try:
            v = parse_num(vars_v[i].get())
            r_kohm = parse_num(vars_r[i].get())
            if r_kohm <= 0:
                raise ValueError
            r_ohm = r_kohm * 1000.0
            p_calc = (v * v) / r_ohm
            labels_p_calc[i].configure(text=f"{p_calc:.6f} W", style="Calc.TLabel")

            # Vergleich mit Anzeige (Basis: Messwert)
            try:
                p_meas = parse_num(vars_p_meas[i].get())
                if p_meas <= 0:
                    raise ValueError
                diff = (p_calc - p_meas) / p_meas * 100.0
                absdiff = abs(diff)

                if absdiff <= 2:
                    color = "green"
                elif absdiff <= 5:
                    color = "orange"
                else:
                    color = "red"

                labels_diff[i].configure(text=f"{diff:+.2f} %")
                set_diff_style(labels_diff[i], color)
            except Exception:
                labels_diff[i].configure(text="—")
                set_diff_style(labels_diff[i], "red")
                set_entry_valid(entries_p[i], False)
                any_error = True

        except Exception:
            labels_p_calc[i].configure(text="—")
            labels_diff[i].configure(text="—")
            set_diff_style(labels_diff[i], "red")
            # Feld-Markierung
            try:
                parse_num(vars_v[i].get())
            except Exception:
                set_entry_valid(entries_v[i], False)
            try:
                r_test = parse_num(vars_r[i].get())
                if r_test <= 0:
                    raise ValueError
            except Exception:
                set_entry_valid(entries_r[i], False)
            any_error = True

    status.set("Fehler in Eingaben" if any_error else "Berechnet")

def reset():
    for i in range(3):
        vars_v[i].set("")
        vars_r[i].set("")
        vars_p_meas[i].set("")
        labels_p_calc[i].configure(text="—", style="TLabel")
        labels_diff[i].configure(text="—", style="TLabel")
        set_entry_valid(entries_v[i], True)
        set_entry_valid(entries_r[i], True)
        set_entry_valid(entries_p[i], True)
    status.set("Zurückgesetzt")

# ----------------------------- Eingaben/Zeilen -------------------------------
for r in range(3):
    vvar = tk.StringVar()
    rvar = tk.StringVar()
    pvar = tk.StringVar()

    # Live-Berechnung bei jeder Änderung
    vvar.trace_add("write", berechnen)
    rvar.trace_add("write", berechnen)
    pvar.trace_add("write", berechnen)

    vars_v.append(vvar); vars_r.append(rvar); vars_p_meas.append(pvar)

    e_v = ttk.Entry(main, textvariable=vvar, validate="key", validatecommand=vcmd)
    e_v.grid(row=r+1, column=0, padx=6, pady=4, sticky="ew")
    e_v.bind("<KeyRelease>", normalize_decimal)
    entries_v.append(e_v)
    Tooltip(e_v, "Spannung in Volt (Komma oder Punkt möglich)")

    e_r = ttk.Entry(main, textvariable=rvar, validate="key", validatecommand=vcmd)
    e_r.grid(row=r+1, column=1, padx=6, pady=4, sticky="ew")
    e_r.bind("<KeyRelease>", normalize_decimal)
    entries_r.append(e_r)
    Tooltip(e_r, "Belastungswiderstand in kΩ (> 0)")

    lbl_calc = ttk.Label(main, text="—", style="Calc.TLabel")
    lbl_calc.grid(row=r+1, column=2, padx=6, pady=4, sticky="ew")
    labels_p_calc.append(lbl_calc)
    Tooltip(lbl_calc, "Berechnete Wirkleistung Pcalc")

    e_p_meas = ttk.Entry(main, textvariable=pvar, validate="key", validatecommand=vcmd)
    e_p_meas.grid(row=r+1, column=3, padx=6, pady=4, sticky="ew")
    e_p_meas.bind("<KeyRelease>", normalize_decimal)
    entries_p.append(e_p_meas)
    Tooltip(e_p_meas, "Gemessene/angezeigte Leistung (W)")

    lbl_diff = ttk.Label(main, text="—")
    lbl_diff.grid(row=r+1, column=4, padx=6, pady=4, sticky="ew")
    labels_diff.append(lbl_diff)
    Tooltip(lbl_diff, "Abweichung (Pcalc−Pmeas)/Pmeas in %")

    # --- NEU: Kopieren-Button pro Zeile (Spalte 5) ---
    btn_copy_row = ttk.Button(main, text=f"P({r+1}) kopieren", command=lambda idx=r: copy_value(idx))
    btn_copy_row.grid(row=r+1, column=5, padx=6, pady=4, sticky="e")
    Tooltip(btn_copy_row, f"Berechneten Wert der Zeile {r+1} in die Zwischenablage kopieren")

# ----------------------------- Buttonzeile (Reset) ---------------------------
btn_frame = ttk.Frame(main)
btn_frame.grid(row=4, column=0, columnspan=6, sticky="e", pady=(10, 0))

btn_reset = ttk.Button(btn_frame, text="Reset", command=reset)
btn_reset.pack(side="right")

# ----------------------------- Statusleiste ----------------------------------
statusbar = ttk.Label(root, textvariable=status, anchor="w")
statusbar.grid(row=99, column=0, sticky="ew")
root.grid_columnconfigure(0, weight=1)

# ----------------------------- Shortcuts -------------------------------------
root.bind("<Return>", lambda e: berechnen())
root.bind("<Control-r>", lambda e: reset())
root.bind("<Escape>", lambda e: root.destroy())

# ----------------------------- Geometrie merken ------------------------------
STATE_FILE = os.path.join(os.path.expanduser("~"), ".wirkleistungsrechner_ui.json")
def save_geometry():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"geometry": root.wm_geometry()}, f)
    except Exception:
        pass
def restore_geometry():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            geo = json.load(f).get("geometry")
            if geo: root.geometry(geo)
    except Exception:
        pass

restore_geometry()
root.protocol("WM_DELETE_WINDOW", lambda: (save_geometry(), root.destroy()))

# ----------------------------- Startzustand ----------------------------------
berechnen()  # initiale Anzeige
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())

root.mainloop()

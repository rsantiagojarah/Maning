# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Single-file Python desktop application (`Caudales_Maning.py`) for hydraulic engineering calculations using the Manning equation on partially-filled circular pipes. It reads CSV/Excel input (columns: `Caudal`, `Diametro`, `Rugosidad`, `Pendiente`), computes hydraulic properties via `scipy.optimize.fsolve`, and writes results to CSV/Excel.

### Dependencies

- Python 3.12+ with `numpy`, `pandas`, `scipy`, `openpyxl` (installed via `pip install -r requirements.txt`)
- `python3-tk` system package (for tkinter GUI)

### Running the application

```bash
python3 Caudales_Maning.py
```

The app uses tkinter file dialogs, so it requires a display. In headless environments, start Xvfb first:

```bash
Xvfb :99 -screen 0 1280x1024x24 &
export DISPLAY=:99
python3 Caudales_Maning.py
```

### Testing the core logic without GUI

You can test the hydraulic calculation function without the GUI by importing only the function definition (everything before the `# Ventana para seleccionar archivo de entrada` comment). Example:

```python
exec(open('Caudales_Maning.py').read().split('# Ventana para seleccionar archivo de entrada')[0])
result = calcular_propiedades_hidraulicas(Q=0.05, D=0.3, n=0.013, S=0.001)
```

### Notes

- No automated test suite exists in this repository.
- No linter or build system is configured.
- A sample input file `test_data.csv` is provided for quick testing.

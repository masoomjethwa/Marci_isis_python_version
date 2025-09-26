
---

## 📄 `README.md`

````markdown
# 🛰️ MARCI ISIS Processing Pipeline

> Modern Python interface for processing **MRO MARCI** images using **USGS ISIS** software.

---

## 📦 Features

- ✅ Process `.IMG` files from the PDS Imaging Node
- ✅ ISIS integration (`marci2isis`, `spiceinit`, `marcical`, `explode`, `cam2map`, `isis2std`)
- ✅ SPICE Web fallback support
- ✅ Clean, modular Python (PEP8, type-hinted, Python 3.10+)
- ✅ Logging to file + console
- ✅ Auto map template generation from projection presets
- ✅ Optional deletion of intermediate files
- ✅ CLI support for batch processing

---

## 🚀 Prerequisites

- ✅ Python **3.10+**
- ✅ [ISIS](https://github.com/USGS-Astrogeology/ISIS3) (installed and sourced)
- ✅ ISIS data (`$ISISDATA`) and MRO SPICE base files

---

## 📁 Installation

```bash
git clone https://github.com/your-username/marci-isis-pipeline.git
cd marci-isis-pipeline
````

> 🔁 Ensure your Python environment has access to `isis3` commands in `$PATH`.

---

## 📸 Image Preparation

1. Download `.IMG` files from PDS:

```bash
wget https://pds-imaging.jpl.nasa.gov/data/mro/.../YOUR_IMAGE.IMG
```

2. Place them in a working directory alongside the script.

---

## 🔧 Usage

### 💡 Process with a predefined projection

```bash
python marci_isis_processing.py --projection simplecyl --delete 1
```

| Projection Name | Description                     |
| --------------- | ------------------------------- |
| `simplecyl`     | SimpleCylindrical (default)     |
| `polar`         | PolarStereographic (north pole) |
| `eqc`           | Equirectangular                 |

This generates a temporary `.map` file for the selected projection.

---

### 💡 Process with a custom `.map` file

```bash
python marci_isis_processing.py --map path/to/your_custom.map --delete 0
```

---

### 💡 Specify a working directory (optional)

```bash
python marci_isis_processing.py --projection eqc --dir path/to/images --delete 1
```

---

## 🧹 File Cleanup

Use the `--delete 1` flag to delete intermediate `.cub`, `.lev1.cub`, and `.bandX.cub` files after processing.

---

## 📂 Output Files

| Extension    | Description                         |
| ------------ | ----------------------------------- |
| `.cub`       | Raw ISIS cube from `marci2isis`     |
| `.lev1.cub`  | Calibrated cube from `marcical`     |
| `.band*.cub` | Band-separated cubes from `explode` |
| `.lev2.cub`  | Map-projected cubes from `cam2map`  |
| `.png`       | Final exported PNG from `isis2std`  |
| `.log`       | Processing log file                 |

---

## 📒 Log File

All output (including warnings and errors) is logged to:

```bash
marci_isis_processing.log
```

---

## 🌐 SPICE Web Fallback

If `spiceinit` fails due to missing local kernels, the script automatically retries with:

```bash
spiceinit from=file.cub web=true
```

Ensure your machine is online to use this.

---

## 🧪 Sample Run

```bash
python marci_isis_processing.py --projection simplecyl --delete 0
```

Output:

```
[INFO] Running: marci2isis from=...
[INFO] Running: spiceinit from=...
[WARNING] spiceinit failed, retrying with web=true...
...
[INFO] ✅ MARCI processing complete.
```

---

## 📁 Project Structure

```bash
marci-isis-pipeline/
├── marci_isis_processing.py     # Main Python script
├── marci_isis_processing.log    # Log file (auto-created)
├── simplecyl.map                # Map template (auto-created if using --projection)
├── *.IMG                        # Input files (you provide)
└── *.png                        # Final processed outputs
```

---

## 👨‍💻 Author

* **Script Author:** `@mp10`
* **AI Refactor Assistant:** `[TGC-DD26092025]`

---

## 📜 License

This project is released under the MIT License.

---

## 📬 Questions?

If you encounter issues, please:

1. Ensure ISIS is properly installed and sourced.
2. Check `marci_isis_processing.log` for detailed error messages.
3. Verify your `.IMG` files are complete and valid.
```


# Quick‑Start Guide for simple‑ml‑skill

## 1️⃣ Run the provided example trainer  

```bash
python scripts/train_iris.py
```

The script will:
- Load `assets/iris_example.csv`
- Train a Logistic Regression model (default 100 epochs)
- Print accuracy/precision/recall and save `model.pkl`

## 2️⃣ Use your own CSV  

Your file must follow the schema defined in `references/data_schema.json`:

```json
{
  "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
  "target": "species"
}
```

Run:

```bash
python scripts/train_iris.py -d path/to/your_file.csv -n 200
```

All results are saved to `model.pkl` in the skill’s root directory.

## 3️⃣ Retrieve model diagnostics  

After training, you can inspect metrics printed by the script. If you need more
details (e.g., confusion matrix), ask Claude to **read** `references/README.md`
and request a custom extension.
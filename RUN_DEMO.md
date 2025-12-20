# RUN THIS FIRST!

## Activate Virtual Environment

```powershell
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt.

## Then Run the Demo

```powershell
python fraud_demo.py
```

---

## Full Command Sequence

```powershell
# 1. Activate venv
venv\Scripts\activate

# 2. Run demo
python fraud_demo.py
```

---

## If You See "No module named 'kafka'" Error

This means you forgot to activate the virtual environment!

**Solution:**
```powershell
venv\Scripts\activate
python fraud_demo.py
```

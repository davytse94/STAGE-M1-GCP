# test_import.py
try:
    from google.cloud import monitoring_v3
    print("Importation réussie.")
except ImportError as e:
    print(f"Erreur d'importation : {e}")

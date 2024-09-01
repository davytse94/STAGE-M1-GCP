from google.cloud import monitoring_v3
from google.auth import default

# Récupérer les informations d'authentification par défaut
credentials, project = default()

# Initialiser le client de service de métriques
client = monitoring_v3.MetricServiceClient(credentials=credentials)

# Nom du projet pour l'API Monitoring
project_name = f"projects/{project}"

# Lister les descripteurs de métriques
metric_descriptors = client.list_metric_descriptors(name=project_name)

# Afficher les descripteurs de métriques disponibles
for descriptor in metric_descriptors:
    print(f"Metric Type: {descriptor.type}")
    print(f"Metric Display Name: {descriptor.display_name}")
    print(f"Description: {descriptor.description}")
    print("-" * 80)

print("Liste des métriques disponibles récupérée.")

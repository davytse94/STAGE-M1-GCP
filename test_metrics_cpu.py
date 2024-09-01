from google.cloud import monitoring_v3
from google.auth import default
import datetime
import csv

# Récupérer les informations d'authentification par défaut
# Retrieve the default authentication information
credentials, project = default()

# Initialiser le client de service de métriques
# Initialize the metrics service client
client = monitoring_v3.MetricServiceClient(credentials=credentials)

# Nom du projet pour l'API Monitoring
# Project name for the Monitoring API
project_name = f"projects/{project}"

# Récupérer l'heure actuelle en temps universel coordonné (UTC)
maintenant = datetime.datetime.now(datetime.timezone.utc)

# Calculer le temps de fin et le temps de début pour une fenêtre d'une heure
temps_fin = maintenant
temps_debut = maintenant - datetime.timedelta(hours=1)

# Créer l'intervalle de temps pour la requête
intervalle = monitoring_v3.TimeInterval(
    {
        "end_time": {"seconds": int(temps_fin.timestamp()), "nanos": temps_fin.microsecond * 1000},
        "start_time": {"seconds": int(temps_debut.timestamp()), "nanos": temps_debut.microsecond * 1000},
    }
)

# Effectuer la requête pour lister les séries temporelles des métriques
results = client.list_time_series(
    request={
        "name": project_name,
        "filter": 'metric.type = "compute.googleapis.com/instance/cpu/utilization"',
        "interval": intervalle,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }
)

# Ouvrir le fichier CSV pour écrire les résultats
with open('/Users/davy/Downloads/stagem1/projet/ansible/test_metrics_cpu.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Écrire les en-têtes du fichier CSV
    writer.writerow(['Instance', 'Metric Type', 'Timestamp', 'Value'])
    
    # Parcourir les résultats de la requête
    for result in results:
        # Obtenir le nom de l'instance et le type de métrique
        instance_name = result.resource.labels['instance_id']
        metric_type = result.metric.type
        
        # Parcourir les points de données de chaque résultat
        for point in result.points:
            # Obtenir le timestamp et la valeur de la métrique
            timestamp = point.interval.end_time
            value = point.value.double_value
            
            # Écrire les informations dans le fichier CSV
            writer.writerow([instance_name, metric_type, timestamp, value])

print("Les résultats des métriques ont été écrits dans le fichier CSV.")

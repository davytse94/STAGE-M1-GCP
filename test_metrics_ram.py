from google.cloud import monitoring_v3
from google.auth import default
import datetime
import csv
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Récupérer les informations d'authentification par défaut
credentials, project = default()

# Initialiser le client de service de métriques
client = monitoring_v3.MetricServiceClient(credentials=credentials)

# Nom du projet pour l'API Monitoring
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

# Filtre pour les métriques d'utilisation de la mémoire de l'agent Ops
filters = [
    'metric.type = "agent.googleapis.com/memory/percent_used"',
    'metric.type = "agent.googleapis.com/memory/bytes_used"'
]

# Ouvrir le fichier CSV pour écrire les résultats
csv_file_path = '/Users/davy/Downloads/stagem1/projet/ansible/test_metrics_ram_ops_agent.csv'

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Écrire les en-têtes du fichier CSV
    writer.writerow(['Instance', 'Metric Type', 'Timestamp', 'Value'])
    
    # Parcourir les filtres pour obtenir les métriques d'utilisation de la mémoire
    for metric_filter in filters:
        logging.info(f"Récupération des métriques pour le filtre: {metric_filter}")
        try:
            results = client.list_time_series(
                request={
                    "name": project_name,
                    "filter": metric_filter,
                    "interval": intervalle,
                    "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                }
            )
            
            result_count = 0
            # Parcourir les résultats de la requête
            for result in results:
                result_count += 1
                # Obtenir le nom de l'instance et le type de métrique
                instance_name = result.resource.labels.get('instance_id', 'Unknown')
                metric_type = result.metric.type
                
                logging.info(f"Traitement des données pour l'instance: {instance_name}, métrique: {metric_type}")
                
                # Parcourir les points de données de chaque résultat
                for point in result.points:
                    # Obtenir le timestamp et le convertir en chaîne ISO 8601
                    timestamp = point.interval.end_time.isoformat()
                    
                    # Essayer de récupérer la valeur, quel que soit son type
                    if hasattr(point.value, 'double_value'):
                        value = point.value.double_value
                    elif hasattr(point.value, 'int64_value'):
                        value = point.value.int64_value
                    else:
                        logging.warning(f"Type de valeur inattendu pour {metric_type}: {type(point.value)}")
                        value = str(point.value)  # Convertir en chaîne si le type est inattendu
                    
                    # Écrire les informations dans le fichier CSV
                    writer.writerow([instance_name, metric_type, timestamp, value])
            
            logging.info(f"Nombre total de résultats pour {metric_filter}: {result_count}")
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des métriques pour {metric_filter}: {e}", exc_info=True)

logging.info(f"Les résultats des métriques d'utilisation de la RAM ont été écrits dans le fichier CSV : {csv_file_path}")
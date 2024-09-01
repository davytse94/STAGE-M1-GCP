from google.cloud import compute_v1

# Initialise le client Compute Engine
compute_client = compute_v1.InstancesClient()

# Remplacez par votre projet Google Cloud
project = 'devops-stage-426707'

# Récupère la liste des instances VM
instances = compute_client.list(project=project, zone='europe-west1-b')

# Éteint chaque instance VM trouvée
for instance in instances:
    print(f'Arrêt de l\'instance {instance.name}')
    operation = compute_client.stop(project=project, zone='europe-west1-b', instance=instance.name)
    operation.result()  # Attend la fin de l'opération

print('Toutes les instances VM ont été éteintes avec succès.')

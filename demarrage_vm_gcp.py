from google.cloud import compute_v1

# Initialise le client Compute Engine
compute_client = compute_v1.InstancesClient()

# Remplacez par votre projet Google Cloud
project = 'devops-stage-426707'

# Récupère la liste des instances VM
instances = compute_client.list(project=project, zone='europe-west1-b')

# Démarre chaque instance VM trouvée
for instance in instances:
    print(f'Démarrage de l\'instance {instance.name}')
    operation = compute_client.start(project=project, zone='europe-west1-b', instance=instance.name)
    operation.result()  # Attend la fin de l'opération

print('Toutes les instances VM ont été démarrées avec succès.')

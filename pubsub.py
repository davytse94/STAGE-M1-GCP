import pandas as pd
from google.cloud import pubsub_v1
import json

# Chemin vers le fichier CSV
csv_file_path = 'data.csv'

# Lire le fichier CSV
data = pd.read_csv(csv_file_path)

# Configurer Pub/Sub
project_id = 'devops-stage-426707'
topic_id = 'mytopic'
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Fonction pour publier un message
def publish_message(data):
    message = json.dumps(data)
    future = publisher.publish(topic_path, message.encode('utf-8'))
    print(f'Published message ID: {future.result()}')

# Publier chaque ligne du CSV
for index, row in data.iterrows():
    publish_message(row.to_dict())

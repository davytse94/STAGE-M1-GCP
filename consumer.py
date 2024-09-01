import json
import time
from kafka import KafkaConsumer

if __name__ == "__main__":
    # Capturer le temps de début
    start_time = time.time()

    # Initialiser le consommateur Kafka
    consumer = KafkaConsumer(
        'test',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # Lire et afficher les messages du sujet
    for message in consumer:
        data = message.value
        print(data)
        if 'end_of_transmission' in data and data['end_of_transmission']:
            print("End of transmission received.")
            break

    # Capturer le temps de fin
    end_time = time.time()

    # Calculer et afficher le temps écoulé
    elapsed_time = end_time - start_time
    print(f"Temps total écoulé: {elapsed_time:.2f} secondes")

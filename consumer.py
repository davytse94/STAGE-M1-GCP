import json
from kafka import KafkaConsumer

if __name__ == "__main__":
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
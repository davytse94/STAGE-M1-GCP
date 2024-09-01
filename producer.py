import pandas as pd
import json
import time
from kafka import KafkaProducer


def serializer(message):
    return json.dumps(message).encode('utf-8')

def inject_to_kafka(producer, df, topic, divide, amplifier):
    sorted_df = df.sort_values(by='modified_timestamp')
    i = 0

    for index, row in sorted_df.iterrows():
        current_timestamp = row['modified_timestamp']
        if i == 0:
            previous_timestamp = row['modified_timestamp']
        i += 1
        if previous_timestamp is not None:
            time_difference = (current_timestamp - previous_timestamp) / 1000
            if time_difference > 0:
                print(f"Waiting for {time_difference} seconds before sending the next message...")
                time.sleep(time_difference / int(divide))

        message = {
            'timestamp': current_timestamp,
            'data': row.to_dict()
        }

        print(json.dumps(message, ensure_ascii=False))

        for _ in range(amplifier):
            producer.send(topic, value=message)

        previous_timestamp = current_timestamp

    end_of_transmission_message = {'end_of_transmission': True}
    producer.send(topic, value=end_of_transmission_message)
    print(json.dumps(end_of_transmission_message, ensure_ascii=False))

    producer.flush()
    return producer

if __name__ == "__main__":
    # Initialiser le producteur Kafka
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=serializer
    )

    # Lire le fichier CSV dans un DataFrame
    df = pd.read_csv('data.csv')

    # Assurez-vous que la colonne 'modified_timestamp' est de type datetime et convertissez-la en timestamp (millisecondes)
    df['modified_timestamp'] = pd.to_datetime(df['modified_timestamp']).astype(int) / 10**6

    # Appel de la fonction pour injecter les données dans Kafka
    inject_to_kafka(producer, df, topic='test', divide=1, amplifier=1)
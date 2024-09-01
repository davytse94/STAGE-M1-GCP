from confluent_kafka import Producer

# Configuration du producteur
producer = Producer({'bootstrap.servers': '34.76.22.195:9092'})
topic = 'test'

def delivery_report(err, msg):
    """ Appelée une fois que le message a été livré ou a échoué à être livré """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Lecture du fichier CSV et envoi des lignes en tant que messages
with open('data.csv', mode='r') as file:
    for line in file:
        producer.produce(topic, line.strip(), callback=delivery_report)
        producer.poll(0)

producer.flush()

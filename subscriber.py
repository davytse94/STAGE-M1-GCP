from google.cloud import pubsub_v1
from google.api_core import retry
import logging
import signal
import sys
import time
import concurrent.futures

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration de Pub/Sub
project_id = "devops-stage-426707"
subscription_id = "mysubscription"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Compteur de messages
message_count = 0

def callback(message):
    global message_count
    try:
        logging.info(f'Received message: {message.data.decode("utf-8")}')
        message.ack()
        message_count += 1
        logging.info(f'Message acknowledged. Total messages processed: {message_count}')
    except Exception as e:
        logging.error(f'Error in callback: {e}', exc_info=True)

@retry.Retry(predicate=retry.if_exception_type(Exception))
def subscribe_with_retry():
    return subscriber.subscribe(subscription_path, callback=callback)

def shutdown(signal, frame):
    logging.info('Signal received, stopping listener...')
    if 'streaming_pull_future' in globals():
        streaming_pull_future.cancel()
    logging.info('Listener stopped.')
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def main():
    global streaming_pull_future
    while True:
        try:
            logging.info(f'Starting to listen for messages on {subscription_path}...')
            streaming_pull_future = subscribe_with_retry()
            streaming_pull_future.result(timeout=300)  # Timeout après 5 minutes
        except concurrent.futures.TimeoutError:
            logging.info("No messages received for 5 minutes, restarting subscription")
        except Exception as e:
            logging.error(f'An error occurred: {e}', exc_info=True)
            time.sleep(10)  # Attendre avant de réessayer
        finally:
            if 'streaming_pull_future' in locals():
                streaming_pull_future.cancel()
            logging.info('Streaming pull future cancelled. Restarting...')
        
        # Log périodique
        logging.info(f'Total messages processed so far: {message_count}')
        time.sleep(1)  # Petite pause avant de redémarrer

if __name__ == "__main__":
    main()
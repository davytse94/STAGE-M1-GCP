#!/bin/bash

# Variables
TOPIC_NAME="TOPIC"
SUBSCRIBER_NAME="SUBCRIBER"

# Fonction d'affichage de l'aide
function show_help() {
    echo "Usage: $0 [-t TOPIC_NAME] [-s SUBSCRIBER_NAME]"
    echo "Options:"
    echo "  -t TOPIC_NAME        Specify the topic name (default: TOPIC)"
    echo "  -s SUBSCRIBER_NAME   Specify the subscriber name (default: SUBSCRIBER)"
    echo "  -h                   Show this help message"
}

# Affichage des valeurs des variables (pour vérification)
echo "TOPIC_NAME: $TOPIC_NAME"
echo "SUBSCRIBER_NAME: $SUBSCRIBER_NAME"


# Traitement des options
while getopts "t:s:h" opt; do
  case $opt in
    t) TOPIC_NAME="$OPTARG" ;;
    s) SUBSCRIBER_NAME="$OPTARG" ;;
    h) show_help; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; show_help; exit 1 ;;
  esac
done

# Création du topic 
gcloud pubsub topics create $TOPIC_NAME

# Création du subscriber pour le topic 
gcloud pubsub subscriptions create --topic $TOPIC_NAME $SUBSCRIBER_NAME


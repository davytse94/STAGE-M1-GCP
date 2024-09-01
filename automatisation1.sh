#!/bin/bash

# Variables
COMPTE_SERVICE="davy1998"
PROJECT_ID="devops-stage-426707"
API_KEY_FILE="api_key.txt"


# Fonction d'affichage de l'aide
function show_help() {
    echo "Usage: $0 [-a COMPTE_SERVICE] [-p PROJECT_ID] [-k API_KEY_FILE]"
}

# Traitement des options
while getopts "a:p:k:h" opt; do
  case $opt in
    a) COMPTE_SERVICE="$OPTARG" ;;
    p) PROJECT_ID="$OPTARG" ;;
    k) API_KEY_FILE="$OPTARG" ;;
    h) show_help; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; show_help; exit 1 ;;
  esac
done

# Validation de la longueur de COMPTE_SERVICE
if [ -n "$COMPTE_SERVICE" ]; then
    if [ ${#COMPTE_SERVICE} -lt 6 ] || [ ${#COMPTE_SERVICE} -gt 30 ]; then
        echo "Error: COMPTE_SERVICE must be between 6 and 30 characters."
        echo "Error: COMPTE_SERVICE doit avoir entre 6 et 30 characteres."
        exit 1
    fi
fi

# Affichage des valeurs des variables (pour vérification)
echo "COMPTE_SERVICE: $COMPTE_SERVICE"
echo "PROJECT_ID: $PROJECT_ID"
echo "API_KEY_FILE: $API_KEY_FILE"

# Enable necessary services
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable pubsub.googleapis.com

# Run Python script
python test_import.py

# Create a service account
gcloud iam service-accounts create $COMPTE_SERVICE --display-name="Service Account for $COMPTE_SERVICE"

# Add IAM policy bindings for the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin.v1"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/billing.projectManager"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.futureReservationViewer"

gcloud iam service-accounts keys create key_compte_service.json \
  --iam-account=$COMPTE_SERVICE@$PROJECT_ID.iam.gserviceaccount.com


# Create API Key
#API_KEY=$(gcloud alpha services api-keys create --display-name="API Key for $COMPTE_SERVICE" --project=$PROJECT_ID --format="json")

# Save API Key to file
#echo "$API_KEY" > $API_KEY_FILE

#echo "API Key created and saved to $API_KEY_FILE"


# Install necessary Python packages
pip install google-cloud-monitoring google-auth
pip install google-cloud-billing

# Fichier de récuperation des métriques 
#./automatisationmetric.sh


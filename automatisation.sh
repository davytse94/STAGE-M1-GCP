#!/bin/bash

# Variables par défaut
TEMPLATE_NAME="my-template"
MACHINE_TYPE="n1-standard-1"
IMAGE_FAMILY="debian-11"
IMAGE_PROJECT="debian-cloud"
BOOT_DISK_SIZE="200GB"
TAGS="http-server,https-server"
INSTANCE_GROUP_NAME="example-group"
BASE_INSTANCE_NAME="example-instance"
INSTANCE_COUNT=6
ZONE="europe-west1-b"
SSH_KEY_DIR="clé"
SSH_KEY_NAME="ANSIBLE"
USERNAME="davy"
PROJECT_ID="devops-stage-426707"
SSH_KEY_PATH="clé/ANSIBLE"
INI_FILE="hosts.ini"
INVENTORY_FILE="inventory.ini"
OPS="TRUE"
KAFKA="TRUE"
#STORM NE MARCHE PAS LAISSER EN FALSE
STORM="FALSE"

# Fonction d'affichage de l'aide
function show_help() {
    echo "Usage: $0 [-t TEMPLATE_NAME] [-m MACHINE_TYPE] [-f IMAGE_FAMILY] [-p IMAGE_PROJECT] [-b BOOT_DISK_SIZE]"
    echo "          [-g INSTANCE_GROUP_NAME] [-n BASE_INSTANCE_NAME] [-c INSTANCE_COUNT] [-z ZONE]"
    echo "          [-d SSH_KEY_DIR] [-k SSH_KEY_NAME] [-u USERNAME] [-j PROJECT_ID] [-s SSH_KEY_PATH]"
    echo "          [-i INI_FILE] [-v INVENTORY_FILE] [-o OPS] [-a KAFKA] [-e STORM] [-h]"
}

# Traitement des options
while getopts "t:m:f:p:b:g:n:c:z:d:k:u:j:s:i:v:o:a:e:h" opt; do
  case $opt in
    t) TEMPLATE_NAME="$OPTARG" ;;
    m) MACHINE_TYPE="$OPTARG" ;;
    f) IMAGE_FAMILY="$OPTARG" ;;
    p) IMAGE_PROJECT="$OPTARG" ;;
    b) BOOT_DISK_SIZE="$OPTARG" ;;
    g) INSTANCE_GROUP_NAME="$OPTARG" ;;
    n) BASE_INSTANCE_NAME="$OPTARG" ;;
    c) INSTANCE_COUNT="$OPTARG" ;;
    z) ZONE="$OPTARG" ;;
    d) SSH_KEY_DIR="$OPTARG" ;;
    k) SSH_KEY_NAME="$OPTARG" ;;
    u) USERNAME="$OPTARG" ;;
    j) PROJECT_ID="$OPTARG" ;;
    s) SSH_KEY_PATH="$OPTARG" ;;
    i) INI_FILE="$OPTARG" ;;
    v) INVENTORY_FILE="$OPTARG" ;;
    o) OPS="$OPTARG" ;;
    a) KAFKA="$OPTARG" ;;
    e) STORM="$OPTARG" ;;
    h) show_help; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; show_help; exit 1 ;;
  esac
done

# Affichage des valeurs des variables (pour vérification)
echo "TEMPLATE_NAME: $TEMPLATE_NAME"
echo "MACHINE_TYPE: $MACHINE_TYPE"
echo "IMAGE_FAMILY: $IMAGE_FAMILY"
echo "IMAGE_PROJECT: $IMAGE_PROJECT"
echo "BOOT_DISK_SIZE: $BOOT_DISK_SIZE"
echo "TAGS: $TAGS"
echo "INSTANCE_GROUP_NAME: $INSTANCE_GROUP_NAME"
echo "BASE_INSTANCE_NAME: $BASE_INSTANCE_NAME"
echo "INSTANCE_COUNT: $INSTANCE_COUNT"
echo "ZONE: $ZONE"
echo "SSH_KEY_DIR: $SSH_KEY_DIR"
echo "SSH_KEY_NAME: $SSH_KEY_NAME"
echo "USERNAME: $USERNAME"
echo "PROJECT_ID: $PROJECT_ID"
echo "SSH_KEY_PATH: $SSH_KEY_PATH"
echo "INI_FILE: $INI_FILE"
echo "INVENTORY_FILE: $INVENTORY_FILE"
echo "OPS: $OPS"
echo "KAFKA: $KAFKA"
echo "STORM: $STORM"

# Active l'API compute engine de google Cloud Platform
gcloud services enable compute.googleapis.com


# Créer un modèle d'instance
gcloud compute instance-templates create $TEMPLATE_NAME \
    --machine-type=$MACHINE_TYPE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --tags=$TAGS

# Créer un groupe d'instances managées
gcloud compute instance-groups managed create $INSTANCE_GROUP_NAME \
    --base-instance-name=$BASE_INSTANCE_NAME \
    --template=$TEMPLATE_NAME \
    --size=$INSTANCE_COUNT \
    --zone=$ZONE

echo "Création du modèle et des instances terminée."

# Retirer les instances du groupe sans les supprimer
gcloud compute instance-groups managed abandon-instances $INSTANCE_GROUP_NAME \
    --instances=$(gcloud compute instance-groups managed list-instances $INSTANCE_GROUP_NAME \
                  --zone=$ZONE --format="value(NAME)" | tr '\n' ',') \
    --zone=$ZONE

echo "Les instances ont été retirées du groupe mais continuent d'exister en tant qu'instances individuelles."

# Créer un répertoire pour le stockage des clés
mkdir -p $SSH_KEY_DIR

# Créer une paire de clés SSH
yes y | ssh-keygen -t rsa -b 2048 -f $SSH_KEY_DIR/$SSH_KEY_NAME -N ""

# Extraire la clé publique
SSH_KEY_CONTENT=$(cat $SSH_KEY_DIR/${SSH_KEY_NAME}.pub)

# Créer un fichier temporaire pour la clé publique
echo "$USERNAME:$SSH_KEY_CONTENT" > ssh_keys.txt

# Ajouter la clé publique aux métadonnées du projet
gcloud compute project-info add-metadata --metadata-from-file=ssh-keys=ssh_keys.txt

# Supprimer le fichier temporaire
rm ssh_keys.txt

echo "Création et configuration de la clé SSH terminée."


# Fonction pour récupérer l'IP externe d'une instance
get_external_ip() {
    local instance_name=$1
    gcloud compute instances describe $instance_name --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
}

# Récupérer les noms des instances
INSTANCE_NAMES=($(gcloud compute instances list --filter="name~'^${BASE_INSTANCE_NAME}'" --zones=$ZONE --format="value(name)"))

if [ ${#INSTANCE_NAMES[@]} -eq 0 ]; then
    echo "Aucune instance trouvée. Veuillez vérifier que les instances ont été créées correctement."
    exit 1
fi

echo "Instances trouvées : ${INSTANCE_NAMES[@]}"

# Initialiser des tableaux pour stocker les IPs des instances
INSTANCE_IPS=()

# Récupérer les IPs externes des instances
for instance in "${INSTANCE_NAMES[@]}"; do
    IP=$(get_external_ip $instance)
    if [ -z "$IP" ]; then
        echo "Impossible de récupérer l'IP externe de l'instance $instance"
        exit 1
    fi
    echo "Instance: $instance, IP: $IP"  # Debug message
    INSTANCE_IPS+=($IP)
done

# Vérifier que les IPs ont été récupérées
echo "Récupération des IPs: ${INSTANCE_IPS[@]}"

# Nettoyer le fichier d'inventaire existant
echo "[ops_agents]" > $INVENTORY_FILE

# Mettre à jour le fichier inventory.ini avec les IPs récupérées
for ip in "${INSTANCE_IPS[@]}"; do
    echo "$ip ansible_user=davy ansible_ssh_private_key_file=clé/ANSIBLE" >> $INVENTORY_FILE
done

echo "Inventaire mis à jour :"
cat $INVENTORY_FILE

# Nettoyer le fichier d'inventaire existant
echo "[kafka_servers]" > $INI_FILE

# Mettre à jour le fichier hosts.ini 
for ip in "${INSTANCE_IPS[@]}"; do
    echo "$ip ansible_user=davy ansible_ssh_private_key_file=clé/ANSIBLE" >> $INI_FILE
done

echo "[storm_servers]" >> $INI_FILE

for ip in "${INSTANCE_IPS[@]}"; do
    echo "$ip ansible_user=davy ansible_ssh_private_key_file=clé/ANSIBLE" >> $INI_FILE
done


echo "Mise à jour des adresses IP dans $INI_FILE terminée."

sleep 10

#deploiement de l'outil ops_agent dans les vm
if [ "$OPS" = "TRUE" ]; then
    ansible-playbook -i inventory.ini install_ops_agent.yml
fi
#deploiement de apache kafka et de zookeeper dans les vm
if [ "$KAFKA" = "TRUE" ]; then
    ansible-playbook -i hosts.ini  kafka.yml
fi

#deploiement de apache storm et de zookeeper dans les vm
if [ "$STORM" = "TRUE" ]; then
    ansible-playbook -i hosts.ini  storm.yml
fi
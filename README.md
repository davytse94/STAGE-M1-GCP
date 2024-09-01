# STAGE-M1-GCP
L'objectif du stage est de créer et d'automatiser le déploiement d'un écosystème distribué où nous pouvons exécuter un processus ETL (Extract-Transform-Load) complet et une application de traitement de données en flux en utilisant plusieurs machines avec des res- sources hétérogènes

Rajouter un dossier templates et déplacer les 4 fichier .j2 dans le dossier templates.

Pré-requis 
Pour démarrer le projet, il est nécessaire d’installer Ansible , d’avoir python, de pouvoir exécuter des scripts shell et de disposer d’un compte google.

Pour accéder à votre compte Google Cloud Platform à partir d’un terminal, utilisez la commande suivant : 
gcloud auth login

Script d’automatisation  

Création de deux scripts automatisés avec des paramètres par défaut, qui sont modifiable en ajoutant les options défini  : 
automatisation.sh
automatisation1.sh

Le script “automatisation.sh” offre une solution complète pour intégrer et gérer les services Google Cloud, notamment : 
Ajoutez le service Compute Engine.
Créer un modèle d’instance pour standardiser le déploiement.
Provisionner des machines virtuelles à partir de ce modèle d’instance.
Générer une paire de clés publique/privée pour permettre une connexion sécurisée depuis votre machine locale, équipée d’Ansible, vers votre projet sur Google Cloud Platform.

Relever les adresses IP externes des machines virtuelles pour créer les fichiers d’inventaire d’ansible (“inventory.ini” et “hosts.ini”).
Lance les commandes pour exécuter les playbook Ansible.
Et le script “automatisation1.sh” permet de : 
Ajouter des services comme le Monitoring, le Logging et Pub/Sub.
Installer les différents modules Python requis.
Créer un compte de service.
Attribuer les différents rôles nécessaires au compte de service pour accéder aux métriques demandées.
Ajouter une clé au compte de service.
Lancer les scripts Python pour la collecte des métriques.

Publish/Subscribe
Pour commencer à utiliser l’outil Pub/Sub de Google Cloud Platform : 
Autorisation de l’outil Pub/Sub via la console.
Création d’un Topic et d’un Subscriber (lancer le script automatisationpubsub.sh).
Ajouter le module pip install google-cloud-pubsub.
Envoyer des messages au Topic (lancer le script pubsub.sh) celui-ci utilise le fichier de données envoyé par Bianca (data.csv).
Réception des messages du Topic à l’aide du Subscriber (lancer le script subcriber.sh).

Apache Kafka dans une VM
Transfert de fichier depuis la machine local à la VM de GCP.

gcloud compute scp data.csv user@<nom de l’instance>::~/

gcloud compute scp consumer.py user@<nom de l’instance>::~/

gcloud compute scp producer.py user@<nom de l’instance>::~/

Se connecter en ssh à la VM de GCP. 
gcloud compute ssh <NOMVM>

Création d’un topic dans la machine virtuelle : 
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic test --partitions 3 --replication-factor 1

Installation de Python3 et du module kafka pour python: 
sudo apt install python3-pip
pip install kafka-python confluent_kafka pandas

Lancement du producer puis du consumer : 
python3 producer.py
python3 consumer.py

from google.cloud import billing_v1
from google.auth import default
import csv
import datetime

# Récupérer les informations d'authentification par défaut
credentials, project_id = default()

# Créer un client pour l'API Billing Catalog
client = billing_v1.CloudCatalogClient(credentials=credentials)

# Récupérer la liste des services disponibles
services = client.list_services()

# Ouvrir le fichier CSV pour écrire les résultats
with open('test_metrics_billing.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Écrire les en-têtes du fichier CSV
    writer.writerow(['Service Name', 'Service ID', 'SKU ID', 'SKU Description', 'Pricing Info'])
    
    for service in services:
        service_name = service.display_name
        service_id = service.name.split('/')[-1]
        # Récupérer les SKUs pour chaque service
        skus = client.list_skus(parent=service.name)
        
        for sku in skus:
            sku_id = sku.name.split('/')[-1]
            sku_description = sku.description
            pricing_info = sku.pricing_info
            # Extraire les informations de tarification
            price_details = []
            for price in pricing_info:
                price_type = price.pricing_expression.usage_unit_description
                unit_price = "N/A"
                
                # Vérifier si tiered_rates existe et n'est pas vide
                if price.pricing_expression.tiered_rates:
                    try:
                        unit_price = price.pricing_expression.tiered_rates[0].unit_price.nanos / 1e9
                    except (IndexError, AttributeError):
                        # Si l'accès échoue, on garde "N/A"
                        pass
                
                price_details.append(f"{price_type}: {unit_price} USD")
            
            # Si aucun détail de prix n'est disponible, ajouter une information par défaut
            if not price_details:
                price_details = ["Pricing information not available"]
            
            # Écrire les informations dans le fichier CSV
            writer.writerow([service_name, service_id, sku_id, sku_description, "; ".join(price_details)])

print("Les informations de tarification ont été écrites dans le fichier CSV.")
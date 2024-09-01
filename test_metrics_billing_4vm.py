import google.auth
from google.cloud import billing_v1
from google.api_core import retry
from google.api_core import exceptions

# Utiliser les identifiants par défaut
credentials, project_id = google.auth.default()

# Initialisation du client pour accéder au catalogue de prix
billing_client = billing_v1.CloudCatalogClient(credentials=credentials)

# Définir les paramètres pour les VMs
zone = "europe-west1"
machine_type = "n1-standard-2"
num_vms = 4

# Fonction pour obtenir le prix de l'instance avec retry
@retry.Retry(predicate=retry.if_exception_type(
    exceptions.ServiceUnavailable,
    exceptions.InternalServerError,
    exceptions.GatewayTimeout
))
def get_vm_price(machine_type, region):
    cpu_price = 0
    ram_price = 0
    
    try:
        response = billing_client.list_skus(parent="services/6F81-5844-456A")
        
        print(f"Recherche du prix pour le type de machine : {machine_type}")
        
        for sku in response:
            if sku.category.resource_family == "Compute":
                if sku.category.resource_group == "CPU" and machine_type.split('-')[0] in sku.description.lower():
                    for pricing_info in sku.pricing_info:
                        for price in pricing_info.pricing_expression.tiered_rates:
                            if price.unit_price.currency_code == "USD":
                                cpu_price = price.unit_price.units + price.unit_price.nanos / 1e9
                                print(f"Prix CPU trouvé : {cpu_price} USD/heure")
                
                elif sku.category.resource_group == "RAM":
                    for pricing_info in sku.pricing_info:
                        for price in pricing_info.pricing_expression.tiered_rates:
                            if price.unit_price.currency_code == "USD":
                                ram_price = price.unit_price.units + price.unit_price.nanos / 1e9
                                print(f"Prix RAM trouvé : {ram_price} USD/heure")
        
        total_price = cpu_price + ram_price
        if total_price > 0:
            print(f"Prix total trouvé : {total_price} USD/heure")
            return total_price
        else:
            print("Aucun prix correspondant n'a été trouvé.")
            return None
    
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des prix : {e}")
        raise

# Obtenir le prix par heure pour l'instance spécifiée
try:
    price_per_hour = get_vm_price(machine_type, zone)

    if price_per_hour:
        # Calculer le coût mensuel pour 4 VMs (supposant 24 heures par mois)
        cost_per_month_per_vm = price_per_hour * 24
        total_cost_per_month = cost_per_month_per_vm * num_vms

        print(f"Estimation mensuelle pour {num_vms} VMs de type {machine_type} en zone {zone} avec Ubuntu: ${total_cost_per_month:.2f}")
    else:
        print("Impossible d'obtenir les prix des VMs.")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
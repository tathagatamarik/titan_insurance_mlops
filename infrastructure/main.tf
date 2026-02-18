terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}

# 1. Resource Group (LOCATION: PUNE, INDIA)
resource "azurerm_resource_group" "titan_rg" {
  name     = "TitanInsuranceRG"
  location = "centralindia"   # <--- Approved!
}

# 2. Azure Container Registry
resource "random_id" "acr_suffix" {
  byte_length = 4
}

resource "azurerm_container_registry" "titan_acr" {
  name                = "titanregistry${random_id.acr_suffix.hex}"
  resource_group_name = azurerm_resource_group.titan_rg.name
  location            = azurerm_resource_group.titan_rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# 3. Azure Kubernetes Service
resource "azurerm_kubernetes_cluster" "titan_aks" {
  name                = "TitanCluster"
  location            = azurerm_resource_group.titan_rg.location
  resource_group_name = azurerm_resource_group.titan_rg.name
  dns_prefix          = "titanaks"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }
}

# 4. Link AKS to ACR
resource "azurerm_role_assignment" "aks_pull_acr" {
  principal_id                     = azurerm_kubernetes_cluster.titan_aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.titan_acr.id
  skip_service_principal_aad_check = true
}

# 5. Outputs
output "acr_login_server" {
  value = azurerm_container_registry.titan_acr.login_server
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.titan_aks.name
}

output "resource_group" {
  value = azurerm_resource_group.titan_rg.name
}
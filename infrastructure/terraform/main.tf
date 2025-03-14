terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.0"
    }
  }

  backend "s3" {
    bucket         = "advanced-cicd-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

# AWS Provider
provider "aws" {
  region = var.aws_region
}

# Azure Provider
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
}

# Google Cloud Provider
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Kubernetes Provider
provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Helm Provider
provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

# Vault Provider
provider "vault" {
  address = var.vault_address
  token   = var.vault_token
}

# AWS EKS Cluster
module "aws_eks" {
  source = "./modules/aws/eks"
  
  cluster_name    = "advanced-cicd-${var.environment}"
  cluster_version = "1.24"
  vpc_cidr        = "10.0.0.0/16"
  
  node_groups = {
    general = {
      desired_size = 2
      min_size     = 1
      max_size     = 5
      instance_types = ["t3.medium"]
    }
  }
}

# Azure AKS Cluster
module "azure_aks" {
  source = "./modules/azure/aks"
  
  resource_group_name = "advanced-cicd-${var.environment}"
  cluster_name       = "advanced-cicd-${var.environment}"
  node_count        = 2
  vm_size          = "Standard_D2s_v3"
}

# Google GKE Cluster
module "gcp_gke" {
  source = "./modules/gcp/gke"
  
  project_id     = var.gcp_project_id
  cluster_name   = "advanced-cicd-${var.environment}"
  region         = var.gcp_region
  node_count     = 2
  machine_type   = "e2-medium"
}

# Vault Server
module "vault" {
  source = "./modules/vault"
  
  environment = var.environment
  k8s_namespace = "vault"
  
  depends_on = [
    module.aws_eks,
    module.azure_aks,
    module.gcp_gke
  ]
}

# Monitoring Stack
module "monitoring" {
  source = "./modules/monitoring"
  
  environment = var.environment
  k8s_namespace = "monitoring"
  
  prometheus_values = {
    server = {
      retention = "15d"
      persistentVolume = {
        enabled = true
        size = "50Gi"
      }
    }
    alertmanager = {
      enabled = true
      persistentVolume = {
        enabled = true
        size = "10Gi"
      }
    }
  }
  
  grafana_values = {
    persistence = {
      enabled = true
      size = "10Gi"
    }
    adminPassword = var.grafana_admin_password
  }
  
  depends_on = [
    module.aws_eks,
    module.azure_aks,
    module.gcp_gke
  ]
}

# Service Mesh (Istio)
module "service_mesh" {
  source = "./modules/service-mesh"
  
  environment = var.environment
  k8s_namespace = "istio-system"
  
  depends_on = [
    module.aws_eks,
    module.azure_aks,
    module.gcp_gke
  ]
}

# Application Deployment
module "app_deployment" {
  source = "./modules/app"
  
  environment = var.environment
  image_tag   = var.image_tag
  
  frontend_values = {
    replicaCount = 2
    resources = {
      limits = {
        cpu = "1000m"
        memory = "1Gi"
      }
      requests = {
        cpu = "500m"
        memory = "512Mi"
      }
    }
  }
  
  backend_values = {
    replicaCount = 2
    resources = {
      limits = {
        cpu = "1000m"
        memory = "2Gi"
      }
      requests = {
        cpu = "500m"
        memory = "1Gi"
      }
    }
  }
  
  depends_on = [
    module.vault,
    module.monitoring,
    module.service_mesh
  ]
} 
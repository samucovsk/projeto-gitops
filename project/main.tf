terraform {
  required_version = ">= 1.15.3"
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = ">= 0.11.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 3.2.1"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 3.2.0"
    }
  }

  backend "local" {
    path = "../backend/terraform.tfstate"
  }
}


provider "kind" {}


provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "project-portifolio"
}

provider "helm" {
  kubernetes = {
    config_path = "~/.kube/config"
  }
}

module "k8s" {
  source       = "../modules/kind/"
  cluster_name = "project-portifolio"
}

module "helm" {
  depends_on       = [module.k8s]
  source           = "../modules/helm/"
  helm_name        = "argo-cd"
  helm_repository  = "https://argoproj.github.io/argo-helm"
  helm_chart       = "argo-cd"
  helm_version     = "10.5.0"
  create_namespace = true
  namespace        = "argocd"
}
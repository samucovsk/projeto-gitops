terraform {
  required_version = ">= 1.15.3"
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = ">= 0.11.0"
    }
  }
}

resource "kind_cluster" "default" {
    name = var.cluster_name

    kind_config { 
        kind = "Cluster"
        api_version = "kind.x-k8s.io/v1alpha4"
        node {
            role = "control-plane"
        }
        node {
            role = "worker"
        }
    }
}
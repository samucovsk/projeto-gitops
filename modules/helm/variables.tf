variable "helm_name" {
  description = "Nome do release do helm"
  type        = string
}

variable "helm_repository" {
  description = "Repositório do helm"
  type        = string
}

variable "helm_chart" {
  description = "Chart do helm"
  type        = string
}

variable "helm_version" {
    description = "Versão do chart do helm"
    type        = string
}

variable "create_namespace" {
    description = "Criar namespace do helm"
    type        = bool
}

variable "namespace" {
    description = "Namespace do helm"
    type        = string
}
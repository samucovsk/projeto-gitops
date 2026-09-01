resource "helm_release" "this" {
    name = var.helm_name
    repository = var.helm_repository
    chart = var.helm_chart
    version = var.helm_version
    create_namespace = var.create_namespace
    namespace = var.namespace
}
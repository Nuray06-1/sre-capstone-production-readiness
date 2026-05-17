output "namespace" {
  description = "Namespace where the application resources are deployed"
  value       = kubernetes_namespace_v1.sre.metadata[0].name
}

output "deployment_name" {
  description = "Name of the Kubernetes Deployment managed by Terraform"
  value       = "ecommerce-api"
}

output "service_name" {
  description = "Name of the Kubernetes Service managed by Terraform"
  value       = "ecommerce-api-service"
}

output "hpa_name" {
  description = "Name of the Kubernetes HPA managed by Terraform"
  value       = "ecommerce-api-hpa"
}

output "verification_commands" {
  description = "Useful commands to verify Terraform-managed resources"
  value       = <<EOT
kubectl get all -n ${kubernetes_namespace_v1.sre.metadata[0].name}
kubectl get hpa -n ${kubernetes_namespace_v1.sre.metadata[0].name}
EOT
}
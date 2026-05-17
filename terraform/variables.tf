variable "namespace" {
  description = "Kubernetes namespace for the SRE capstone resources"
  type        = string
  default     = "sre-project"
}

variable "kubeconfig_path" {
  description = "Path to the local Kubernetes kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}
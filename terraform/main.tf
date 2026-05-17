terraform {
  required_version = ">= 1.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = pathexpand(var.kubeconfig_path)
}

resource "kubernetes_namespace_v1" "sre" {
  metadata {
    name = var.namespace
  }
}

locals {
  deployment_yaml = yamldecode(
    file("${path.module}/../k8s/deployment.yaml")
  )

  service_yaml = yamldecode(
    file("${path.module}/../k8s/service.yaml")
  )

  hpa_yaml = yamldecode(
    file("${path.module}/../k8s/hpa.yaml")
  )

  deployment_manifest = merge(
    local.deployment_yaml,
    {
      metadata = merge(
        local.deployment_yaml.metadata,
        {
          namespace = kubernetes_namespace_v1.sre.metadata[0].name
        }
      )
    }
  )

  service_manifest = merge(
    local.service_yaml,
    {
      metadata = merge(
        local.service_yaml.metadata,
        {
          namespace = kubernetes_namespace_v1.sre.metadata[0].name
        }
      )
    }
  )

  hpa_manifest = merge(
    local.hpa_yaml,
    {
      metadata = merge(
        local.hpa_yaml.metadata,
        {
          namespace = kubernetes_namespace_v1.sre.metadata[0].name
        }
      )
    }
  )
}

resource "kubernetes_manifest" "deployment" {
  manifest = local.deployment_manifest

  depends_on = [
    kubernetes_namespace_v1.sre
  ]
}

resource "kubernetes_manifest" "service" {
  manifest = local.service_manifest

  depends_on = [
    kubernetes_namespace_v1.sre,
    kubernetes_manifest.deployment
  ]
}

resource "kubernetes_manifest" "hpa" {
  manifest = local.hpa_manifest

  depends_on = [
    kubernetes_namespace_v1.sre,
    kubernetes_manifest.deployment
  ]
}
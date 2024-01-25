terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.13.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "5.13.0"
    }
  }
}

variable "project" {
  type    = string
  default = "taprx-9c82f"
}
variable "region" {
  type    = string
  default = "us-central1"
}
variable "zone" {
  type    = string
  default = "us-central1-c"
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}
provider "google-beta" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_storage_bucket" "bucket" {
  name                        = "${var.project}-gcf-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "hello_world_gcf_object" {
  name   = "hello_world_function"
  bucket = google_storage_bucket.bucket.name
  source = "../functions/hello_world_function/hello_world_function-source.zip"
}

resource "google_cloudfunctions2_function" "hello_world_function" {
  name        = "hello_world_function"
  location    = var.region
  description = "Example function"

  build_config {
    runtime     = "python311"
    entry_point = "hello_get"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.hello_world_gcf_object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_api_gateway_api" "api" {
  provider     = google-beta
  api_id       = "tap-rx-api"
  display_name = "tap-rx-api"
}

resource "google_api_gateway_api_config" "api_config" {
  provider     = google-beta
  api          = google_api_gateway_api.api.api_id
  display_name = "tap-rx-api-config"
  openapi_documents {
    document {
      path     = "openapi.yaml"
      contents = filebase64("openapi.yaml")
    }
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "google_api_gateway_gateway" "api_gw" {
  provider     = google-beta
  api_config   = google_api_gateway_api_config.api_config.id
  gateway_id   = "tap-rx-api-gateway"
  display_name = "tap-rx-api-gateway"
}
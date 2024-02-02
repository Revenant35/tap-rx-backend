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
variable "firebase_database_url" {
  type    = string
  default = "https://taprx-9c82f-default-rtdb.firebaseio.com"
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

resource "google_kms_key_ring" "terraform_state" {
  name     = "${random_id.bucket_prefix.hex}-bucket-tfstate"
  location = "us"
}

resource "google_kms_crypto_key" "terraform_state_bucket" {
  name            = "test-terraform-state-bucket"
  key_ring        = google_kms_key_ring.terraform_state.id
  rotation_period = "86400s"

  lifecycle {
    prevent_destroy = false
  }
}

data "google_project" "project" {
}

resource "google_project_iam_member" "default" {
  project = data.google_project.project.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member  = "serviceAccount:service-1061539834893@gs-project-accounts.iam.gserviceaccount.com"
}

resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "default" {
  name          = "${random_id.bucket_prefix.hex}-bucket-tfstate"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
  encryption {
    default_kms_key_name = google_kms_crypto_key.terraform_state_bucket.id
  }
  depends_on = [
    google_project_iam_member.default
  ]
}

resource "google_storage_bucket" "bucket" {
  name                        = "${var.project}-gcf-source"
  location                    = "US"
  uniform_bucket_level_access = true
}
terraform {
  backend "gcs" {
    bucket = "56e8ac26bd50a172-bucket-tfstate"
    prefix = "terraform/state"
  }
}
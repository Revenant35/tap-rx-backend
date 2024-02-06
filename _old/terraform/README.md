# Terraform Overview
- GCP provider for Terraform: https://registry.terraform.io/providers/hashicorp/google/latest/docs
 
## Using a Cloud Storage Bucket to Keep Track of State
 - https://cloud.google.com/docs/terraform/resource-management/store-state
 - Stores state file in a centralized location, to avoid conflict from local work.

## How to Get Started With Terraform
- Installing GCloud CLI: https://cloud.google.com/sdk/docs/install-sdk
- Authorizing with GCloud CLI: https://cloud.google.com/sdk/docs/authorizing
- Installing Terraform: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

## How to Deploy a New Function
- Zip the source code together with the `requirements.txt` file.
- Change the `openapi.yaml` config to include the path for the new function.
- Destroy the api using `terraform destroy --target google_api_gateway_api{API_NAME}`.
- Create a new Google Cloud Storage Object that will be put in the source code bucket. Follow previous objects in `functions.tf` for example.
- Create a new Google Cloud Function with the source being your new object. Follow previous functions in `functions.tf` for examples.
- Format and validate your changes using `terraform fmt` and `terraform validate`.
- Apply and deploy your changes using `terraform apply`.
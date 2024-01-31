# TapRx API

This repository contains the infrastructure and deployment configuration for the Backend API of TapRx, hosted on Google Cloud Platform (GCP). It leverages Terraform for infrastructure as code (IaC) to ensure a reproducible and scalable environment.

## CI/CD Status

[![CI/CD Workflow](https://github.com/Revenant35/tap-rx-backend/actions/workflows/ci_cd.yml/badge.svg?branch=main&event=push)](https://github.com/Revenant35/tap-rx-backend/actions/workflows/ci_cd.yml)

## Project Overview

The Backend API is designed to provide authenticated data storage and data sharing for app users to log their medications. It is developed with Flask in Python and is deployed to GCP using Cloud Functions.

## Infrastructure

The infrastructure is managed using Terraform, which allows us to define resources declaratively. This setup includes:

- Google Cloud Functions/Cloud Run services
- Cloud SQL instances
- VPC networks and subnets
- IAM roles and permissions

## Getting Started

### Prerequisites

- Google Cloud SDK
- Terraform
- Access to GCP (with necessary permissions)

### Setup

1. **Clone the repository**:
```
git clone https://github.com/Revenant35/tap-rx-backend.git
```

2. **Configure GCP authentication**:

Set up your GCP credentials by downloading the service account key file and setting the environment variable:
```
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account-file.json"
```

3. **Initialize Terraform**:

Navigate to the `terraform` directory and run:
```
terraform init
```

4. **Apply Terraform configuration**:

To create the infrastructure, run:

```
terraform apply
```

### Deployment

Deployments are managed through GitHub Actions CI/CD workflows, which automatically deploy changes to the Cloud Functions/Cloud Run services whenever changes are pushed to the `main` branch.

## License

This project is licensed under the [Apache License v2.0](LICENSE) - see the LICENSE file for details.

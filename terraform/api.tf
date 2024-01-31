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
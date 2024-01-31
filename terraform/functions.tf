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

resource "google_storage_bucket_object" "register_user_gcf_object" {
  name   = "register_user_function"
  bucket = google_storage_bucket.bucket.name
  source = "../functions/register_user_function/register_user_function-source.zip"
}

resource "google_cloudfunctions2_function" "register_user_function" {
  name        = "register_user_function"
  location    = var.region
  description = "Registers a user for TapRx"

  build_config {
    runtime     = "python311"
    entry_point = "register_user_handler"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.register_user_gcf_object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}
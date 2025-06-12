provider "google" {
  project = "your-gcp-project-id"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_compute_instance" "gpu_vm" {
  name         = "ubuntu-anaconda-gpu"
  machine_type = "n1-standard-4"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts"
      size  = 100
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    install-nvidia-driver = "True"
    startup-script        = file("gce-startup-anaconda-gpu.sh")
  }

  guest_accelerator {
    type  = "nvidia-tesla-t4"
    count = 1
  }

  scheduling {
    on_host_maintenance = "TERMINATE"
  }

  tags = ["http-server"]
}

resource "google_storage_bucket_object" "llm_env" {
  name   = "llm_110623.yml"
  bucket = "your-gcs-bucket"
  source = "llm_110623.yml"
}

resource "google_storage_bucket_object" "etl_env" {
  name   = "web_scrape_etl.yml"
  bucket = "your-gcs-bucket"
  source = "web_scrape_etl.yml"
}

module "VPC_Build" {
  source      = "../modules/orgscp"
  name        = "VPC_Build"
  description = "Reusable vpc code."
  targets     = var.targets
  content     = file("${path.module}/policies/cloudue_imagebuild_and_share_limits.json")
}
# This deploys a Data Portal stack.
# 

data aws_secretsmanager_secret_version config {
  secret_id = var.happy_config_secret
}

locals {
  secret = jsondecode(data.aws_secretsmanager_secret_version.config.secret_string)

  source                = "../master"
  custom_stack_name     = var.stack_name
  image_tag             = var.image_tag
  priority              = var.priority
  deployment_stage      = var.deployment_stage

  migration_cmd         = "make,-C,/corpora-data-portal/backend,db/init_remote_dev"
  deletion_cmd          = "make,-C,/corpora-data-portal/backend,db/delete_remote_dev"
  frontend_cmd          = ""
  backend_cmd           = "python3,/chalice/run_local_server.py,--host,0.0.0.0"
  data_load_path        = "s3://${local.secret["env_s3_bucket"]}/database/dev_data.sql"

  vpc_id                = local.secret["vpc_id"]
  subnets               = var.require_okta ? local.secret["private_subnets"] : local.secret["public_subnets"]
  security_groups       = local.secret["security_groups"]
  zone                  = local.secret["zone_id"]
  cluster               = local.secret["cluster_arn"]
  frontend_image_repo   = local.secret["ecrs"]["frontend"]
  backend_image_repo    = local.secret["ecrs"]["backend"]
  upload_image_repo     = local.secret["ecrs"]["processing"]
  lambda_upload_repo    = local.secret["ecrs"]["upload_failures"]
  batch_role_arn        = local.secret["batch_queues"]["upload"]["role_arn"]
  job_queue_arn         = local.secret["batch_queues"]["upload"]["queue_arn"]
  external_dns          = local.secret["external_zone_name"]

  frontend_listener_arn = try(local.secret["alb_listeners"]["frontend"]["arn"], "")
  backend_listener_arn  = try(local.secret["alb_listeners"]["backend"]["arn"], "")
  frontend_alb_zone     = try(local.secret["albs"]["frontend"]["zone_id"], "")
  backend_alb_zone      = try(local.secret["albs"]["backend"]["zone_id"], "")
  frontend_alb_dns      = try(local.secret["albs"]["frontend"]["dns_name"], "")
  backend_alb_dns       = try(local.secret["albs"]["backend"]["dns_name"], "")

  artifact_bucket       = try(local.secret["s3_buckets"]["artifacts"]["name"], "")
  cellxgene_bucket      = try(local.secret["s3_buckets"]["cellxgene"]["name"], "")

  task_role_arn         = local.secret["task_role_arn"]
  sfn_role_arn          = local.secret["sfn_role_arn"]
  lambda_execution_role = local.secret["lambda_execution_role"]
}

module frontend_dns {
  count                 = var.require_okta ? 1 : 0
  source                = "../dns"
  custom_stack_name     = local.custom_stack_name
  app_name              = "frontend"
  alb_dns               = var.frontend_alb_dns
  canonical_hosted_zone = var.frontend_alb_zone
  zone                  = var.zone
}

module backend_dns {
  count                 = var.require_okta ? 1 : 0
  source                = "../dns"
  custom_stack_name     = local.custom_stack_name
  app_name              = "backend"
  alb_dns               = var.backend_alb_dns
  canonical_hosted_zone = var.backend_alb_zone
  zone                  = var.zone
}

module frontend_service {
  source            = "../service"
  custom_stack_name = local.custom_stack_name
  app_name          = "frontend"
  vpc               = local.vpc_id
  image             = "${local.frontend_image_repo}:${local.image_tag}"
  cluster           = local.cluster
  desired_count     = 2
  listener          = local.frontend_listener_arn
  subnets           = local.subnets
  security_groups   = local.security_groups
  task_role_arn     = local.task_role_arn
  service_port      = 9000
  deployment_stage  = local.deployment_stage
  step_function_arn = module.upload_sfn.step_function_arn
  host_match        = join(".", [module.frontend_dns.dns_prefix, local.external_dns])
  priority          = local.priority
  api_url           = join("", ["https://", module.backend_dns.dns_prefix, ".", local.external_dns])
  frontend_url      = join("", ["https://", module.frontend_dns.dns_prefix, ".", local.external_dns])
}

module backend_service {
  source            = "../service"
  custom_stack_name = local.custom_stack_name
  app_name          = "backend"
  vpc               = local.vpc_id
  image             = "${local.backend_image_repo}:${local.image_tag}"
  cluster           = local.cluster
  desired_count     = 2
  listener          = local.backend_listener_arn
  subnets           = local.subnets
  security_groups   = local.security_groups
  task_role_arn     = local.task_role_arn
  service_port      = 5000
  cmd               = local.backend_cmd
  deployment_stage  = local.deployment_stage
  step_function_arn = module.upload_sfn.step_function_arn
  host_match        = join(".", [module.backend_dns.dns_prefix, local.external_dns])
  priority          = local.priority
  api_url           = join("", ["https://", module.backend_dns.dns_prefix, ".", local.external_dns])
  frontend_url      = join("", ["https://", module.frontend_dns.dns_prefix, ".", local.external_dns])
}

module migrate_db {
  source            = "../migration"
  image             = "${local.backend_image_repo}:${local.image_tag}"
  task_role_arn     = local.task_role_arn
  cmd               = local.migration_cmd
  custom_stack_name = local.custom_stack_name
  deployment_stage  = local.deployment_stage
  data_load_path    = local.data_load_path
}

module delete_db {
  count             = var.delete_protected ? 0 : 1
  source            = "../deletion"
  image             = "${local.backend_image_repo}:${local.image_tag}"
  task_role_arn     = local.task_role_arn
  cmd               = local.deletion_cmd
  custom_stack_name = local.custom_stack_name
  deployment_stage  = local.deployment_stage
}

module upload_batch {
  source            = "../batch"
  image             = "${local.upload_image_repo}:${local.image_tag}"
  batch_role_arn    = local.batch_role_arn
  cmd               = ""
  custom_stack_name = local.custom_stack_name
  deployment_stage  = local.deployment_stage
  artifact_bucket   = local.artifact_bucket
  cellxgene_bucket  = local.cellxgene_bucket
  frontend_url      = join("", ["https://", module.frontend_dns.dns_prefix, ".", local.external_dns])
}

module upload_lambda {
  source                = "../lambda"
  image                 = "${local.lambda_upload_repo}:${local.image_tag}"
  custom_stack_name     = local.custom_stack_name
  deployment_stage      = local.deployment_stage
  artifact_bucket       = local.artifact_bucket
  cellxgene_bucket      = local.cellxgene_bucket
  lambda_execution_role = local.lambda_execution_role
}

module upload_sfn {
  source               = "../sfn"
  job_definition_arn   = module.upload_batch.batch_job_definition
  job_queue_arn        = local.job_queue_arn
  role_arn             = local.sfn_role_arn
  custom_stack_name    = local.custom_stack_name
  lambda_error_handler = module.upload_lambda.error_handler
}

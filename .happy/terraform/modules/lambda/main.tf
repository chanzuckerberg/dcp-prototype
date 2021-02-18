# This is a lambda job
# 
resource aws_lambda_function lambda_job_def {
  role          = var.lambda_execution_role
  function_name = "dp-${var.deployment_stage}-${var.custom_stack_name}-lambda"
  package_type  = "Image"
  image_uri     = var.image
  environment {
    variables = {
      ARTIFACT_BUCKET = var.artifact_bucket,
      CELLXGENE_BUCKET = var.cellxgene_bucket,
      DEPLOYMENT_STAGE = var.deployment_stage,
      REMOTE_DEV_PREFIX = var.remote_dev_prefix
    }
  }
}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/dp/${var.deployment_stage}/${var.custom_stack_name}/lambda-handler-error"
}

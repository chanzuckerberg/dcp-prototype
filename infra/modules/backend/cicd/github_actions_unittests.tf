
resource "aws_secretsmanager_secret" "auth0" {
  name = "backend/corpora/test/auth0-secret"
  tags = {
    project   = var.project
    env       = var.env
    service   = var.service
    owner     = var.owner
    managedBy = "terraform"
  }
}


data "aws_iam_policy_document" "policy" {
  statement {
    sid    = "ReadAuth0TestSecret"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]

    resources = [
      aws_secretsmanager_secret.auth0.arn,
    ]
  }
  statement {
    sid     = "ChaliceDeployedAPIGateway"
    effect  = "Allow"
    actions = ["apigateway:*"]
    resources = [
      "arn:aws:apigateway:us-west-2::/restapis/${var.api_gateway_dev}",
      "arn:aws:apigateway:us-west-2::/restapis/${var.api_gateway_staging}",
      "arn:aws:apigateway:us-west-2::/restapis/${var.api_gateway_dev}/*",
      "arn:aws:apigateway:us-west-2::/restapis/${var.api_gateway_staging}/*"
    ]
  }
  statement {
    sid       = "ChaliceAPIGateway"
    effect    = "Allow"
    actions   = ["apigateway:POST"]
    resources = ["arn:aws:apigateway:us-west-2::/restapis"]

  }
  statement {
    sid    = "ChaliceLambdas"
    effect = "Allow"
    actions = [
      "lambda:CreateFunction",
      "lambda:TagResource",
      "lambda:DeleteProvisionedConcurrencyConfig",
      "lambda:GetFunctionConfiguration",
      "lambda:UntagResource",
      "lambda:PutFunctionConcurrency",
      "lambda:GetProvisionedConcurrencyConfig",
      "lambda:ListTags",
      "lambda:PutFunctionEventInvokeConfig",
      "lambda:DeleteFunctionEventInvokeConfig",
      "lambda:DeleteFunction",
      "lambda:UpdateFunctionEventInvokeConfig",
      "lambda:GetFunction",
      "lambda:UpdateFunctionConfiguration",
      "lambda:AddPermission",
      "lambda:GetFunctionConcurrency",
      "lambda:GetFunctionEventInvokeConfig",
      "lambda:PutProvisionedConcurrencyConfig",
      "lambda:UpdateFunctionCode",
      "lambda:DeleteFunctionConcurrency",
      "lambda:PublishVersion",
      "lambda:RemovePermission",
      "lambda:GetPolicy"
    ]
    resources = [
      "arn:aws:lambda:us-west-2:${var.account_id}:function:corpora-api-dev",
      "arn:aws:lambda:us-west-2:${var.account_id}:function:corpora-api-staging"
    ]
  }
  statement {
    sid    = "ChaliceIAM"
    effect = "Allow"
    actions = [
      "iam:UntagRole",
      "iam:TagRole",
      "iam:CreateRole",
      "iam:AttachRolePolicy",
      "iam:PutRolePolicy",
      "iam:PassRole",
      "iam:DeleteRolePolicy",
      "iam:GetRole",
      "iam:UpdateRoleDescription",
      "iam:DeleteRole",
      "iam:UpdateRole",
      "iam:GetRolePolicy",
    ]
    resources = [
      "arn:aws:iam::${var.account_id}:role/corpora-api-dev-api_handler",
      "arn:aws:iam::${var.account_id}:role/corpora-api-staging-api_handler",
    ]
  }
  statement {
    sid    = "ChaliceS3"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::org-dcp-infra-${var.account_id}/chalice/*"
    ]
  }
  statement {
    sid    = "GatsbyS3"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::dcp-static-site-${var.deployment_stage}-${var.account_id}/*",
      "arn:aws:s3:::dcp-static-site-${var.deployment_stage}-${var.account_id}"
    ]
  }
}

resource "aws_iam_policy" "github_actions" {
  name        = "github_actions"
  path        = "/"
  policy      = data.aws_iam_policy_document.policy.json
  description = "Provides github actions access to aws for running tests."
}

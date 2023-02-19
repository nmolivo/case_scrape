data "aws_vpc" "main" {
  id = local.vpc["id"]  # vpc-xx1x1x1x
}
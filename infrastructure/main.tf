terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  shared_credentials_files = ["C:/Users/Quan/.aws/credentials"]
}


module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "eks-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  map_public_ip_on_launch = true

  tags = {
    Name = "eks-vpc"
  }
}

module "eks" {
  source = "./modules/eks"
  depends_on = [ module.vpc ]

  cluster_name = "${var.name_prefix}-eks-cluster"
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets
  iam_role_arn = var.iam_role_arn
}
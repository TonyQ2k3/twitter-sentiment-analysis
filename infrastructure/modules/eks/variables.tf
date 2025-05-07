variable "iam_role_arn" {
  description = "IAM role ARN for the EKS cluster"
  type        = string
  default     = "arn:aws:iam::381492172464:role/LabRole"
}


variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "uat-environment"
}

variable "node_group_name" {
  description = "Name of the Ndoe group"
  type        = string
  default     = "uat-nodes"
}

variable "vpc_id" {
  description = "VPC ID for the EKS cluster"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the EKS cluster"
  type        = list(string)
}


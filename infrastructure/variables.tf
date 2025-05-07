variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default = "10.0.0.0/16"
}

variable "name_prefix" {
  description = "Prefix for naming resources"
  type        = string
  default     = "devops"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "availability_zone" {
  description = "AZ for the subnets"
  type        = string
  default = "us-east-1a"
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance."
  type        = string
  default = "ami-084568db4383264d4"
}

variable "instance_type" {
  description = "The type of instance to create."
  type        = string
  default = "t2.micro"
}

variable "key_name" {
  description = "The name of the key pair to use for SSH access."
  type        = string
  default     = "linux-kp"
}

variable "iam_role_arn" {
  description = "IAM role ARN for the EKS cluster"
  type        = string
  default     = "arn:aws:iam::381492172464:role/LabRole"
}
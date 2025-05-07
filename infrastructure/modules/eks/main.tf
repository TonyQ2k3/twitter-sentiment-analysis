locals {
  cluster_name    = var.cluster_name
  node_group_name = var.node_group_name
  vpc_id          = var.vpc_id
  subnet_ids      = var.subnet_ids
  iam_role_arn    = var.iam_role_arn
}

# EKS Cluster provisioning
resource "aws_eks_cluster" "cluster" {
  name     = local.cluster_name
  role_arn = local.iam_role_arn

  vpc_config {
    subnet_ids = local.subnet_ids
  }

  version = "1.32"
}

# EKS Node Group
resource "aws_eks_node_group" "node_group" {
  cluster_name    = local.cluster_name
  node_group_name = local.node_group_name
  node_role_arn   = local.iam_role_arn
  subnet_ids      = local.subnet_ids

  scaling_config {
    desired_size = 3
    max_size     = 4
    min_size     = 3
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [aws_eks_cluster.cluster]
}


# EKS Add-ons
resource "aws_eks_addon" "coredns" {
  cluster_name  = local.cluster_name
  addon_name    = "coredns"
  addon_version = "v1.11.4-eksbuild.2"
  depends_on    = [aws_eks_cluster.cluster, aws_eks_node_group.node_group]
}

resource "aws_eks_addon" "kube-proxy" {
  cluster_name  = local.cluster_name
  addon_name    = "kube-proxy"
  addon_version = "v1.32.0-eksbuild.2"
  depends_on    = [aws_eks_cluster.cluster]
}

resource "aws_eks_addon" "vpc-cni" {
  cluster_name  = local.cluster_name
  addon_name    = "vpc-cni"
  addon_version = "v1.19.2-eksbuild.1"
  depends_on    = [aws_eks_cluster.cluster]
}

resource "aws_eks_addon" "eks-pod-identity-agent" {
  cluster_name  = local.cluster_name
  addon_name    = "eks-pod-identity-agent"
  addon_version = "v1.3.4-eksbuild.1"
  depends_on    = [aws_eks_cluster.cluster]
}
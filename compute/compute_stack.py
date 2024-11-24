from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
from .components.ecs_cluster import ECSCluster
from .components.task_definition import TaskDefinition
from .components.load_balancer import LoadBalancer
from .components.ecs_service import ECSService

class ComputeStack(ComponentResource):
    def __init__(self, name: str, vpc_id: str, private_subnet_ids: list, 
                 public_subnet_ids: list, security_groups, iam_roles, 
                 certificate_arn: str, tags: dict = None, opts: ResourceOptions = None):
        super().__init__("custom:compute:ComputeStack", name, None, opts)

        # Create CloudWatch Log Group for ECS
        self.log_group = aws.cloudwatch.LogGroup(f"{name}-ecs-logs",
            retention_in_days=30,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create ECS Cluster with proper parenting
        self.cluster = ECSCluster(f"{name}",
            log_group_name=self.log_group.name,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create Load Balancer with proper parenting
        self.load_balancer = LoadBalancer(f"{name}",
            vpc_id=vpc_id,
            public_subnet_ids=public_subnet_ids,
            security_group_id=security_groups.alb_sg_id,
            certificate_arn=certificate_arn,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create Task Definition with proper parenting
        self.task_definition = TaskDefinition(f"{name}",
            execution_role_arn=iam_roles.task_execution_role_arn,
            task_role_arn=iam_roles.task_role_arn,
            log_group_name=self.log_group.name,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create ECS Service with proper parenting
        self.service = ECSService(f"{name}",
            cluster_arn=self.cluster.cluster_arn,
            task_definition_arn=self.task_definition.task_definition_arn,
            target_group_arn=self.load_balancer.target_group_arn,
            subnet_ids=private_subnet_ids,
            security_groups=security_groups.ecs_tasks_sg_id,
            tags=tags,
            opts=ResourceOptions(
                parent=self,
                depends_on=[self.load_balancer, self.task_definition]
            )
        )

        # Register outputs
        self.cluster_name = self.cluster.cluster_name
        self.cluster_arn = self.cluster.cluster_arn
        self.alb_dns_name = self.load_balancer.alb_dns_name

        self.register_outputs({
            "cluster_name": self.cluster_name,
            "cluster_arn": self.cluster_arn,
            "alb_dns_name": self.alb_dns_name
        })
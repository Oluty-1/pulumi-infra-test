from pulumi import ComponentResource, ResourceOptions
from .iam import IAMRoles
from .secrets import SecretsManager
from .security_groups import SecurityGroups

class SecurityStack(ComponentResource):
    def __init__(self, name, vpc_id, tags=None, opts=None):
        super().__init__("custom:security:SecurityStack", name, None, opts)

        # Create Security Groups
        self.security_groups = SecurityGroups(f"{name}",
            vpc_id=vpc_id,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create Secrets Manager Configuration first
        self.secrets = SecretsManager(f"{name}",
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create IAM Roles after secrets so we can pass the ARNs
        self.iam_roles = IAMRoles(f"{name}",
            tags=tags,
            opts=ResourceOptions(parent=self, depends_on=[self.secrets])
        )

        # Export important values
        self.alb_sg_id = self.security_groups.alb_sg_id
        self.ecs_tasks_sg_id = self.security_groups.ecs_tasks_sg_id
        self.rds_sg_id = self.security_groups.rds_sg_id
        self.vpc_endpoints_sg_id = self.security_groups.vpc_endpoints_sg_id
        self.task_execution_role_arn = self.iam_roles.task_execution_role_arn
        self.task_role_arn = self.iam_roles.task_role_arn
        self.app_secret_arn = self.secrets.app_secret_arn  # Export the app secret ARN

        self.register_outputs({
            "alb_sg_id": self.alb_sg_id,
            "ecs_tasks_sg_id": self.ecs_tasks_sg_id,
            "rds_sg_id": self.rds_sg_id,
            "vpc_endpoints_sg_id": self.vpc_endpoints_sg_id,
            "task_execution_role_arn": self.task_execution_role_arn,
            "task_role_arn": self.task_role_arn,
            "app_secret_arn": self.app_secret_arn  # Add to outputs
        })
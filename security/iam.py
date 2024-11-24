from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
import json

class IAMRoles(ComponentResource):
    def __init__(self, name, tags=None, opts=None):
        super().__init__("custom:security:IAMRoles", name, None, opts)

        # ECS Task Execution Role
        self.task_execution_role = aws.iam.Role(f"{name}-task-execution-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    }
                }]
            }),
            tags=tags or {},
            opts=ResourceOptions(parent=self)
        )

        # Attach AWS managed policy for ECS task execution
        aws.iam.RolePolicyAttachment(f"{name}-task-execution-policy",
            role=self.task_execution_role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            opts=ResourceOptions(parent=self.task_execution_role)
        )

        # Add secrets access policy to task execution role
        aws.iam.RolePolicy(f"{name}-task-execution-secrets-policy",
            role=self.task_execution_role.id,
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "secretsmanager:GetSecretValue",
                            "kms:Decrypt"
                        ],
                        "Resource": "*"  # You can make this more specific if needed
                    }
                ]
            }),
            opts=ResourceOptions(parent=self.task_execution_role)
        )

        # ECS Task Role
        self.task_role = aws.iam.Role(f"{name}-task-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    }
                }]
            }),
            tags=tags or {},
            opts=ResourceOptions(parent=self)
        )

        # Enhanced custom policy for the task role - added RDS IAM auth
        self.task_role_policy = aws.iam.RolePolicy(f"{name}-task-role-policy",
            role=self.task_role.id,
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "secretsmanager:GetSecretValue",
                            "kms:Decrypt"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "rds-db:connect"
                        ],
                        "Resource": [
                            # This format allows connection to any database user in your RDS instance
                            # Format: arn:aws:rds-db:region:account-id:dbuser:db-resource-id/*
                            # You can make this more specific by specifying exact database users
                            "arn:aws:rds-db:*:*:dbuser:*/*"
                        ]
                    }
                ]
            }),
            opts=ResourceOptions(parent=self.task_role)
        )

        self.task_execution_role_arn = self.task_execution_role.arn
        self.task_role_arn = self.task_role.arn

        self.register_outputs({})
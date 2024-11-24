from pulumi import ComponentResource, ResourceOptions, Output
import pulumi_aws as aws
import json

class TaskDefinition(ComponentResource):
    def __init__(self, name: str, execution_role_arn: str, task_role_arn: str,
                 log_group_name: str, db_secret_arn: str = None, app_secret_arn: str = None,
                 tags: dict = None, opts: ResourceOptions = None):
        super().__init__("custom:compute:TaskDefinition", name, None, opts)

        # Use Output.all() to handle the Pulumi Output
        def create_container_definition(log_group):
            container_definition = {
                "name": "app",
                "image": "your-app-image:latest",
                "cpu": 256,
                "memory": 512,
                "essential": True,
                "portMappings": [{
                    "containerPort": 8080,
                    "protocol": "tcp"
                }],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": log_group,
                        "awslogs-region": "us-west-2",
                        "awslogs-stream-prefix": "ecs"
                    }
                }
            }

            # Only add secrets if they are provided
            if db_secret_arn or app_secret_arn:
                container_definition["secrets"] = []
                if db_secret_arn:
                    container_definition["secrets"].append({
                        "name": "DB_CONNECTION",
                        "valueFrom": db_secret_arn
                    })
                if app_secret_arn:
                    container_definition["secrets"].append({
                        "name": "APP_SECRETS",
                        "valueFrom": app_secret_arn
                    })

            return json.dumps([container_definition])

        container_defs = Output.all(log_group_name).apply(
            lambda args: create_container_definition(args[0])
        )

        # Create Task Definition with proper parenting
        self.task_definition = aws.ecs.TaskDefinition(f"{name}-task",
            family=f"{name}-task",
            cpu="256",
            memory="512",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=execution_role_arn,
            task_role_arn=task_role_arn,
            container_definitions=container_defs,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        self.task_definition_arn = self.task_definition.arn

        self.register_outputs({
            "task_definition_arn": self.task_definition_arn
        })
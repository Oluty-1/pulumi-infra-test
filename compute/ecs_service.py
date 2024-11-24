from pulumi import ComponentResource
import pulumi_aws as aws

class ECSService(ComponentResource):
    def __init__(self, name, cluster_arn, task_definition_arn, target_group_arn, 
                 subnet_ids, security_groups,tags=None, opts=None):
        super().__init__("custom:compute:ECSService", name, None, opts)

        # Create ECS Service
        self.service = aws.ecs.Service(f"{name}-service",
            cluster=cluster_arn,
            task_definition=task_definition_arn,
            desired_count=2,
            launch_type="FARGATE",
            platform_version="LATEST",
            
            network_configuration={
                "assign_public_ip": False,
                "subnets": subnet_ids,
                "security_groups": [security_groups.ecs_tasks_sg_id]
            },
            
            load_balancers=[{
                "target_group_arn": target_group_arn,
                "container_name": "app",
                "container_port": 8080
            }],
            
            force_new_deployment=True,
            
            # Configure service to use FARGATE_SPOT with FARGATE as backup
            capacity_provider_strategies=[
                {
                    "capacity_provider": "FARGATE_SPOT",
                    "weight": 4,
                    "base": 0
                },
                {
                    "capacity_provider": "FARGATE",
                    "weight": 1,
                    "base": 0
                }
            ],

            health_check_grace_period_seconds=60,
            deployment_maximum_percent=200,
            deployment_minimum_healthy_percent=100,
            
            # Enable ECS Exec for debugging
            enable_execute_command=True
        )

        self.register_outputs({})

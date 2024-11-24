from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class ECSCluster(ComponentResource):
    def __init__(self, name: str, log_group_name: str, 
                 tags: dict = None, opts: ResourceOptions = None):
        super().__init__("custom:compute:ECSCluster", name, None, opts)

        # Create ECS Cluster with proper parenting
        self.cluster = aws.ecs.Cluster(f"{name}-cluster",
            settings=[{
                "name": "containerInsights",
                "value": "enabled"
            }],
            configuration={
                "execute_command_configuration": {
                    "logging": "OVERRIDE",
                    "log_configuration": {
                        "cloud_watch_log_group_name": log_group_name
                    }
                }
            },
            tags=dict(tags or {}, Name=f"{name}-cluster"),
            opts=ResourceOptions(parent=self)
        )

        # Configure cluster capacity providers with proper parenting
        self.capacity_providers = aws.ecs.ClusterCapacityProviders(f"{name}-cluster-cp",
            cluster_name=self.cluster.name,
            capacity_providers=["FARGATE_SPOT", "FARGATE"],
            default_capacity_provider_strategies=[
                {
                    "base": 0,
                    "weight": 4,
                    "capacityProvider": "FARGATE_SPOT"
                },
                {
                    "base": 0,
                    "weight": 1,
                    "capacityProvider": "FARGATE"
                }
            ],
            opts=ResourceOptions(parent=self.cluster)
        )

        # Register outputs
        self.cluster_name = self.cluster.name
        self.cluster_arn = self.cluster.arn

        self.register_outputs({
            "cluster_name": self.cluster_name,
            "cluster_arn": self.cluster_arn
        })
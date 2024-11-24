from pulumi import ComponentResource, ResourceOptions
from .cloudwatch import CloudWatchConfig
from .opensearch import OpenSearchMonitoring
import pulumi_aws as aws

class MonitoringStack(ComponentResource):
    def __init__(self, name, vpc_id, subnet_ids, security_group_id, cluster_name, rds_instance_id, tags=None, opts=None):
        super().__init__("custom:monitoring:MonitoringStack", name, None, opts)

        # Create CloudWatch Configuration
        self.cloudwatch = CloudWatchConfig(f"{name}",
            cluster_name=cluster_name,
            rds_instance_id=rds_instance_id,
            opts=ResourceOptions(parent=self)
        )

        # Create OpenSearch Configuration
        self.opensearch = OpenSearchMonitoring(f"{name}",
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            security_group_id=security_group_id,
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({})

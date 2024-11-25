from pulumi import ComponentResource, ResourceOptions
from typing import List, Optional
from .components.logs import LogAggregationStack
from .components.metrics import MetricsStack
from .components.alerts import AlertingStack

class MonitoringStack(ComponentResource):
    def __init__(self,
                 name: str,
                 vpc_id: str,
                 subnet_ids: List[str],
                 security_group_id: str,
                 cluster_name: str,
                 service_name: str,
                 rds_instance_id: str,
                 environment: str,
                 tags: Optional[dict] = None,
                 opts: Optional[ResourceOptions] = None):
        super().__init__("custom:monitoring:MonitoringStack", name, None, opts)

        self.tags = {
            "Name": name,
            "Environment": environment,
            **(tags or {})
        }

        self.log_aggregation = LogAggregationStack(
            f"{name}-logs",
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            security_group_id=security_group_id,
            tags=self.tags,
            opts=ResourceOptions(parent=self)
        )

        self.metrics = MetricsStack(
            f"{name}-metrics",
            cluster_name=cluster_name,
            service_name=service_name,
            rds_instance_id=rds_instance_id,
            environment=environment,
            tags=self.tags,
            opts=ResourceOptions(parent=self)
        )

        self.alerting = AlertingStack(
            f"{name}-alerts",
            cluster_name=cluster_name,
            service_name=service_name,
            rds_instance_id=rds_instance_id,
            environment=environment,
            log_group_name=self.metrics.log_group_name,
            tags=self.tags,
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "opensearch_endpoint": self.log_aggregation.opensearch.endpoint,
            "cloudwatch_dashboard_url": self.metrics.dashboard_url,
            "alert_topic_arn": self.alerting.alert_topic.arn
        })
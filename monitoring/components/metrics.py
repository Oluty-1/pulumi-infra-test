from pulumi import ComponentResource, ResourceOptions, Output
from typing import List, Optional
import pulumi_aws as aws
import json

class MetricsStack(ComponentResource):
    def __init__(self,
                 name: str,
                 cluster_name: str,
                 service_name: str,
                 rds_instance_id: str,
                 environment: str,
                 tags: dict,
                 opts: Optional[ResourceOptions] = None):
        super().__init__("custom:monitoring:MetricsStack", name, None, opts)

        self.log_group = aws.cloudwatch.LogGroup(
            f"{name}-app-logs",
            name=f"/apps/{environment}/{name}",
            retention_in_days=30,
            tags=tags
        )

        # Combine all outputs to create the dashboard
        combined_config = Output.all(cluster_name=cluster_name,
                                   service_name=service_name,
                                   rds_instance_id=rds_instance_id).apply(
            lambda args: self._create_dashboard_config(
                args['cluster_name'],
                args['service_name'],
                args['rds_instance_id']
            )
        )

        self.dashboard = aws.cloudwatch.Dashboard(
            f"{name}-dashboard",
            dashboard_name=f"{environment}-{name}-dashboard",
            dashboard_body=combined_config,
            opts=ResourceOptions(parent=self)
        )

        self.log_group_name = self.log_group.name
        self.dashboard_url = Output.concat(
            "https://console.aws.amazon.com/cloudwatch/home#dashboards:name=",
            self.dashboard.dashboard_name
        )

        self.register_outputs({
            "log_group_name": self.log_group_name,
            "dashboard_url": self.dashboard_url
        })

    def _create_dashboard_config(self, cluster_name: str, service_name: str, rds_instance_id: str) -> str:
        config = {
            "widgets": [
                self._create_metric_widget(
                    title="ECS Service Metrics",
                    metrics=[
                        ["AWS/ECS", "CPUUtilization", "ClusterName", cluster_name, "ServiceName", service_name],
                        [".", "MemoryUtilization", ".", ".", ".", "."]
                    ],
                    x=0, y=0
                ),
                self._create_metric_widget(
                    title="RDS Metrics",
                    metrics=[
                        ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", rds_instance_id],
                        [".", "FreeStorageSpace", ".", "."],
                        [".", "DatabaseConnections", ".", "."]
                    ],
                    x=12, y=0
                ),
                # Add Application Metrics
                self._create_metric_widget(
                    title="Application Health",
                    metrics=[
                        ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", "${tg_arn_suffix}"],
                        [".", "UnHealthyHostCount", ".", "."],
                        [".", "RequestCount", ".", "."],
                        [".", "TargetResponseTime", ".", "."]
                    ],
                    x=0, y=6
                )
            ]
        }
        return json.dumps(config)

    def _create_metric_widget(self, title: str, metrics: List, x: int, y: int) -> dict:
        return {
            "type": "metric",
            "x": x,
            "y": y,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": metrics,
                "period": 300,
                "stat": "Average",
                "region": "us-west-1",  # You might want to make this configurable
                "title": title
            }
        }
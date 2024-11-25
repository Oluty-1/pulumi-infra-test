from pulumi import ComponentResource, ResourceOptions
from typing import List, Optional
import pulumi_aws as aws

class AlertingStack(ComponentResource):
    def __init__(self,
                 name: str,
                 cluster_name: str,
                 service_name: str,
                 rds_instance_id: str,
                 environment: str,
                 log_group_name: str,
                 tags: dict,
                 opts: Optional[ResourceOptions] = None):
        super().__init__("custom:monitoring:AlertingStack", name, None, opts)

        self.alert_topic = aws.sns.Topic(
            f"{name}-topic",
            name=f"{environment}-{name}-alerts",
            tags=tags
        )

        self.alarms = self._create_alarms(
            name,
            cluster_name,
            service_name,
            rds_instance_id,
            log_group_name,
            self.alert_topic.arn,
            tags
        )

        self.register_outputs({
            "alert_topic_arn": self.alert_topic.arn,
            "alarm_names": [alarm.name for alarm in self.alarms]
        })

    def _create_alarms(self, name: str, cluster_name: str, service_name: str,
                      rds_instance_id: str, log_group_name: str, topic_arn: str,
                      tags: dict) -> List[aws.cloudwatch.MetricAlarm]:
        return [
            self._create_alarm(
                f"{name}-ecs-cpu",
                "AWS/ECS",
                "CPUUtilization",
                "GreaterThanThreshold",
                85.0,
                {"ClusterName": cluster_name, "ServiceName": service_name},
                topic_arn,
                tags
            ),
            self._create_alarm(
                f"{name}-rds-cpu",
                "AWS/RDS",
                "CPUUtilization",
                "GreaterThanThreshold",
                80.0,
                {"DBInstanceIdentifier": rds_instance_id},
                topic_arn,
                tags
            ),
            self._create_alarm(
                f"{name}-rds-storage",
                "AWS/RDS",
                "FreeStorageSpace",
                "LessThanThreshold",
                20_000_000_000,
                {"DBInstanceIdentifier": rds_instance_id},
                topic_arn,
                tags
            )
        ]

    def _create_alarm(self, name: str, namespace: str, metric_name: str,
                     comparison_operator: str, threshold: float,
                     dimensions: dict, topic_arn: str, tags: dict) -> aws.cloudwatch.MetricAlarm:
        return aws.cloudwatch.MetricAlarm(
            name,
            comparison_operator=comparison_operator,
            evaluation_periods=2,
            metric_name=metric_name,
            namespace=namespace,
            period=300,
            statistic="Average",
            threshold=threshold,
            alarm_actions=[topic_arn],
            dimensions=dimensions,
            tags=tags
        )
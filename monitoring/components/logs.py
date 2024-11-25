from pulumi import ComponentResource, ResourceOptions
from typing import List, Optional
import pulumi_aws as aws

class LogAggregationStack(ComponentResource):
    def __init__(self,
                 name: str,
                 vpc_id: str,
                 subnet_ids: List[str],
                 security_group_id: str,
                 tags: dict,
                 opts: Optional[ResourceOptions] = None):
        super().__init__("custom:monitoring:LogAggregationStack", name, None, opts)

        self.opensearch = OpenSearchCluster(
            name,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            security_group_id=security_group_id,
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "opensearch_endpoint": self.opensearch.endpoint
        })

class OpenSearchCluster(ComponentResource):
    def __init__(self,
                 name: str,
                 vpc_id: str,
                 subnet_ids: List[str],
                 security_group_id: str,
                 tags: dict,
                 opts: Optional[ResourceOptions] = None):
        super().__init__("custom:monitoring:OpenSearchCluster", name, None, opts)

        self.domain = aws.opensearch.Domain(
            f"{name}-domain",
            cluster_config={
                "instance_type": "t3.small.search",
                "instance_count": 2,
                "zone_awareness_enabled": True,
                "zone_awareness_config": {
                    "availability_zone_count": 2
                }
            },
            ebs_options={
                "ebs_enabled": True,
                "volume_size": 10,
                "volume_type": "gp3"
            },
            vpc_options={
                "subnet_ids": subnet_ids[:2],
                "security_group_ids": [security_group_id]
            },
            encrypt_at_rest={"enabled": True},
            node_to_node_encryption={"enabled": True},
            domain_endpoint_options={
                "enforce_https": True,
                "tls_security_policy": "Policy-Min-TLS-1-2-2019-07"
            },
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        self.endpoint = self.domain.endpoint

        self.register_outputs({
            "endpoint": self.endpoint
        })
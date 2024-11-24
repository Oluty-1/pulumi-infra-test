from pulumi import ComponentResource
import pulumi_aws as aws

class OpenSearchMonitoring(ComponentResource):
    def __init__(self, name, vpc_id, subnet_ids, security_group_id, opts=None):
        super().__init__("custom:monitoring:OpenSearchMonitoring", name, None, opts)

        # Create OpenSearch Domain
        self.domain = aws.opensearch.Domain(f"{name}-logs",
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
                "subnet_ids": subnet_ids[:2],  # Use 2 subnets for HA
                "security_group_ids": [security_group_id]
            },
            encrypt_at_rest={
                "enabled": True
            },
            node_to_node_encryption={
                "enabled": True
            },
            domain_endpoint_options={
                "enforce_https": True,
                "tls_security_policy": "Policy-Min-TLS-1-2-2019-07"
            },
            tags={
                "Name": f"{name}-opensearch",
                "Environment": "dev"
            }
        )

        self.endpoint = self.domain.endpoint

        self.register_outputs({})

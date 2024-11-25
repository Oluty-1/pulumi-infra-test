from pulumi import ComponentResource, ResourceOptions, Output
import pulumi_aws as aws

class RDSInstance(ComponentResource):
    def __init__(self, name: str, vpc_id: str, subnet_group_name: str, security_group_id: str,
                 tags: dict = None, opts: ResourceOptions = None):
        super().__init__("custom:data:RDSInstance", name, None, opts)

        # Create RDS instance with IAM authentication enabled
        self.instance = aws.rds.Instance(f"{name}-postgres",
            engine="postgres",
            engine_version="15.8-R2",
            instance_class="db.t3.micro",
            allocated_storage=20,
            db_subnet_group_name=subnet_group_name,
            vpc_security_group_ids=[security_group_id],
            # parameter_group_name=parameter_group_name,
            skip_final_snapshot=True,
            iam_database_authentication_enabled=True,  # Enable IAM authentication
            tags=tags,
            opts=ResourceOptions(parent=self)
        )

        # Create IAM policy for RDS IAM authentication
        rds_connect_policy = aws.iam.Policy(f"{name}-rds-connect",
            description="Policy for RDS IAM authentication",
            policy=Output.all(self.instance.arn).apply(
                lambda args: {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": [
                            "rds-db:connect"
                        ],
                        "Resource": [
                            f"{args[0]}/database_user"
                        ]
                    }]
                }
            ),
            opts=ResourceOptions(parent=self)
        )

        self.instance_id = self.instance.id
        self.endpoint = self.instance.endpoint
        self.policy_arn = rds_connect_policy.arn

        self.register_outputs({
            "instance_id": self.instance_id,
            "endpoint": self.endpoint,
            "policy_arn": self.policy_arn
        })
from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
import json

class BackupConfig(ComponentResource):
    def __init__(self, name, vault_name, resource_id, rds_instance_arn, tags=None, opts=None):
        super().__init__("custom:data:BackupConfig", name, None, opts)

        # Create AWS Backup Vault
        self.backup_vault = aws.backup.Vault(vault_name,
            name=vault_name,
            tags=dict(tags or {}, Name=vault_name)
        )

        # Create AWS Backup Plan
        self.backup_plan = aws.backup.Plan(f"{name}-plan",
            name=f"{name}-backup-plan",
            rules=[{
                "rule_name": "daily_backup",
                "target_vault_name": self.backup_vault.name,
                "schedule": "cron(0 5 ? * * *)",  # Daily at 5 AM UTC
                "start_window": 60,
                "completion_window": 120,
                "lifecycle": {
                    "cold_storage_after": 90,
                    "delete_after": 180
                }
            }],
            tags=dict(tags or {}, Name=f"{name}-backup-plan")
        )

        # Create Selection for the Backup Plan
        self.backup_selection = aws.backup.Selection(f"{name}-selection",
            name=f"{name}-backup-selection",
            plan_id=self.backup_plan.id,
            iam_role_arn=self._get_backup_role().arn,
            resources=[rds_instance_arn]
        )

        self.register_outputs({})

    def _get_backup_role(self):
        try:
            # Try to get existing AWS Backup service role
            return aws.iam.get_role(name="AWSBackupDefaultServiceRole")
        except:
            # If role doesn't exist, create it
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "backup.amazonaws.com"
                    }
                }]
            }
            
            role = aws.iam.Role("backup-service-role",
                name="AWSBackupDefaultServiceRole",
                assume_role_policy=json.dumps(assume_role_policy),
                managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"]
            )
            
            return role
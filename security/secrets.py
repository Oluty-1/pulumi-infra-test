from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class SecretsManager(ComponentResource):
    def __init__(self, name, tags=None, opts=None):
        super().__init__("custom:security:SecretsManager", name, None, opts)

        # Create KMS key for encrypting secrets
        self.kms_key = aws.kms.Key(f"{name}-secrets-key",
            description=f"KMS key for {name} secrets",
            enable_key_rotation=True,
            tags=dict(tags or {}, Name=f"{name}-secrets-key")
        )

        # Create alias for the KMS key
        self.kms_alias = aws.kms.Alias(f"{name}-secrets-key-alias",
            name=f"alias/{name}-secrets-key",
            target_key_id=self.kms_key.id
        )

        # Create secret for application environment variables
        self.app_secret = aws.secretsmanager.Secret(f"{name}-app-secret",
            kms_key_id=self.kms_key.id,
            name=f"{name}/application",
            tags=dict(tags or {}, Name=f"{name}-app-secret")
        )

        # Store application secrets
        self.app_secret_version = aws.secretsmanager.SecretVersion(f"{name}-app-secret-version",
            secret_id=self.app_secret.id,
            secret_string="""{
                "API_KEY": "your-api-key",
                "OTHER_SECRET": "other-secret-value"
            }"""
        )

        self.app_secret_arn = self.app_secret.arn

        self.register_outputs({
            "app_secret_arn": self.app_secret_arn,
            "kms_key_id": self.kms_key.id
        })
        
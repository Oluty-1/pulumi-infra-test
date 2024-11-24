from typing import Dict

def get_resource_tags(name: str, stack: str, resource_type: str) -> Dict[str, str]:
    """
    Generate consistent tags for resources.
    
    Args:
        name: Resource name prefix
        stack: Stack name (e.g., 'dev', 'prod')
        resource_type: Type of resource (e.g., 'vpc', 'ecs', 'rds')
    """
    return {
        "Name": f"{name}-{resource_type}",
        "Environment": stack,
        "ManagedBy": "pulumi",
        "Project": "numeris",
        "Owner": "devops-team",
        "CostCenter": "infrastructure"
    }

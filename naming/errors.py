from typing import Callable, Any
from functools import wraps
import pulumi

def handle_aws_errors(func: Callable) -> Callable:
    """Decorator to handle AWS-related errors during resource creation"""
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger = args[0].logger if hasattr(args[0], 'logger') else None
            if logger:
                logger.error(f"Error in {func.__name__}: {str(e)}")
            
            # Raise a Pulumi error
            raise pulumi.RunError(f"AWS Resource Creation Failed: {str(e)}")
    
    return wrapper

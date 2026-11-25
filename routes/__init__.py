"""Routes, one blueprint per area (CS174-18, slides 37-38)."""
from functools import wraps

from flask import request


def ensure_args(keys): # recieve keys
	def decorator(func): # recieve function
		@wraps(func)
		def wrapper(*args, **kwargs): # wrapper function that runs
			missing = set(keys) - set(request.form)
			if not missing: return func(*args, **kwargs)
			return f"Required request arguments {', '.join(missing)} missing", 400
		return wrapper
	return decorator

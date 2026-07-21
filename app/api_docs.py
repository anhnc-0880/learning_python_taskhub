from app.schemas import ErrorResponse, ValidationErrorResponse

auth_responses = {
    401: {"model": ErrorResponse, "description": "Authentication required or invalid token"},
    422: {"model": ValidationErrorResponse, "description": "Validation error"},
}

owner_responses = {
    **auth_responses,
    403: {"model": ErrorResponse, "description": "Only task owner or admin can perform this action"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
}

public_responses = {
    400: {"model": ErrorResponse, "description": "Bad request"},
    401: {"model": ErrorResponse, "description": "Invalid credentials"},
    422: {"model": ValidationErrorResponse, "description": "Validation error"},
}

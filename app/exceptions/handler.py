"""Custom exception handlers."""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.event import ErrorResponse, SearchResponse


async def search_exception_handler(
    _: Request, exception: HTTPException
) -> JSONResponse:
    """Handle search exceptions."""

    if isinstance(exception, RequestValidationError):
        error_msg = "Validation error"
        response = SearchResponse(
            data=None,
            error=ErrorResponse(code="400", message=error_msg),
        )
        status_code = 400
    else:
        response = SearchResponse(
            data=None,
            error=ErrorResponse(
                code=str(exception.status_code), message=exception.detail
            ),
        )
        status_code = 500

    return JSONResponse(status_code=status_code, content=response.model_dump())

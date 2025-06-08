from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from base.connect import db_conn
from server.dependes import user_, post_
from schema.user import SchemaUser, SchemaVerification
from typing import Dict, Any


user = APIRouter(tags=['Users'], prefix='/users',
                 responses={404: {"description": "Not found"}})


@user.post("/",
           response_model=Dict[str, Any],
           status_code=status.HTTP_201_CREATED,
           summary="Create a new user",
           responses={
                201: {"description": "User created successfully"},
                400: {"description": "Bad request"},
                409: {"description": "User already exists"},
                500: {"description": "Internal server error"}
           })
async def create_user(new_user: SchemaUser,
                      db: AsyncSession = Depends(db_conn)) -> Dict[str, Any]:

    result = await user_.new_user(db, new_user)

    if result.get("status_code") != 201:
        raise HTTPException(
            status_code=result["status_code"],
            detail={
                "title": result.get("title", "Error"),
                "description": result.get("description", "Unknown error")
            }
        )

    return result


@user.delete("/{user_id}",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Delete a user by ID",
             responses={
                    200: {"description": "User deleted successfully"},
                    404: {"description": "User not found"},
                    500: {"description": "Internal server error"}
             })
async def delete_user(user_id: int,
                      db: AsyncSession = Depends(db_conn)) -> Dict[str, Any]:

    posts_result = await post_.delete_post_user(db, user_id=user_id)
    if posts_result.get("status_code") not in [200, 404]:
        raise HTTPException(
            status_code=posts_result["status_code"],
            detail={
                "title": posts_result.get("title", "Error deleting posts"),
                "description": posts_result.get("description", "Unknown error")
            }
        )

    user_result = await user_.delete_user(db, user_id=user_id)
    if user_result.get("status_code") != 200:
        raise HTTPException(
            status_code=user_result["status_code"],
            detail={
                "title": user_result.get("title", "Error deleting user"),
                "description": user_result.get("description", "Unknown error")
            }
        )

    return {
        "status": "success",
        "message": f"User {user_id} and all their posts were deleted"
    }


@user.post("/login",
           response_model=Dict[str, Any],
           status_code=status.HTTP_200_OK,
           summary="Authenticate user",
           responses={
                200: {"description": "Authentication successful"},
                401: {"description": "Invalid credentials"},
                500: {"description": "Internal server error"}
           })
async def authenticate_user(credentials: SchemaVerification,
                            db: AsyncSession = Depends(db_conn)) -> Dict[str, Any]:

    result = await user_.verification(db=db, credentials=credentials)

    if "token" in result:
        return result

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "title": "Authentication failed",
            "description": result.get("message", "Invalid login or password")
        }
    )

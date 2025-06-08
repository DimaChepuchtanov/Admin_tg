from fastapi.routing import APIRouter
from fastapi import Depends, Request, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from base.connect import db_conn
from server.dependes import user_, post_
from schema.post import SchemaPost, SchemaPostUpdate
from typing import Dict, Any, List


router = APIRouter(tags=['Posts'],prefix='/posts',
                   responses={404: {"description": "Not found"}})


async def verify_token(token: str = Query(..., description="User authentication token"),
                       request: Request = None,
                       db: AsyncSession = Depends(db_conn)) -> None:
    """
    Verify user authentication token.

    Args:
        token: User authentication token
        request: FastAPI request object
        db: Database session

    Raises:
        HTTPException: 403 if token is invalid
    """
    is_valid = await user_.check_token(db, token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )


@router.post("/",
             response_model=Dict[str, Any],
             status_code=status.HTTP_201_CREATED,
             summary="Create a new post",
             responses={
                201: {"description": "Post created successfully"},
                403: {"description": "Invalid authentication token"},
                404: {"description": "Author not found"},
                500: {"description": "Internal server error"}
             })
async def create_post(new_post: SchemaPost,
                      db: AsyncSession = Depends(db_conn),
                      token: str = Depends(verify_token)) -> Dict[str, Any]:
    result = await post_.new_post(db, new_post)

    if result.get("status_code") != 201:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result.get("description", "Error creating post")
        )

    return result


@router.delete("/{post_id}",
               response_model=Dict[str, Any],
               status_code=status.HTTP_200_OK,
               summary="Delete a post by ID",
               responses={
                    200: {"description": "Post deleted successfully"},
                    403: {"description": "Invalid authentication token"},
                    404: {"description": "Post not found"},
                    500: {"description": "Internal server error"}
                })
async def delete_post(post_id: int,
                      db: AsyncSession = Depends(db_conn),
                      token: str = Depends(verify_token)) -> Dict[str, Any]:

    result = await post_.delete_post(db, post_id=post_id)

    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result.get("description", "Error deleting post")
        )

    return result


@router.patch("/{post_id}",
              response_model=Dict[str, Any],
              status_code=status.HTTP_200_OK,
              summary="Update a post by ID",
              responses={
                200: {"description": "Post updated successfully"},
                403: {"description": "Invalid authentication token"},
                404: {"description": "Post not found"},
                500: {"description": "Internal server error"}
              })
async def update_post(post_id: int,
                      update: SchemaPostUpdate,
                      db: AsyncSession = Depends(db_conn),
                      token: str = Depends(verify_token)) -> Dict[str, Any]:
    if update.id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post ID in path does not match ID in request body"
        )

    result = await post_.update_post(db, update)

    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result.get("description", "Error updating post")
        )

    return result


@router.get("/{post_id}",
            response_model=Dict[str, Any],
            status_code=status.HTTP_200_OK,
            summary="Get a post by ID",
            responses={
                200: {"description": "Post details"},
                404: {"description": "Post not found"},
                500: {"description": "Internal server error"}
            })
async def get_post(post_id: int,
                   db: AsyncSession = Depends(db_conn)) -> Dict[str, Any]:
    result = await post_.get_post(db, post_id)

    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Post not found")
        )

    return result


@router.get("/",
            response_model=List[Dict[str, Any]],
            status_code=status.HTTP_200_OK,
            summary="Get filtered list of posts",
            responses={
                200: {"description": "List of posts"},
                400: {"description": "Invalid filter parameters"},
                500: {"description": "Internal server error"}
            })
async def get_posts(sort_by: str = Query("created_at",
                                         alias="desc",
                                         description="Sort field (created_at or title)"),
                    limit: int = Query(None,
                                    alias="limit",
                                    description="Maximum number of posts to return"),
                    author_id: int = Query(None, 
                                        alias="author",
                                        description="Filter by author ID"),
                    db: AsyncSession = Depends(db_conn)) -> List[Dict[str, Any]]:

    filter_params = {}
    if sort_by:
        filter_params["desc"] = sort_by
    if limit is not None:
        filter_params["limit"] = limit
    if author_id is not None:
        filter_params["author"] = author_id

    result = await post_.get_posts(db, filter_params)

    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Invalid filter parameters")
        )

    return result

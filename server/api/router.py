from fastapi import APIRouter
from api.routers import users, movies, comments, episodes

main_router = APIRouter()

main_router.include_router(users.user_router, prefix="/users", tags=["users"])
main_router.include_router(movies.movie_router, prefix="/movies", tags=["movies"])
main_router.include_router(comments.comment_router, prefix="/comments", tags=["comments"])
main_router.include_router(episodes.episode_router, prefix="/episodes", tags=["episodes"])

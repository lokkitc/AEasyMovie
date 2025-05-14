from fastapi import APIRouter
from api.routers import users, movies, comments, episodes, premium, auth
main_router = APIRouter()

main_router.include_router(main_router, prefix="/api")
main_router.include_router(auth.auth_router, prefix="/api/auth", tags=["auth"])
main_router.include_router(users.user_router, prefix="/api/users", tags=["users"])
main_router.include_router(movies.movie_router, prefix="/api/movies", tags=["movies"])
main_router.include_router(comments.comment_router, prefix="/api/comments", tags=["comments"])
main_router.include_router(episodes.episode_router, prefix="/api/episodes", tags=["episodes"])
main_router.include_router(premium.premium_router, prefix="/api/premium", tags=["premium"])
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.auth import get_current_user_from_token
from db.session import get_db
from db.models.users import User
from schemas.users import PremiumPurchaseRequest, PremiumPurchaseResponse
from api.services.premium_service import purchase_premium

premium_router = APIRouter()

@premium_router.post("/purchase", response_model=PremiumPurchaseResponse)
async def purchase_premium_subscription(
    request: PremiumPurchaseRequest,
    current_user: User = Depends(get_current_user_from_token),
    session: AsyncSession = Depends(get_db)
) -> PremiumPurchaseResponse:
    """
    Покупка премиум-подписки
    """
    try:
        result = await purchase_premium(
            user=current_user,
            months=request.months,
            payment_method=request.payment_method,
            session=session
        )
        return PremiumPurchaseResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при покупке премиум-подписки: {str(e)}"
        ) 
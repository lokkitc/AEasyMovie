import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, DateTime, Enum as SQLAlchemyEnum, Float
from enum import Enum
from .base import Base

DEFAULT_PHOTO = "https://i.pinimg.com/736x/fd/02/55/fd02556bc6ce735541793834bd8725ce.jpg"
DEFAULT_HEADER_PHOTO = "https://i.pinimg.com/736x/9b/4d/ab/9b4dab17886caaab85a4a7eec70a3792.jpg"

class UserRole(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"

    def can_moderate(self) -> bool:
        return self in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPERADMIN]

    def is_admin(self) -> bool:
        return self in [UserRole.ADMIN, UserRole.SUPERADMIN]

    def is_superadmin(self) -> bool:
        return self == UserRole.SUPERADMIN

class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"


    role: Mapped[UserRole] = mapped_column(SQLAlchemyEnum(UserRole, name="user_role"), nullable=False, default=UserRole.USER)

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    photo: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_PHOTO)
    frame_photo: Mapped[str] = mapped_column(String, nullable=True)
    header_photo: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_HEADER_PHOTO)

    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    about: Mapped[str] = mapped_column(String, nullable=False, default="Пользователь ничего о себе не написал.")
    location: Mapped[str] = mapped_column(String, nullable=False, default="")
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Премиум система
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    money: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String, default="Новичок")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Отношения
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    owned_movies: Mapped[list['Movie']] = relationship("Movie", back_populates="owner")
    purchased_episodes: Mapped[list["PurchasedEpisode"]] = relationship("PurchasedEpisode", back_populates="user")




    def has_role(self, role: UserRole) -> bool:
        return self.role == role

    def can_moderate(self) -> bool:
        return self.role.can_moderate()

    def is_admin(self) -> bool:
        return self.role.is_admin()

    def is_superadmin(self) -> bool:
        return self.role.is_superadmin()

    def is_premium_active(self) -> bool:
        """Проверяет, активна ли премиум-подписка"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return False
        return datetime.now() < self.premium_until

    def can_watch_episode(self, episode_cost: float = 50.0) -> tuple[bool, str]:
        """
        Проверяет, может ли пользователь смотреть эпизод
        Возвращает (может_смотреть, сообщение)
        """
        if self.is_premium_active():
            return True, "Премиум-подписка активна"
        
        if self.money >= episode_cost:
            return True, f"Достаточно денег ({self.money} монет)"
            
        return False, f"Недостаточно денег. Нужно {episode_cost} монет, доступно {self.money} монет"

    def check_and_update_premium_status(self) -> bool:
        """Проверяет и обновляет статус премиум-подписки"""
        if self.is_premium and self.premium_until and datetime.now() >= self.premium_until:
            self.is_premium = False
            self.premium_until = None
            return False
        return self.is_premium_active()

    def add_premium_days(self, days: int) -> None:
        """Добавляет дни к премиум-подписке"""
        if not self.is_premium or not self.premium_until:
            self.premium_until = datetime.now()
        self.premium_until += timedelta(days=days)
        self.is_premium = True

    def add_money(self, amount: float) -> None:
        """Добавляет деньги на баланс пользователя"""
        self.money += amount

    def spend_money(self, amount: float) -> bool:
        """Тратит деньги с баланса пользователя"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def update_level(self) -> None:
        """Обновляет уровень пользователя на основе его активности"""
        # Простая формула для расчета уровня
        self.level = max(1, min(100, self.level + 1))
        # Обновляем титул в зависимости от уровня
        if self.level < 5:
            self.title = "Новичок"
        elif self.level < 10:
            self.title = "Активный пользователь"
        elif self.level < 20:
            self.title = "Опытный пользователь"
        elif self.level < 50:
            self.title = "Ветеран"
        else:
            self.title = "Легенда"

    def can_modify_user(self, target_user: 'User') -> bool:
        """Проверяет, может ли текущий пользователь модифицировать целевого пользователя"""
        # Пользователь всегда может редактировать свой профиль
        if self.user_id == target_user.user_id:
            return True
        # Суперадмин может редактировать любого
        if self.is_superadmin():
            return True
        # Админ может редактировать всех, кроме других админов и суперадмина
        if self.is_admin() and not target_user.is_admin():
            return True
        # Модератор может редактировать только обычных пользователей
        if self.role == UserRole.MODERATOR and target_user.role == UserRole.USER:
            return True
        return False

    def validate(self) -> bool:
        if not self.username or len(self.username) < 3:
            return False
        if not self.email or '@' not in self.email:
            return False
        if not self.name or not self.surname:
            return False
        if self.age < 0 or self.age > 150:
            return False
        return True
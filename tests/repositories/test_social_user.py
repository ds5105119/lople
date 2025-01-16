import pytest
import pytest_asyncio
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from pydantic import BaseModel
from src.app.user.repository.social_user import SocialUserReadRepository

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    social_provider = Column(String(50), nullable=True)
    social_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    social_provider: str
    social_id: str
    is_active: bool

    class Config:
        from_attributes = True  # Enable ORM compatibility

class SocialUserVerificationDTO(BaseModel):
    """
    최초 소셜 로그인 User 정보 식별
    """
    email: str
    social_provider: str

class SocialUserRepository:
    def __init__(self, user_model):
        self.user_model = user_model

    async def get_user(self, session, **kwargs) -> UserResponse | None:
        stmt = select(self.user_model).filter_by(**kwargs)
        result = await session.execute(stmt)

        return result.scalars().first()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session(test_db):
    async_session_local = async_sessionmaker(bind=test_db, class_=AsyncSession)

    async with async_session_local() as session:
        yield session
#

@pytest_asyncio.fixture
def social_user_repository():
    return SocialUserRepository(User)


@pytest.mark.asyncio
async def test_get_user(session, social_user_repository):
    test_user = User(
        email="test@example.com", username="tester", password="secure", social_provider="google", social_id="123"
    )
    session.add(test_user)
    await session.commit()

    retrieved_user = await social_user_repository.get_user(
        session=session, email="test@example.com"
    )

    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_by_social_data(session, social_user_repository):
    test_user = User(
        email="socialuser@example.com",
        username="socialuser",
        password=None,
        social_provider="google",
        social_id="google123"
    )
    session.add(test_user)
    await session.commit()

    retrieved_user = await social_user_repository.get_user(
        session=session, social_provider="google", social_id="google123"
    )

    print("Retrieved User:", retrieved_user)

    assert retrieved_user is not None
    assert retrieved_user.email == "socialuser@example.com"
    assert retrieved_user.social_provider == "google"
    assert retrieved_user.social_id == "google123"


@pytest.mark.asyncio
async def test_get_user_not_found(session, social_user_repository):
    """
    테스트: 존재하지 않는 사용자 조회 시 None 확인
    """
    retrieved_user = await social_user_repository.get_user(
        session=session, email="nonexistent@example.com"
    )

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_create_user(session, social_user_repository):
    """
    테스트: 새 사용자를 생성하고 데이터베이스에 저장 확인
    """
    new_user = User(
        email="newuser@example.com",
        username="newuser",
        password="newpassword",
        social_provider="facebook",
        social_id="fb789"
    )
    session.add(new_user)
    await session.commit()

    # 생성된 사용자 확인
    retrieved_user = await social_user_repository.get_user(session=session, email="newuser@example.com")
    assert retrieved_user is not None
    assert retrieved_user.email == "newuser@example.com"
    assert retrieved_user.username == "newuser"


@pytest.mark.asyncio
async def test_duplicate_email_error(session):
    """
    테스트: 중복된 이메일을 가진 사용자 추가 시 IntegrityError 확인
    """
    user1 = User(
        email="duplicate@example.com",
        username="user1",
        password="password1"
    )
    user2 = User(
        email="duplicate@example.com",  # 동일 이메일
        username="user2",
        password="password2"
    )

    session.add(user1)
    await session.commit()

    session.add(user2)
    with pytest.raises(IntegrityError):  # 중복 에러 발생 확인
        await session.commit()
        await session.rollback()


@pytest.mark.asyncio
async def test_duplicate_social_id_error(session):
    """
    테스트: 중복된 소셜 ID를 가진 사용자 추가 시 IntegrityError 확인
    """
    user1 = User(
        email="social1@example.com",
        username="social1",
        social_provider="google",
        social_id="google123"
    )
    user2 = User(
        email="social2@example.com",
        username="social2",
        social_provider="google",
        social_id="google123"  # 동일 소셜 ID
    )

    session.add(user1)
    await session.commit()

    session.add(user2)
    with pytest.raises(IntegrityError):  # 중복 에러 발생 확인
        await session.commit()
        await session.rollback()

@pytest.mark.asyncio
async def test_social_user_get_user_by_social_provider(session):
    """
    소셜 인증 정보를 사용하여 사용자를 검색합니다.
    """
    # 테스트 데이터 추가
    test_user = User(
        email="social_user@example.com",
        username="social_user",
        social_id="social123",
        social_provider="google"
    )
    session.add(test_user)
    await session.commit()

    # Repository 초기화
    repository = SocialUserRepository(User)

    # 소셜 사용자 검색
    retrieved_user, status = await repository.get_user(
        session=session,
        data=SocialUserVerificationDTO(email="social_user@example.com", social_provider="google")
    )

    assert retrieved_user is not None
    assert retrieved_user.email == "social_user@example.com"
    assert retrieved_user.social_provider == "google"
    assert status == "social_auth"  # 소셜 사용자임을 확인


@pytest.mark.asyncio
async def test_social_user_get_user_by_email_only(session):
    """
    이메일만으로 일반 사용자를 검색합니다.
    """
    # 테스트 데이터 추가
    test_user = User(
        email="general_user@example.com",
        username="general_user",
        password="securepassword"
    )
    session.add(test_user)
    await session.commit()

    # Repository 초기화
    repository = SocialUserReadRepository(User)

    # 일반 사용자 검색
    retrieved_user, status = await repository.get_user(
        session=session,
        data=SocialUserVerificationDTO(email="general_user@example.com", social_provider=None)
    )

    assert retrieved_user is not None
    assert retrieved_user.email == "general_user@example.com"
    assert retrieved_user.social_provider is None
    assert status == "general"  # 일반 사용자임을 확인


@pytest.mark.asyncio
async def test_get_user_not_found(session):
    """
    존재하지 않는 사용자 검색 시 확인.
    """
    # Repository 초기화
    repository = SocialUserReadRepository(User)

    # 존재하지 않는 사용자 검색
    retrieved_user, status = await repository.get_user(
        session=session,
        data=SocialUserVerificationDTO(email="nonexistent@example.com", social_provider=None)
    )

    assert retrieved_user is None
    assert status == "not_found"  # 상태가 not_found임을 확인


@pytest.mark.asyncio
async def test_social_user_status_distinguish(session):
    """
    소셜 사용자와 일반 사용자의 상태를 구분합니다.
    """
    # 데이터 추가
    social_user = User(
        email="social_user2@example.com",
        username="social_user2",
        social_id="social456",
        social_provider="facebook"
    )
    general_user = User(
        email="general_user2@example.com",
        username="general_user2"
    )
    session.add(social_user)
    session.add(general_user)
    await session.commit()

    # Repository 초기화
    repository = SocialUserReadRepository(User)

    # 소셜 사용자 검색
    retrieved_social_user, social_status = await repository.get_user(
        session=session,
        data=SocialUserVerificationDTO(email="social_user2@example.com", social_provider="facebook")
    )
    assert retrieved_social_user is not None
    assert social_status == "social_auth"

    # 일반 사용자 검색
    retrieved_general_user, general_status = await repository.get_user(
        session=session,
        data=SocialUserVerificationDTO(email="general_user2@example.com", social_provider=None)
    )
    assert retrieved_general_user is not None
    assert general_status == "general"

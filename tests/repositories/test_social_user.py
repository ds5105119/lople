import pytest
import pytest_asyncio
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

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


class SocialUserRepository:
    def __init__(self, user_model):
        self.user_model = user_model

    async def get_user(self, session, **kwargs):
        stmt = select(self.user_model).filter_by(**kwargs)  # Use SQLAlchemy Core-style queries
        result = await session.execute(stmt)  # Execute the statement
        return result.scalars().first()  # Convert to ORM model and return the first result


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
async def test_deactivate_user(session, social_user_repository):
    """
    테스트: 기존 사용자를 비활성화 처리
    """
    test_user = User(
        email="activeuser@example.com",
        username="activeuser",
        password="activepassword",
        is_active=True
    )
    session.add(test_user)
    await session.commit()

    # 사용자 비활성 처리
    test_user.is_active = False
    await session.commit()

    # 업데이트 확인
    retrieved_user = await social_user_repository.get_user(session=session, email="activeuser@example.com")
    assert retrieved_user is not None
    assert retrieved_user.is_active is False


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
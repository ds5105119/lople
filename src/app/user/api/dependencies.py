from src.app.user.model.user import User
from src.app.user.model.user_data import UserData
from src.app.user.repository.user import UserRepository
from src.app.user.repository.user_data import UserDataRepository
from src.app.user.service.user import UserService
from src.app.user.service.user_data import UserDataService
from src.core.dependencies.auth import jwt_service

user_repository = UserRepository(User)
user_service = UserService(user_repository, jwt_service)

user_data_repository = UserDataRepository(UserData)
user_data_service = UserDataService(user_data_repository)

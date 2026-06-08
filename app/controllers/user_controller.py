from app.services.user_service import (
    register_user,
    login_user
)


def register_controller(
    username,
    email,
    password,
    role="user"
):

    return register_user(
        username,
        email,
        password,
        role
    )


def login_controller(
    email,
    password
):

    return login_user(
        email,
        password
    )
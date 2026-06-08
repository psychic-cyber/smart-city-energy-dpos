from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.models.users import User

from database.mongodb.user_repository import (
    save_user,
    find_user_by_email,
    find_user_by_username
)


def register_user(
    username,
    email,
    password,
    role="user"
):

    existing_email = (
        find_user_by_email(
            email
        )
    )

    if existing_email:

        return (
            False,
            "Email already exists"
        )

    existing_username = (
        find_user_by_username(
            username
        )
    )

    if existing_username:

        return (
            False,
            "Username already exists"
        )

    hashed_password = (
        generate_password_hash(
            password
        )
    )

    user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        energy_balance=0
    )

    save_user(
        user.to_dict()
    )

    return (
        True,
        "User registered successfully"
    )


def login_user(
    email,
    password
):

    user = (
        find_user_by_email(
            email
        )
    )

    if not user:

        return None

    if not check_password_hash(
        user["password"],
        password
    ):
        return None

    return user
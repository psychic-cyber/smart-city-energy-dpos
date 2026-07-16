from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.utils.wallet_generator import create_wallet

from database.models.users import User

from database.mongodb.user_repository import (
    save_user,
    find_user_by_email,
    find_user_by_username
)

from app.services.blockchain_client import (
    initialize_user
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

    wallet = create_wallet()

    user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=role,
        energy_balance=0,
        wallet_address=wallet["address"],
        private_key=wallet["private_key"]
    )

    user_dict = user.to_dict()

    save_user(user_dict)

    try:
        initialize_user(username)
    except Exception as e:
        print(e)

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
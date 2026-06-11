from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from app.controllers.user_controller import (
    register_controller,
    login_controller
)

from database.mongodb.user_repository import (
    get_user_by_username,
    update_energy_balance,
    update_revenue
)

from database.mongodb.user_transaction_repository import (
    save_user_transaction,
    get_user_transactions
)

from blockchain.core.blockchain import (
    Blockchain
)

from database.mongodb.blockchain_repository import (
    save_block
)

user_bp = Blueprint(
    "users",
    __name__
)


@user_bp.route("/")
def home():

    return render_template(
        "index.html"
    )


@user_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        result = register_controller(
            request.form["username"],
            request.form["email"],
            request.form["password"],
            "user"
        )

        if result[0]:

            return redirect(
                "/login"
            )

    return render_template(
        "register.html"
    )


@user_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        user = login_controller(
            request.form["email"],
            request.form["password"]
        )

        if user:

            session["user_id"] = str(
                user["_id"]
            )

            session["username"] = user[
                "username"
            ]

            session["role"] = user[
                "role"
            ]

            if user["role"] == "admin":

                return redirect(
                    "/admin-dashboard"
                )

            return redirect(
                "/user-dashboard"
            )

    return render_template(
        "login.html"
    )


@user_bp.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        "/login"
    )


@user_bp.route(
    "/user-dashboard"
)
def user_dashboard():

    if (
        "user_id"
        not in session
    ):
        return redirect(
            "/login"
        )

    return render_template(
        "user_dashboard.html",
        username=session.get(
            "username",
            "User"
        )
    )


@user_bp.route(
    "/api/sell-energy",
    methods=["POST"]
)
def sell_energy():

    username = session.get(
        "username"
    )

    user = get_user_by_username(
        username
    )

    if not user:

        return jsonify(
            {
                "success": False,
                "message": "User not found"
            }
        )

    sell_amount = 50

    current_balance = float(
        user.get(
            "energy_balance",
            0
        )
    )

    if current_balance < sell_amount:

        return jsonify(
            {
                "success": False,
                "message": "Not enough energy"
            }
        )

    new_balance = (
        current_balance
        - sell_amount
    )

    current_revenue = float(
        user.get(
            "total_revenue",
            0
        )
    )

    earned = (
        sell_amount * 10
    )

    save_user_transaction(
        username,
        "Smart Grid",
        sell_amount,
        earned
    )

    update_energy_balance(
        username,
        new_balance
    )

    update_revenue(
        username,
        current_revenue + earned
    )

    blockchain = Blockchain()

    blockchain.add_block(
        {
            "type": "ENERGY_SALE",
            "user": username,
            "buyer": "Smart Grid",
            "energy": sell_amount,
            "revenue": earned
        }
    )

    save_block(
        blockchain.get_latest_block()
    )

    return jsonify(
        {
            "success": True,
            "balance": new_balance,
            "earned": earned
        }
    )


@user_bp.route(
    "/api/user/dashboard"
)
def user_dashboard_data():

    username = session.get(
        "username"
    )

    if not username:

        return jsonify(
            {
                "error": "Unauthorized"
            }
        ), 401

    user = get_user_by_username(
        username
    )

    if not user:

        return jsonify(
            {
                "error": "User not found"
            }
        ), 404

    energy_balance = float(
        user.get(
            "energy_balance",
            0
        )
    )

    return jsonify(
        {
            "energy_balance":
                energy_balance,

            "energy_generated":
                energy_balance + 275,

            "energy_consumed":
                275,

            "revenue":
                user.get(
                    "total_revenue",
                    0
                )
        }
    )


@user_bp.route(
    "/api/user/transactions"
)
def user_transactions():

    username = session.get(
        "username"
    )

    return jsonify(
        get_user_transactions(
            username
        )
    )
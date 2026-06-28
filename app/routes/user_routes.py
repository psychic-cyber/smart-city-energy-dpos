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
    update_revenue,
    vote_for_delegate,
    has_user_voted,
    get_all_users
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

from blockchain.storage.storage_manager import (
    save_blockchain
)

from database.mongodb.marketplace_repository import (
    get_available_listings,
    get_energy_requests
)

from app.services.energy_service import (
    create_marketplace_listing as create_listing_service,
    purchase_energy,
    submit_energy_request
)

from database.mongodb.energy_record_repository import (
    save_energy_record
)

from app.services.dpos_service import (
    cast_delegate_vote
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
            request.form["role"]
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

            if user["role"] == "Admin":

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

    save_blockchain(
        blockchain.chain
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
                user.get(
                    "energy_generated",
                    0
                ),

            "energy_consumed":
                user.get(
                    "energy_consumed",
                    0
                ),

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


@user_bp.route(
    "/marketplace"
)
def marketplace():

    if "user_id" not in session:

        return redirect(
            "/login"
        )

    return render_template(
        "marketplace.html"
    )


@user_bp.route(
    "/api/create-listing",
    methods=["POST"]
)
def create_marketplace_listing():

    username = session.get(
        "username"
    )

    data = request.get_json(silent=True) or {}
    success, message, result = create_listing_service(
        username, data.get("energy"), data.get("price")
    )
    return jsonify({"success": success, "message": message, "data": result})

@user_bp.route(
    "/api/marketplace"
)
def marketplace_data():

    return jsonify(
        get_available_listings()
    )

@user_bp.route(
    "/api/buy-energy",
    methods=["POST"]
)
def buy_energy():
    data = request.get_json(silent=True) or {}
    success, message, result = purchase_energy(
        session.get("username"), data.get("seller"), data.get("quantity")
    )
    return jsonify({"success": success, "message": message, "data": result})


@user_bp.route("/api/marketplace/requests", methods=["GET", "POST"])
def marketplace_requests():
    if request.method == "GET":
        return jsonify(get_energy_requests())

    data = request.get_json(silent=True) or {}
    success, message, result = submit_energy_request(
        session.get("username"),
        data.get("requested_energy"),
        data.get("maximum_price_per_kwh"),
        data.get("message"),
    )
    return jsonify({"success": success, "message": message, "data": result})

@user_bp.route(
    "/api/submit-energy",
    methods=["POST"]
)
def submit_energy():

    username = session.get(
        "username"
    )

    if not username:

        return jsonify(
            {
                "success": False
            }
        )

    data = request.get_json()

    generated = float(
        data.get(
            "generated",
            0
        )
    )

    consumed = float(
        data.get(
            "consumed",
            0
        )
    )

    save_energy_record(
        username,
        generated,
        consumed
    )

    return jsonify(
        {
            "success": True,
            "message":
                "Reading Submitted Successfully"
        }
    )

@user_bp.route(
    "/api/delegates"
)
def delegates():

    users = get_all_users()

    delegates = []

    for user in users:

        if user["role"] in [
            "Hospital",
            "University",
            "SolarFarm"
        ]:

            delegates.append(
                {
                    "username":
                        user["username"],

                    "role":
                        user["role"],

                    "votes":
                        user.get(
                            "votes",
                            0
                        )
                }
            )

    return jsonify(
        delegates
    )


@user_bp.route(
    "/api/vote",
    methods=["POST"]
)
def vote():

    voter = session.get(
        "username"
    )

    if not voter:
        return jsonify(
            {
                "success": False,
                "message": "Login Required"
            }
        )

    if has_user_voted(
        voter
    ):
        return jsonify(
            {
                "success": False,
                "message":
                    "You already voted"
            }
        )

    data = request.get_json()

    delegate = data[
        "delegate"
    ]

    success, message, validator = cast_delegate_vote(
        delegate
    )

    if not success:
        return jsonify(
            {
                "success": False,
                "message": message
            }
        )

    vote_for_delegate(
        voter,
        delegate
    )

    return jsonify(
        {
            "success": True,
            "message":
                message,
            "active_validator":
                validator["username"]
                if validator else None
        }
    )

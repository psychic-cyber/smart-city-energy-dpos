from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from app.controllers.user_controller import (
    register_controller,
    login_controller
)

user_bp = Blueprint(
    "users",
    __name__
)

@user_bp.route("/")
def home():

    if "user_id" in session:

        if session.get("role") == "admin":
            return redirect(
                "/admin-dashboard"
            )

        return redirect(
            "/user-dashboard"
        )

    return redirect(
        "/login"
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

            else:

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
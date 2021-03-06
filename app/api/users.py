from flask import jsonify, request, url_for
from app.api import bp
from app.models import User
from app import db
from app.api.errors import bad_request

@bp.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route("/users", methods=["GET"])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_age', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route("/users/<int:id>/followers", methods=["GET"])
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page, 'api.get_followers', id=id)
    return jsonify(data)


@bp.route("/users/<int:id>/following", methods=["GET"])
def get_following(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page, 'api.get_following', id=id)
    return jsonify(data)


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    if "username" not in data or "email" not in data or "password" not in data:
        return bad_request("Must Include POST data")
    if User.query.filter_by(username=data["username"]).first():
        return bad_request("Please use a different username")
    if User.query.filter_by(email=data["email"]).first():
        return bad_request("Please use a different email")
    
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for('api.get_user', id=user.id)
    return response


@bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if "username" in data and data["username"] != user.username and User.query.filter_by(username=data["username"]).first():
        return bad_request("Please use a different username")
    if "email" in data and data["email"] != user.email and User.query.filter_by(email=data["email"]).first():
        return bad_request("Please use a different email")
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
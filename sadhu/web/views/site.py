from flask import Blueprint, render_template, current_app

module = Blueprint('site', __name__)

@module.route('/')
def index():
    return render_template('/site/index.html')

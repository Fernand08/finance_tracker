from datetime import datetime, timedelta
from flask import render_template, request, Response
from app import app, db
from app.models import Movement


def get_balance(movements):
    incomes = sum(
        [m.amount for m in movements if m.movement_type == 'incomes'])
    expenses = sum(
        [m.amount for m in movements if m.movement_type == 'expenses'])
    balance = incomes - expenses
    return balance


@app.template_filter()
def format_date(value, format='%m/%d/%Y'):
    if not value:
        return ""
    return value.strftime(format)


@app.template_filter()
def format_currency(value):
    if not value:
        return ""
    return '$ {:.2f}'.format(value)


@app.template_filter()
def format_number(value):
    if not value:
        return ""
    return '{:.2f}'.format(value)


@app.route("/", methods=['GET'])
def home():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    movements = db.session.query(Movement).filter(
        Movement.movement_date.between(start_date, end_date)).all()
    balance = get_balance(movements)

    return render_template('index.html',
                           movements=movements,
                           balance=balance,
                           start_date=start_date,
                           end_date=end_date,
                           movement_type='all')


@app.route("/filter-movements", methods=["GET"])
def filter_movements():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    description = request.args.get("description")
    movement_type = request.args.get("movement_type")

    query = db.session.query(Movement)

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Movement.movement_date >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Movement.movement_date <= end_date)

    if description:
        query = query.filter(Movement.description.like(f'%{description}%'))

    if movement_type != 'all':
        query = query.filter(Movement.movement_type == movement_type)

    movements = query.all()
    balance = get_balance(movements)

    return render_template('movement_list.html', movements=movements, balance=balance)


@app.route("/empty-filter", methods=["GET"])
def empty_filter():
    return render_template('movement_filter.html')


@app.route("/submit", methods=['POST'])
def submit_movement():

    description = request.form["description"]
    amount = request.form["amount"]
    movement_type = request.form["movement_type"]
    movement_date = request.form["movement_date"]

    movement = Movement(
        description=description,
        amount=amount,
        movement_type=movement_type,
        movement_date=datetime.strptime(movement_date, '%Y-%m-%d')
    )

    db.session.add(movement)
    db.session.commit()

    return render_template('movement_card.html', movement=movement)


@app.route("/create-movement-form", methods=["GET"])
def get_create_movement_form():
    movement = Movement(description="")

    return render_template('new_movement_modal.html', movement=movement)


@app.route("/edit-movement-form/<int:id>", methods=["GET"])
def get_movement_form(id):
    movement = Movement.query.get(id)

    return render_template('edit_movement_modal.html', movement=movement)


@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_movement(id):
    movement = Movement.query.get(id)
    db.session.delete(movement)
    db.session.commit()

    return ""


@app.route("/update/<int:id>", methods=["PUT"])
def update_movement(id):

    db.session.query(Movement).filter(Movement.id == id).update({
        'description': request.form["description"],
        'amount': request.form["amount"],
        'movement_type': request.form["movement_type"],
        'movement_date': datetime.strptime(request.form["movement_date"], '%Y-%m-%d'),
    })
    db.session.commit()

    movement = Movement.query.get(id)

    return render_template('movement_card.html', movement=movement)


@app.route("/validate/description", methods=["POST"])
def validate_description():
    description = request.form["description"]

    if not description:
        return render_template('description_field.html', description=description,
                               error='A description is required')

    if len(description) < 5:
        return render_template('description_field.html', description=description,
                               error='Description must be at least 5 characters long')

    return render_template('description_field.html', description=description)


@app.route("/validate/amount", methods=["POST"])
def validate_amount():
    amount = request.form["amount"]

    if not amount:
        return render_template('amount_field.html', amount=amount,
                               error="An amount is required")

    amount = float(amount)

    if amount < 0:
        return render_template('amount_field.html', amount=amount,
                               error="The amount cannot be negative")

    if amount > 45000:
        return render_template('amount_field.html', amount=amount,
                               error="The amount cannot greather than 45000")

    return render_template('amount_field.html', amount=amount)


@app.route("/validate/movement-date", methods=["POST"])
def validate_movement_date():
    movement_date = request.form["movement_date"]

    if not movement_date:
        return render_template('movement_date_field.html', movement_date=movement_date,
                               error='Movement date is required')

    movement_date = datetime.strptime(movement_date, '%Y-%m-%d')

    if movement_date >= datetime.now():
        return render_template('movement_date_field.html', movement_date=movement_date,
                               error='Movement date cannot be grether than today')

    return render_template('movement_date_field.html', movement_date=movement_date)

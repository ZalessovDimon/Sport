from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from models import db, Client, Admin, Coach, Participation, Training, Occupancy, Payment
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2612@localhost/sport'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Функция для загрузки пользователей
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id) or Client.query.get(user_id) or Coach.query.get(user_id)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    if role == 'admin':
        return redirect(url_for('login_admin'))  # Перенаправление на страницу для входа админа
    elif role == 'client':
        return redirect(url_for('login_client'))  # Перенаправление на страницу для входа клиента
    elif role == 'coach':
        return redirect(url_for('login_coach'))  # Перенаправление на страницу для входа тренера

# Страница входа для admin
@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Логика для проверки админа
        return redirect(url_for('admin_dashboard'))  # Например, переход на панель администратора
    return render_template('login_admin.html')

# Страница входа для клиента
@app.route('/login/client', methods=['GET', 'POST'])
def login_client():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Логика для проверки клиента
        return redirect(url_for('client_dashboard'))  # Например, переход на панель клиента
    return render_template('login_client.html')


# Страница входа для тренера
@app.route('/login/coach', methods=['GET', 'POST'])
def login_coach():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Логика для проверки тренера
        return redirect(url_for('coach_dashboard'))  # Например, переход на панель тренера
    return render_template('login_coach.html')

# Панель администратора
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Управление клиентами (администратор)
@app.route('/admin/manage_clients', methods=['GET'])
def manage_clients():
    # Логика получения клиентов
    clients = Client.query.all()  # Получение данных из базы
    return render_template('manage_clients.html', clients=clients)

# Управление тренерами (администратор)
@app.route('/admin/manage_coaches', methods=['GET'])
def manage_coaches():
    # Логика получения тренеров
    coaches = Coach.query.all()  # Получение данных из базы
    return render_template('manage_coaches.html', coaches=coaches)

# Управление заполняемостью тренировок (администратор)
@app.route('/admin/manage_occupancies', methods=['GET'])
def manage_occupancies():
    # Логика получения данных о занятиях
    occupancies = Occupancy.query.all()  # Получение данных из базы
    return render_template('manage_occupancies.html', occupancies=occupancies)

# Управление участием (администратор)
@app.route('/admin/manage_participations', methods=['GET'])
def manage_participations():
    # Логика получения данных об участиях
    participations = Participation.query.all()  # Получение данных из базы
    return render_template('manage_participations.html', participations=participations)

# Управление платежами (администратор)
@app.route('/admin/manage_payments', methods=['GET'])
def manage_payments():
    # Логика получения данных о платежах
    payments = Payment.query.all()  # Получение данных из базы
    return render_template('manage_payments.html', payments=payments)

# Управление тренировками (администратор)
@app.route('/admin/manage_trainings', methods=['GET', 'POST'])
@login_required
def manage_trainings_admin():
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    trainings = Training.query.all()
    return render_template('manage_trainings.html', trainings=trainings)

# Добавление записи
@app.route('/admin/add/<string:table>', methods=['POST'])
@login_required
def add_entry(table):
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))

    if table == 'clients':
        client = Client(
            username=request.form['username'],
            password=request.form['password'],
            name=request.form['name'],
            phone_number=request.form['phone_number'],
            email=request.form['email'],
            address=request.form['address']
        )
        db.session.add(client)

    elif table == 'trainings':
        training = Training(
            name=request.form['name'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            location=request.form['location'],
            id_coach=request.form['id_coach']
        )
        db.session.add(training)

    db.session.commit()
    flash(f"Entry added to {table} successfully!", 'success')
    return redirect(url_for('admin_dashboard'))

# Удаление записи
@app.route('/admin/delete/<string:table>/<int:id>', methods=['POST'])
@login_required
def delete_entry(table, id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))

    if table == 'clients':
        entry = Client.query.get_or_404(id)
    elif table == 'trainings':
        entry = Training.query.get_or_404(id)
    else:
        flash(f"Invalid table {table}", 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(entry)
    db.session.commit()
    flash(f"Entry deleted from {table} successfully!", 'success')
    return redirect(url_for('admin_dashboard'))

# Редактирование записи
@app.route('/admin/edit/<string:table>/<int:id>', methods=['POST'])
@login_required
def edit_entry(table, id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))

    if table == 'clients':
        entry = Client.query.get_or_404(id)
        entry.username = request.form['username']
        entry.name = request.form['name']
        entry.phone_number = request.form['phone_number']
        entry.email = request.form['email']
        entry.address = request.form['address']

    elif table == 'trainings':
        entry = Training.query.get_or_404(id)
        entry.name = request.form['name']
        entry.start_date = request.form['start_date']
        entry.end_date = request.form['end_date']
        entry.location = request.form['location']
        entry.id_coach = request.form['id_coach']

    db.session.commit()
    flash(f"Entry in {table} updated successfully!", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        birth_date = request.form['birth_date']
        phone_number = request.form['phone_number']
        email = request.form['email']
        address = request.form['address']

        # Добавление нового клиента в базу данных (пример)
        new_client = Client(username=username, name=name, birth_date=birth_date,
                            phone_number=phone_number, email=email, address=address)
        db.session.add(new_client)
        db.session.commit()

        flash('Клиент успешно добавлен!', 'success')
        return redirect(url_for('manage_clients'))  # Перенаправление на страницу управления клиентами
    return render_template('add_client.html')

# Панель клиента
@app.route('/client_dashboard')
def client_dashboard():
    return render_template('client_dashboard.html')

# Панель тренера
@app.route('/coach_dashboard')
def coach_dashboard():
    return render_template('coach_dashboard.html')

# Регистрация клиента
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        client = Client(
            username=request.form['username'],
            password=request.form['password']
        )
        db.session.add(client)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login_client'))
    return render_template('register.html')

@app.route('/client/payments')
def client_payments():
    # Use SQLAlchemy to query payments
    payments = Payment.query.all()

    # Passing the results to the template
    return render_template('client_payments.html', payments=payments)


@app.route('/client_trainings')
def client_trainings():
    # Получаем данные о тренировках из базы данных
    trainings = db.session.query(Training).all()  # Пример запроса в базу данных
    return render_template('client_trainings.html', trainings=trainings)


@app.route('/client_occupancy')
def client_occupancy():
    # Получаем данные о занятости из базы данных
    occupancies = db.session.query(Occupancy).all()  # Пример запроса в базу данных
    return render_template('client_occupancy.html', occupancies=occupancies)

@app.route('/coach/trainings')
def coach_trainings():
    # Получаем все тренировки, не фильтруя по тренеру
    coach_trainings = Training.query.all()  # Все тренировки
    return render_template('coach_trainings.html', trainings=coach_trainings)

@app.route('/coach/occupancy')
def coach_occupancy():
    # Получаем все записи из таблицы occupancy
    coach_occupancy_data = Occupancy.query.all()  # Загружаем все записи
    return render_template('coach_occupancy.html', occupancy=coach_occupancy_data)

@app.route('/coach/payments')
def coach_payments():
    # Получаем все платежи из базы данных
    payments = Payment.query.all()  # Предполагаем, что у вас есть модель Payment для таблицы payments
    return render_template('coach_payments.html', payments=payments)

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
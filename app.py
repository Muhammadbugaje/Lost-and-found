from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, ItemForm, ClaimForm
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost_and_found.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'Uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
csrf = CSRFProtect(app) 


@app.context_processor
def utility_processor():
    def csrf_token():
        from flask_wtf.csrf import generate_csrf
        return generate_csrf()
    return dict(csrf_token=csrf_token)

# ... (other code: models, routes like home, claimed_items, admin_items, etc.)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    found_location = db.Column(db.String(100), nullable=False)
    take_from_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='found')
    image = db.Column(db.String(100))
    claims = db.relationship('Claim', backref='item', lazy=True)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    search = request.args.get('search', '')
    items = LostItem.query.filter(
        LostItem.status == 'found',
        or_(
            LostItem.name.ilike(f'%{search}%'),
            LostItem.category.ilike(f'%{search}%')
        )
    ).all()
    return render_template('index.html', items=items)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@me.com',
            password_hash=generate_password_hash('password')
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('admin_items'))
        else:
            flash('Invalid username or password')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/admin/items')
@login_required
def admin_items():
    items = LostItem.query.filter_by(status='found').all()
    return render_template('admin/items.html', items=items)

@app.route('/admin/add-item', methods=['GET', 'POST'])
@login_required
def admin_add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = LostItem(
            name=form.name.data,
            category=form.category.data,  # Fixed typo from previous version
            description=form.description.data,
            found_location=form.found_location.data,
            take_from_location=form.take_from_location.data,
            status='found'
        )
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!')
        return redirect(url_for('admin_items'))
    return render_template('admin/add_item.html', form=form)

@app.route('/admin/edit-item/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_item(id):
    item = LostItem.query.get_or_404(id)
    form = ItemForm()
    if form.validate_on_submit():
        item.name = form.name.data
        item.category = form.category.data
        item.description = form.description.data
        item.found_location = form.found_location.data
        item.take_from_location = form.take_from_location.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename
        db.session.commit()
        flash('Item updated successfully!')
        return redirect(url_for('admin_items'))
    form.name.data = item.name
    form.category.data = item.category
    form.description.data = item.description
    form.found_location.data = item.found_location
    form.take_from_location.data = item.take_from_location
    return render_template('admin/edit_item.html', form=form, item=item)


@app.route('/admin/claim/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_claim_item(id):
    item = LostItem.query.get_or_404(id)
    if item.status != 'found':
        flash('Item is already claimed')
        return redirect(url_for('admin_items'))
    form = ClaimForm()
    if form.validate_on_submit():
        claim = Claim(
            item_id=item.id,
            name=form.name.data,
            reg_number=form.reg_number.data,
            phone=form.phone.data
        )
        item.status = 'claimed'
        db.session.add(claim)
        db.session.commit()
        flash('Item claimed successfully!')
        return redirect(url_for('admin_items'))
    return render_template('admin/claim.html', form=form, item=item)


@app.route('/item/<int:id>')
def item_detail(id):
    item = LostItem.query.get_or_404(id)
    return render_template('item_detail.html', item=item)

@app.route('/migrate-categories')
def migrate_categories():
    items = LostItem.query.all()
    valid_categories = ['Personal', 'Phone', 'Clothing', 'Books', 'Other', 'ID', 'Finance', 'wearables']
    for item in items:
        if item.category not in valid_categories:
            item.category = 'Other'  # Fallback
    db.session.commit()
    flash('Categories migrated!', 'success')
    return redirect(url_for('admin_items'))

@app.route('/claimed-items', methods=['GET', 'POST'])
def claimed_items():
    search = request.args.get('search', '')
    claimed_items = LostItem.query.filter(
        LostItem.status == 'claimed',
        or_(
            LostItem.name.ilike(f'%{search}%'),
            LostItem.category.ilike(f'%{search}%')
        )
    ).all()
    items_with_claims = []
    for item in claimed_items:
        claim = Claim.query.filter_by(item_id=item.id).first()
        if claim:
            items_with_claims.append((item, claim))
    return render_template('claimed_items.html', items_with_claims=items_with_claims)

@app.route('/delete-claim/<int:id>', methods=['POST'])
@login_required
def delete_claim(id):
    claim = Claim.query.get_or_404(id)
    item = LostItem.query.get_or_404(claim.item_id)
    item.status = 'found'
    db.session.delete(claim)
    db.session.commit()
    flash('Claim deleted successfully!', 'success')
    return redirect(url_for('claimed_items'))

@app.route('/admin/delete-item/<int:id>', methods=['POST'])
@login_required
def admin_delete_item(id):
    item = LostItem.query.get_or_404(id)
    if item.claims:
        flash('Cannot delete item with active claims.', 'error')
        return redirect(url_for('admin_items'))
    if item.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('admin_items'))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
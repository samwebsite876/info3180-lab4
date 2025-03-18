import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.photo.data
        filename = secure_filename(file.filename)  # Sanitize the filename

        # Debug: Print the original and secure filenames
        print(f"Original filename: {file.filename}, Secure filename: {filename}")

        # Save the file to the uploads folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File uploaded successfully!', 'success')
        return redirect(url_for('home'))

    flash_errors(form)
    return render_template('upload.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # Validate the entire form submission
    if form.validate_on_submit():
        # Get the username and password values from the form
        username = form.username.data
        password = form.password.data

        # Query the database for a user with the submitted username
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            # Log the user in
            login_user(user)

            # Flash a success message
            flash('Login successful!', 'success')

            # Redirect the user to the upload route
            return redirect(url_for('upload'))
        else:
            # Flash an error message if login fails
            flash('Invalid username or password', 'danger')

    # Flash form errors if validation fails
    flash_errors(form)

    # Render the login template with the form
    return render_template("login.html", form=form)

def get_uploaded_images():
    # Get the path to the uploads folder
    upload_folder = app.config['UPLOAD_FOLDER']
    # List all files in the uploads folder
    image_files = []
    for filename in os.listdir(upload_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.tiff', '.bmp', '.webp', '.heif', '.heic')):  # Only include image files
            image_files.append(filename)
    return image_files

@app.route('/uploads/<filename>')
def get_image(filename):
    # Serve the requested file from the uploads folder
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

@app.route('/files')
@login_required  # Ensure only logged-in users can access this route
def files():
    # Get the list of uploaded images
    image_files = get_uploaded_images()
    # Render the files.html template with the list of images
    return render_template('files.html', image_files=image_files)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
@login_required  # Ensure only logged-in users can access this route
def logout():
    # Log the user out
    logout_user()
    # Flash a message to the user
    flash('You have been logged out.', 'success')
    # Redirect the user to the home route
    return redirect(url_for('home'))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

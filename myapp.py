import sqlite3
from ssl import AlertDescription
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    conn = sqlite3.connect('recipedatabase.db')
    conn.row_factory = sqlite3.Row
    return conn
def wait_db_connection():
    conct = sqlite3.connect('waitlistdatabase.db')
    conct.row_factory = sqlite3.Row
    return conct

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        useremail = request.form['email']
        userpassword = request.form['password']

        conn = get_db_connection()

        # Check if the email or password already exists in the database
        result = conn.execute('SELECT * FROM loggedUsers WHERE useremail = ? OR userpassword = ?', (useremail, userpassword))
        existing_user = result.fetchone()

        if existing_user:
            # Email or password already registered, display error message
            flash('Email or password already registered!', 'error')
            conn.close()
            return redirect(url_for('register'))
        else:
            # Register the new user
            result = conn.execute('INSERT INTO loggedUsers (useremail, userpassword) VALUES (?, ?)', (useremail, userpassword))
            conn.commit()
            conn.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        

    return render_template('register.html')

@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        useremail = request.form['email']
        userpassword = request.form['password']
  
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM loggedUsers WHERE useremail = ? AND userpassword = ?',
                            (useremail, userpassword)).fetchone()
        conn.close()

        if user:
            if useremail == 'ogolasospeter62@gmail.com' and userpassword == 'admin' or useremail == 'captainsos483@gmail.com' and userpassword == 'Admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
           
            # User credentials are correct, redirect to the main page
            # flash('Login successful!')
            
        else:
            flash('Invalid email or password!')
            return redirect(url_for('login'))

    return render_template('login.html')
###############################################################################
#admin function routings
@app.route('/admin')
def admin():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('adminPages/adminIndex.html', posts = posts)


def admin_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM recipes WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/<int:post_id>/adminpost')
def adminpost(post_id):
    post = admin_post(post_id)
    return render_template('adminPages/adminPost.html', post=post)

@app.route('/<int:id>/delete', methods=('POST','GET'))
def delete(id):
    post = wait_item(id)
    conct = wait_db_connection()
    conct.execute('DELETE FROM awaitrecipes WHERE id = ?', (id,))
    conct.commit()
    conct.close()
    flash('"{}" was successfully deleted!'.format(post['rname']), 'success')
    return redirect(url_for('admin'))


@app.route('/<int:post_id>/main_delete', methods=('POST','GET'))
def main_delete(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('"{}" of category {} was successfully deleted!'.format(post['rname'], post['rcategory']), 'success')
    return redirect(url_for('admin'))


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        image = request.form['rimage']
        name = request.form['rname']
        category = request.form['rcategory']
        description = request.form['description']
        ingredients = request.form['ingredient']
        procedure = request.form['procedure']
        img1 = request.form['img1']
        img2 = request.form['img2']
        img3 = request.form['img3']

        conn = get_db_connection()
        conn.execute('UPDATE recipes SET  rname = ?, rcategory = ?, rimage = ?, rdescription = ?, ringredients = ?, rprocedure = ?, image1 = ?, image2 = ?, image3 = ? WHERE id = ?',(name,category,image,description,ingredients,procedure,img1,img2,img3, id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))


    return render_template('adminPages/adminEdit.html', post=post)



# @app.route('/await_list')
# def await_list():
#     conct = wait_db_connection()
#     waitposts = conct.execute('SELECT * FROM awaitrecipes').fetchall()
#     conct.close()
#     if waitposts is None:
#         return render_template('error.html')
#     return render_template('adminPages/awaitList.html',waitposts=waitposts)

@app.route('/await_list')
def await_list():
    conct = wait_db_connection()
    waitposts = conct.execute('SELECT * FROM awaitrecipes').fetchall()
    conct.close()
    if len(waitposts) == 0:  # Check if the list is empty
        return render_template('error.html')
    return render_template('adminPages/awaitList.html', waitposts=waitposts)


def wait_item(item):
    conct = wait_db_connection()
    itm= conct.execute('SELECT * FROM awaitrecipes WHERE id = ?',(item,)).fetchone()
    conct.close()
    if itm is None:
        abort(404)
    return itm

# @app.route('/<int:item>/itm', methods=('GET', 'POST'))
# def itm(item):
#     itm = wait_item(item)

#     if request.method == 'POST':
#         image = itm['rimage']
#         name = itm['rname']
#         category = itm['rcategory']
#         description = itm['rdescription']
#         ingredients = itm['ringredients']
#         procedure = itm['rprocedure']
#         img1 = itm['image1']
#         img2 = itm['image2']
#         img3 = itm['image3']

@app.route('/<int:item>/itm', methods=('GET', 'POST'))
def itm(item):
    itm = wait_item(item)

    if request.method == 'POST':
        image = request.form['rimage']
        name = request.form['rname']
        category = request.form['rcategory']
        description = request.form['rdescription']
        ingredients = request.form['ringredients']
        procedure = request.form['rprocedure']
        img1 = request.form['img1']
        img2 = request.form['img2']
        img3 = request.form['img3']

        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (rname, rcategory, rimage, rdescription, ringredients, rprocedure, image1, image2, image3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (name, category, image, description, ingredients, procedure, img1, img2, img3))
        conn.commit()
        conn.close()
        flash('"{}" recipe was successfully added!'.format(name))
        delete(itm['id'])
        return redirect(url_for('admin'))

    return render_template('adminPages/viewWaitList.html', itm=itm)


#####################################################################################################
#users
#######################################################################


######################################################################

@app.route('/about')
def about():
    return render_template('about_us.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/breakfast')
def breakfast():
    return render_template('breakfast.html')

@app.route('/lunch')
def lunch():
    return render_template('lunch.html')

@app.route('/dinner')
def dinner():
    return render_template('dinner.html')

@app.route('/salad')
def salad():
    return render_template('salads.html')

@app.route('/index')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('index.html', posts = posts)

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM recipes WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/<int:post_id>/post')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


def get_moduled_post(post_cat):
    conn = get_db_connection()
    cats = conn.execute('SELECT * FROM recipes WHERE rcategory = ?',
                        (post_cat,)).fetchall()
    conn.close()
    if cats is None:
        abort(404)
    return cats

@app.route('/moduled_cat/<post_cat>')
def moduled_cat(post_cat):
    cats = get_moduled_post(post_cat)
    return render_template('moduled.html',cats=cats,post_cat=post_cat)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        rimage = request.form['rimage']
        img1 = request.form['img1']
        img2 = request.form['img2']
        img3 = request.form['img3']

        rname = request.form['rname']
        category = request.form['rcategory']
        description = request.form['description']
        ingredients = request.form['ingredient']
        procedure = request.form['procedure']

        con = wait_db_connection()
        con.execute('INSERT INTO awaitrecipes (rname,rcategory,rimage,rdescription,ringredients,rprocedure,image1,image2,image3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (rname,category,rimage,description,ingredients,procedure,img1,img2,img3))
        con.commit()
        con.close()
        return redirect(url_for('index'))

            

    return render_template('create.html')



@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    # Perform the search logic here based on the search_term
    conn = get_db_connection()
    search_results = conn.execute('SELECT * FROM recipes WHERE rname = ?',
                        (search_term)).fetchall()
    conn.close()

    return {'results': search_results}
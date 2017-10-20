from flask import Flask, request, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogz:blogz@localhost:8889/blogz'

app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "2292sarvani2292"


db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
      
    blogs = db.relationship('Blog',backref='userid')

    def __init__(self,username,password):
        self.username = username
        self.password = password


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title, body,userid):
        self.title = title
        self.body = body
        self.userid = userid
        




#TODO -create a required_login fun for session 
#TODO-and the allowed routed to login,signup,blog(where all users are displayed),main-blog(where all blogs displayed),
#except for newpost.then redirect to newpost if username is in session. 
@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','index_page']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/main-blog', methods=['POST','GET'])
def index():
    
    #here i m displaying all the blogs or just a single blog we clicked
    current_user = request.args.get('user')
    blog_id = request.args.get('id')
    user_blogs1 = Blog.query.join(User).add_columns(Blog.id,Blog.title,Blog.body,User.username).filter(Blog.user_id==User.id).all()
    
    
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template("new-post.html",blog = blog)


    if current_user:
        current_userid = User.query.filter_by(username=current_user).first()
        c_userid = (current_userid.id) 
        #user_blogid = Blog.query.filter_by(user_id=c_userid).first()
        #u_blogid = str(user_blogid.id)
        user_blogs = Blog.query.filter_by(user_id=c_userid).all()
        return render_template("singleuser.html",blogs=user_blogs,user_name=current_user,
        heading="Blog posts")         
    else:
        blogs = Blog.query.all()
        #blog_user = User.query.filter_by().get()
        return render_template("blog-posts.html",blogs=user_blogs1,
        heading="Blog posts")
    
        
        
@app.route('/new-post', methods=['POST','GET'])
def new_post():
    #here i m displaying a form to write a new blog post
    #TODO-when clicked on th newpost link they should be asked to login first if not logged in
    #if logged in rendertemplate to the forms(todos.html)
    #else redirect to /login
    return render_template('todos.html',heading="New post")

@app.route('/new-blog', methods=['POST','GET'])
def new_blog():
    #here if both title and body of the blog are not empty 
    #then its placing values in database and redirecting to the mainblog 
    #where a single blog is printed as id is sent along with it
    #TODO- if new blog post is posted then display author name i.e., the username along with it
    error_title =""
    error_body=""
       
    if request.method == 'GET':
                
        title_name = request.args.get('title')
        body_name = request.args.get('body')
                 

        if title_name == "":
            error_title ="Please fill in the title"
        if body_name == "":
            error_body = "Please fill int the content"

        if not error_title and not error_body:
            userid = User.query.filter_by(username=session['username']).first()
            new_body = Blog(title_name, body_name,userid)
            db.session.add(new_body)
            db.session.commit()
            new_title = Blog.query.filter_by(title=title_name).first() 
            blog_id = new_title.id
            return redirect('/main-blog?id={0}'.format(blog_id))
            #return render_template("new-post.html",blog=new_body)
        else:
            return render_template('todos.html',heading="New post",error_title=error_title,error_body=error_body)

        
@app.route('/signup',methods=['POST','GET'])
def signup():
    #TODO-if the given username is already in database then tell them to enter a newone or go and login
    #else take the username and password and place them in database
    #'remember' the user
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        error_name =""
        error_password = ""
        error_pass_same = ""
        password1=""

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
                error_name = "A user with this username already exists"
        if not existing_user:
            
            #now take the details and put them in database
            if username == "":
                error_name = "Please enter a username"
            if password == "":
                error_password = "Please enter a password"
            if len(password) <3 or len(password)>20:
                error_password = "Not a valid password"
            if verify == ""or password != verify:
                error_pass_same="passwords din't match"
            if len(username) < 3 or len(username) >20:
                error_name = "Not a valid username"
            
            #TODO- tell the user that this username already exists in a better way than this
            
            
            #if not error then this block
            if not error_name and not error_password and not error_pass_same:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                #TODO-remember the user
                session['username']= username
            #redirect to the page where all the tasks of this particular user are displayed.
                return redirect('/new-post')
            
        return render_template('signup.html',heading="signup",error_name=error_name,error_password=error_password,error_pass_same=error_pass_same)
                      
           

    return render_template('signup.html',heading="signup")

@app.route('/login',methods=['POST','GET'])
def login():
    #TODO-check if the username and password given in this login page are already ther in database
    #if not then 'remember' the user(using sessions) 
    #then redirect to the new post page
    #if user doesnt exist ask them to signup.and also tell their errors
    username_error = ""
    password_error =""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        loggedin_user = User.query.filter_by(username=username).first()
       
        if loggedin_user and loggedin_user.password == password:
            #user is logged in and remember user using sessions
            session['username']= username
            #now redirect user to newpost page
            return redirect("/new-post")
        else:
            #TODO- write errors.
            #for now just displaying login page without errors.
            username_table = User.query.get(username)
            password_table = User.query.get(password)
            if password == "" or password != password_table:
                password_error = "Please enter the correct password"
            if username == "" and username != username_table:
                username_error = "Invalid Username"
            
            return render_template('login.html',heading="login",username_error=username_error,password_error=password_error)

    #this return to display a login page first        
    return render_template('login.html',heading="login")

@app.route('/')        
def index_page():
    #TODO-index page should display all the usernames(blog users).
    allusers = User.query.all()
    return render_template('index.html',allusers=allusers,heading="Blog Users")

#@app.route('/usersblogs')
#def users_blogs():
    #TODO-display all the blogs of a particular user
    #before when a particular blog is clicked we displayed that blog using get and sending id init
    #now along with that we a username is clicked we need to send to the blog posts of that user using get and username    

@app.route('/logout')
def logout():
    #TODO redirect to the page where all the blogs from all the users are displayed
    #also delete the username from the session
    del session['username']
    #return redirect()
    return redirect('/main-blog')

if __name__ == '__main__':
    app.run()
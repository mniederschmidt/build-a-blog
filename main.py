import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):

	# These three functions are useful for rendering basic templates
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		# returns a string (rendered from template)
		return t.render(params)

	def render(self, template, **kw):
		# calls render_str but wraps it in a write to send it back to the browser
		self.write(self.render_str(template, **kw))

	def renderError(self, error_code):
		self.error(error_code)
		if error_code == 404:
			self.write("That record was not found.")
		else:
			self.write("Oops! Something went wrong.")

class Post(db.Model):
	title = db.StringProperty(required = True)
	text = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

	def get(self):
		self.redirect("/blog")

class BlogList(Handler):
	def render_list(self):
		posts = db.GqlQuery("SELECT * FROM Post "
						   "ORDER BY created DESC "
						   "LIMIT 5")

		self.render("main.html", posts=posts)

	def get(self):
		self.render_list()

class ViewPostHandler(Handler):
	def render_post(self, id=""):
		post = Post.get_by_id(int(id))

		if not post:
			self.renderError(404)
			return

		self.render("viewpost.html", title=post.title, text=post.text)

	def get(self, id):
		self.render_post(id)
		#self.response.write(id)

class AddPost(Handler):

	def render_newpost(self, title="", text="", error=""):
		self.render("newpost.html", title=title, text=text, error=error)	

	def get(self):
		self.render_newpost()

	def post(self):
		title = self.request.get("title")
		text = self.request.get("text")

		if title and text:
			p = Post(title = title, text = text)
			p.put()
			# Need to add a wait for record to update?
			self.redirect("/blog/{id}".format(id=p.key().id()))
		else:
			error = "Please enter both a title and some text"
			self.render_newpost(title, text, error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogList),
    ('/newpost', AddPost),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)    
], debug=True)

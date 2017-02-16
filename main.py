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

class Post(db.Model):
	title = db.StringProperty(required = True)
	text = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

	def get(self):
		self.redirect("/blog")

class BlogList(Handler):
	def render_list(self, title="", text="", error=""):
		posts = db.GqlQuery("SELECT * FROM Post "
						   "ORDER BY created DESC "
						   "LIMIT 5")

		self.render("main.html", posts=posts)

	def get(self):
		self.render_list()

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
			self.redirect("/")
		else:
			error = "Please enter both a title and some text"
			self.render_newpost(title, text, error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogList),
    ('/newpost', AddPost),
], debug=True)

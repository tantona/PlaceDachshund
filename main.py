from ResizedImage import ResizedImage
import tornado.ioloop
import tornado.web
import os

class ReturnImage(tornado.web.RequestHandler):
	def get(self,x,y):
		self.options = {'x' : x, 'y' : y}
		self.new_image = ResizedImage()
		self.buf = self.new_image.get_image(self.options)
		self.write( self.buf.getvalue() )

		self.set_header("Content-Type", 'image/png')
		self.set_header("Content-Disposition", "inline")

class HomePageHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("index.html")
            
application = tornado.web.Application([
    (r"/([0-9]+)/([0-9]+)", ReturnImage),
   	(r"/",HomePageHandler)
],
template_path=os.path.join(os.path.dirname(__file__), "templates"),
static_path=os.path.join(os.path.dirname(__file__), "static")
)

port = 8888

if __name__ == "__main__":
	 
    application.listen(port)
    print "App Server started at http://localhost:"+str(port)
    tornado.ioloop.IOLoop.instance().start()
   
from PIL import Image
from random import randrange
from pymongo import MongoClient
import base64
import cStringIO

class ResizedImage():
	def get_image_size(self,x,y):
		x = float(x)
		y = float(y)

		if x / y >= 1.33:
			return 'landscape'
		elif x / y <= 0.75: 
			return 'portrait'
		else:
			return 'square'

	def get_image_coords(self,options):
		
		self.resize_spec = {
			'new_image_size' : (0,0),
			'crop_coords' : (0,0,0,0)
		}

		if options['size'] == 'portrait':
			self.resize_spec['new_image_size'] = ( \
				int( float(self.image.size[0]) / float(self.image.size[1]) * int(options['y'])), \
				int(options['y']) \
				)

			self.resize_spec['crop_coords'] = ( \
					((self.resize_spec['new_image_size'][0] - int(options['x']) ) // 2), \
					0, \
					(self.resize_spec['new_image_size'][0] - int(options['x']) ) // 2 + int(options['x']), \
					int(options['y'])
				)
			
		elif options['size'] == 'landscape':
			self.resize_spec['new_image_size'] = (
				int(options['x']), \
				int( int(options['x']) // (float(self.image.size[0]) / float(self.image.size[1]))) \
				)

			self.resize_spec['crop_coords'] = ( \
					0,
					((self.resize_spec['new_image_size'][1] - int(options['y']) ) // 2), \
					int(options['x']), \
					(self.resize_spec['new_image_size'][1] - int(options['y']) ) // 2 + int(options['y']), \
				)
		else:
			self.larger_dim = int(options['x']) if int(options['x']) > int(options['y']) else int(options['y'])
			self.smaller_dim = int(options['x']) if int(options['x']) < int(options['y']) else int(options['y'])
			
			self.resize_spec['new_image_size'] = (
				self.larger_dim, \
				self.larger_dim \
				)
			
			if int(options['x']) >= int(options['y']):
				self.resize_spec['crop_coords'] = ( \
						0, \
						(int(options['x']) - int(options['y'])) // 2, \
						int(options['x']), \
						((int(options['x']) - int(options['y'])) // 2) + int(options['y']) \
					)
			else:
				self.resize_spec['crop_coords'] = ( \
						(int(options['y']) - int(options['x'])) // 2, \
						0, \
						((int(options['y']) - int(options['x'])) // 2) + int(options['x']), \
						int(options['y']), \
					)

	def resize_image(self,options):
		self.jpeg_image_buffer = cStringIO.StringIO()
		self.image_string = cStringIO.StringIO(base64.b64decode(options['image']))
		self.image = Image.open(self.image_string)

		self.get_image_coords(options)

		self.image = self.image \
			.resize(self.resize_spec['new_image_size'],resample=Image.LANCZOS) \
			.crop(self.resize_spec['crop_coords'])

		self.image.save(self.jpeg_image_buffer, format="PNG")
		return self.jpeg_image_buffer

	def get_image(self,options):
		options['size'] = self.get_image_size(options['x'],options['y'])
		
		images = MongoClient('localhost', 27017).Images.images

		count  = images.find({'size': options['size'] }).count()
		self.offset = randrange( 0,count)

		options['image'] = images.find({'size': options['size'] }).skip( self.offset ).limit(1)[0]["data"]

		return self.resize_image(options)


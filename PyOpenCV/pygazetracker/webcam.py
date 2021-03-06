# -*- coding: utf-8 -*-

from __init__ import _message
from generic import EyeTracker

import cv2
import numpy


class WebCamTracker(EyeTracker):
	
	"""OpenCV implementation of a webcam eye-tracker.
	"""
	
	
	def connect(self, camnr=0, mode='RGB', **kwargs):
		
		"""Use this function to implement the initialisation of a specific
		type of eye tracking.
		
		camnr			-	Integer that indicates what webcam should be
						used. Default = 0.
		
		mode			-	String that indicates how the captured frame
						should be processed before it's returned.
						'R' returns the red component of the frame,
						'G' returns the green component of the frame,
						'B' returns the blue component of the frame,
						'RGB' returns the greyscale version of the
						frame (converted by OpenCV). Default = 'RGB'.
		"""
		
		# Only initialise if it hasn't been done yet.
		if not self._connected:
			
			# Set mode and camera number
			self._camnr = camnr
			self._mode = mode

			# DEBUG message.
			_message(u'debug', u'webcam.WebCamTracker.connect', \
				u"Connecting to webcam %d." % (self._camnr))
		
			# Initialise the webcam.
			self._vidcap = cv2.VideoCapture(self._camnr)
			self._connected = True

			# DEBUG message.
			_message(u'debug', u'webcam.WebCamTracker.connect', \
				u"Successfully connected to webcam %d!" % (self._camnr))

	
	def _get_frame(self):
		
		"""Reads the next frame from the active OpenCV VideoCapture.
		
		Keyword Arguments
		
		Returns
		
		success, frame	-	success is a Boolean that indicates whether
						a frame could be obtained.
						frame is a numpy.ndarray with unsigned,
						8-bit integers that reflect the greyscale
						values of the image. If no frame could be
						obtained, None will be returned.
		"""
		
		# Take a photo with the webcam.
		# (ret is the return value: True if everything went ok, False if
		# there was a problem. frame is the image taken from the webcam as
		# a NumPy ndarray, where the image is coded as BGR
		ret, frame = self._vidcap.read()
		
		# If a new frame was available, proceed to process and return it.		
		if ret:
			# Return the red component of the obtained frame.
			if self._mode == 'R':
				return ret, frame[:,:,2]
			# Return the green component of the obtained frame.
			elif self._mode == 'G':
				return ret, frame[:,:,1]
			# Return the blue component of the obtained frame.
			elif self._mode == 'B':
				return ret, frame[:,:,0]
			# Convert to grey.
			elif self._mode == 'RGB':
				return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# Throw an exception if the mode can't be recognised.
			else:
				_message(u'error', u'webcam.WebCamTracker._get_frame', \
					u"Mode '%s' not recognised. Supported modes: 'R', 'G', 'B', or 'RGB'." \
					% (self._mode))
		
		# If a new frame wasn't available, return None.
		else:
			return ret, None
	
	def _close(self):
		
		"""Closes the connection to the OpenCV VideoCapture.
		"""

		# DEBUG message.
		_message(u'debug', u'webcam.WebCamTracker.close', \
			u"Disconnecting from webcam.")

		# Release the video capture from the current webcam.
		self._vidcap.release()

		# DEBUG message.
		_message(u'debug', u'webcam.WebCamTracker.close', \
			u"Successfully disconnected from webcam.")


# # # # #
# DEBUG #
if __name__ == u'__main__':

	import os
	import time
	from matplotlib import pyplot

	# Constants
	MODE = 'B'
	DUMMY = True
	DEBUG = False

	# Initialise a new tracker instance.
	tracker = WebCamTracker(debug=DEBUG)

	# In DUMMY mode, load an existing image (useful for quick debugging).
	if DUMMY:
		filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), u'test.jpg')
		img = cv2.imread(filepath)
		# Return the red component of the obtained frame.
		if MODE == 'R':
			frame = img[:,:,0]
		# Return the green component of the obtained frame.
		elif MODE == 'G':
			frame = img[:,:,1]
		# Return the blue component of the obtained frame.
		elif MODE == 'B':
			frame = img[:,:,2]
		# Convert to grey.
		elif MODE == 'RGB':
			frame = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
		t0 = time.time()
	# If not in DUMMY mode, obtain a frame through the _get_frame method.
	else:
		success = False
		while not success:
			t0 = time.time()
			success, frame = tracker._get_frame(mode=MODE)

	# Crop the face and the eyes from the image.
	success, facecrop = tracker._crop_face(frame, minsize=(30, 30))
	success, eyes = tracker._crop_eyes(facecrop, \
		Lexpect=(0.7,0.4), Rexpect=(0.3,0.4), maxdist=None, maxsize=None)
	# Find the pupils in both eyes
	B = tracker._find_pupils(eyes[0], eyes[1], glint=True, mode='diameter')
	t1 = time.time()

	# Close the connection with the tracker.
	tracker.close()
	
	# Process results
	print("Elapsed time: %.3f ms" % (1000*(t1-t0)))
	pyplot.figure(); pyplot.imshow(facecrop, cmap='gray')
	pyplot.figure(); pyplot.imshow(eyes[0], cmap='gray')
	pyplot.figure(); pyplot.imshow(eyes[1], cmap='gray')
# # # # #
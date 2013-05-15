import sys
import xbmcaddon
import xbmcgui
import xbmc
import os
import random

# get our addon
addon = xbmcaddon.Addon('screensaver.fuzzywuzzie.photoparade')

class Screensaver(xbmcgui.WindowXMLDialog):
	# use this exit monitor to request that we abort
	class ExitMonitor(xbmc.Monitor):
		def __init__(self, exitCallback):
			self.exitCallback = exitCallback

		def onScreensaverDeactivated(self):
			self.exitCallback()

	def onInit(self):
		# set up our screensaver exit monitor
		self.abortRequested = False
		self.monitor = self.ExitMonitor(self.requestAbort)

		# grab our image control
		self.imageControl = self.getControl(2)

		# and our error label
		self.errorControl = self.getControl(3)
		self.errorControl.setLabel('')

		# load our image duration from the settings
		self.duration = int(addon.getSetting('duration')) * 1000
		self.sourcePath = addon.getSetting('folder')

		# error check settings
		# make sure we have a valid path
		if not self.sourcePath:
			self.errorControl.setLabel('Photo parade: no input folder set up!')
			t = 0
			while True:
				xbmc.sleep(250)
				t += 250
				if self.abortRequested:
					break
			self.exit()

		# build our paths
		self.buildPaths()

		# start our parade
		self.parade()

	# let our monitor request an end to the slideshow
	def requestAbort(self):
		self.abortRequested = True

	# actually exit the slideshow
	def exit(self):
		# exit!
		del self.monitor
		self.close()

	# start the parade
	def parade(self):
		# continue forever
		while not self.abortRequested:
			# get our next image
			img = self.nextPath()
			
			# set the control
			self.imageControl.setImage(img)
			
			# handle quitting the screensaver
			# do it this way so we quit more responsively
			# (rather than waiting the full `self.duration` number of seconds first)
			t = 0
			while t < self.duration:
				xbmc.sleep(250)
				t += 250
				if self.abortRequested:
					t = self.duration

		self.exit()

	# get the next image
	def nextPath(self):
		# get our next path
		path = self.paths[self.pathIndex]

		# go to the next item in our path
		self.pathIndex += 1

		# if we've reached the end of the list, reshuffle
		if self.pathIndex >= self.numPaths:
			# regenerate our list
			self.buildPaths()

		# return our next image
		return path

	# build a list of all images in our given path
	def buildPaths(self):
		self.paths = []
		self.numPaths = 0
		try:
			# get all our files that are images
			for r, d, f in os.walk(self.sourcePath):
				for files in f:
					if files.lower().endswith('.jpg') or files.lower().endswith('.jpeg') or files.lower().endswith('.png') or files.lower().endswith('.gif') or files.lower().endswith('.bmp'):
						 self.paths.append(os.path.join(r, files))

			# make sure we have some images in the path
			if not self.paths:
				self.errorControl.setLabel('Photo parade: no images exist in the given folder!')
				t = 0
				while True:
					xbmc.sleep(250)
					t += 250
					if self.abortRequested:
						break
				self.exit()

			# randomly shuffle the list
			random.shuffle(self.paths)

			# and reset information about it
			self.numPaths = len(self.paths)
			self.pathIndex = 0

		except:
			self.abortRequested = True
			print "Photo parade unexpected error: ", sys.exc_info()[0]
			self.errorControl.setLabel('Photo parade: unexpected error (%s)!' % sys.exc_info()[0])

# add-on entry point
if __name__ == '__main__':
	# start our screensaver gui
	screensaver_gui = Screensaver('screensaver.xml', addon.getAddonInfo('path'), 'default')

	# go modal (and run)
	screensaver_gui.doModal()

	# clean up
	del screensaver_gui
	sys.modules.clear()

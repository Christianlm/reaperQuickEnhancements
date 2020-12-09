# -*- coding: UTF-8 -*-
# Reaper quick enhancements appModules for NVDA:
# v. 0.1.2020.11.23:
# Copyright (C)2020 by Chris Leo <llajta2012ATgmail.com>
# Released under GPL 2
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


import appModuleHandler
import addonHandler
import api
import ui
import controlTypes
from NVDAObjects.UIA import UIA
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible
from controlTypes import ROLE_STATICTEXT, ROLE_BUTTON, ROLE_PANE
from NVDAObjects.IAccessible import IAccessible, getNVDAObjectFromEvent
from winUser import CHILDID_SELF, OBJID_CLIENT, setFocus
import windowUtils
#import scriptHandler
from scriptHandler import script

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

def checkStatus ():
	statusw = statusWindow ()
	text = getTextFromWindow (statusw)
	if not text:
		return False
	return text

def statusWindow ():
	fg = api.getForegroundObject ().parent
	statuspanel = windowUtils.findDescendantWindow (fg.windowHandle, controlID = 1010)
	return statuspanel

def getTextFromWindow (statuspanel):
	obj = getNVDAObjectFromEvent (statuspanel, OBJID_CLIENT, CHILDID_SELF)
	return obj.displayText

class processStatus (IAccessible):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	@script(
		# Translators: Message presented in input help mode.
		description=_("Announces transport status")
	)
	def script_announceStatus (self, gesture):
		statusw = statusWindow ()
		text = getTextFromWindow (statusw)
		text = text.split ()
		if checkStatus ():
			import re
			status = re.sub('\d+.\d+.\d+', ': ', text[0])
			time = text[2]
			ui.message(status + " time position: " + time)
		else:
			ui.message("No status informations...")

class AppModule(appModuleHandler.AppModule):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	bpmIndex = 9

	def chooseNVDAObjectOverlayClasses (self, obj, clsList):
		if obj.role == ROLE_PANE and obj.name=="trackview" or obj.windowClassName=='REAPERTCPDisplay':
			clsList.insert (0, processStatus)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Announces audio properties")
	)
	def script_audioinf(self, gesture):
		focus = api.getFocusObject()
		if focus.windowClassName=="REAPERTCPDisplay" or focus.windowClassName=="REAPERTrackListWindow":
			obj = api.getForegroundObject().previous.lastChild
			aui = obj.name
			ui.browseableMessage("\n".join(aui.split(" ")), _("Audio properties "))
		else:
			ui.message("No audio properties from here...")

	def getBpm(self):
		fg = api.getForegroundObject().firstChild.firstChild
		bpm = fg.children[self.bpmIndex]
		if bpm.role == ROLE_BUTTON: return fg.firstChild.name
		return fg.children[self.bpmIndex].name

	@script(
		# Translators: Message presented in input help mode.
		description=_("Announces current BPM")
	)
	def script_announceBpm(self, gesture):
		obj = api.getForegroundObject().firstChild
		if obj.windowText!='Transport':
			ui.message(_("No transport bar displaye"))
		else:
			bpm = self.getBpm()
			ui.message(bpm)

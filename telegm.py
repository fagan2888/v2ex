from telegram.ext import Updater
import telegram
import arrow 

class ServerLogger():
	def __init__(self):
		self.bot = telegram.Bot(token='694574546:AAHP1sIl71OMKeHWWSzqTbTIAsps1k1KdMU')
		self.greco = '460172892'

	def alertGreco(self, status, fname=''):
		# status += '\n#' + fname + ' ' 
		self.bot.send_message(chat_id=self.greco, text=status)


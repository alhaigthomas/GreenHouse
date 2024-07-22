from app.controll.relay import relay
from app.extensions.log import log
import asyncio
import time

class Acctuator:
	def __init__(self, relay_indexes, extension_time):
		self.extension_time = extension_time
		self.relays = relay_indexes
		self.state = 0 # we don't know what state it is in. but we can assume that it is retracted
		# first relay in sequence is the dominant ( turn it on - the acctuator will extend )
	
    # I have a seperate fire and forget decorator for the relays allowing togglable asyncronousity
	def fire_and_forget(f):
		""" Fire and forget is just asyncronously doing two things at the same time! 
		eg. extend and acctuator AND not have to wait for it to fully extend"""
		def wrapped(*args, **kwargs):
			try:
				if args[1]:
					return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)
				return f(args[0], args[1])
			except:
				return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)
		return wrapped
	
	@fire_and_forget
	def extend(self, asynchronous=True):
		relay.turn_on_relay_by_index(self.relays[0])
		log('ControllerPi', None, 'controll', 'acctuator', 'Extending acctuator on relay', arg=self.relayIndex)
		time.sleep(self.extension_time) # takes about 22 seconds to fully extend
		self.state = 1 # show that it is extended
		relay.turn_off_relay_by_index(self.relays[0])
		log('ControllerPi', True, 'controll', 'acctuator', 'Extended acctuator on relay', arg=self.relayIndex)


	@fire_and_forget
	def retract(self, asynchronous=True):
		relay.turn_on_relay_by_index(self.relays[1])
		time.sleep(self.extension_time) # it also takes 22 seconds to retract
		self.state = 0
		relay.turn_off_relay_by_index(self.relays[1])

	def toggle(self, asynchronous=True):
		if self.state == 1:
			self.retract(asynchronous)
		else:
			self.extend(asynchronous)

	def stop(self):
		""" turn off everything, this will stop and movment of the acctuator """
		relay.turn_off_relay_by_index(self.relays[0])
		relay.turn_off_relay_by_index(self.relays[1])

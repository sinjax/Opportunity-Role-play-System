from random import randint, shuffle
class Die:
	""" A single die """
	def __init__(self, colour = None, value = None):
		if(value == None):
			self.roll()
			
	def roll(self):
		self.value = randint(1,6)
	
class DiceSet: 
	""" The dice set that is rolled by each player in the Roll phase of the 
	Seizing Opportunity stage """
	def __init__(self):
		self.Dice = [Die("Attack"),
					 Die("Attack"),
					 Die("Defence"),
					 Die("Defence"),
					 Die("Maneuver"),
					 Die("Maneuver")]
					 
	def roll(self):
		for die in self.Dice:
			die.roll()
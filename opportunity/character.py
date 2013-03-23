
from dice import Die

class Attributes:
	""" A character's attributes """
	def __init__(self, physique, agility, intelligence):
		self.physique = physique
		self.agility = agility
		self.intelligence = intelligence
	
class Weapon:	
	""" A character's weapon """
	def __init__(self, damage, effective_range, armour_penetration, blunt):
		self.damage = damage
		self.effective_range = effective_range
		self.armour_penetration = armour_penetration
		self.blunt = blunt
	
class Armour:
	""" A charater's armour """
	def __init__(self, value, coverage):
		self.value = value
		self.coverage = coverage
	
class Temporary:
	""" A characters temporary numbers """
	def __init__(self, skill, position, trauma, initiative):
		self.skill = skill
		self.position = position
		self.trauma = trauma
		self.initiative = initiative
		self.pool = []

class Status:
	""" A character's status """
	def __init__(self, aimed, fallen, fatally_injured):
		self.melee_lock = set()
		self.aimed = aimed
		self.fallen = fallen
		self.fatally_injured = fatally_injured
		self.dead = False

class Character:
	""" A player character or NPC in a combat """
	def __init__(self, name, attributes, weapon, armour, temporary, status):
		self.name = name
		self.attributes = attributes
		self.weapon = weapon
		self.armour = armour
		self.temporary = temporary
		self.status = status
		
	def calculate_initiative(self):
		""" Once temporary.pool is filled, call to calculate initiative """
		self.temporary.initiative = self.attributes.agility
		for die in self.temporary.pool:
			self.temporary.initiative += die.value
			
	def update_status(self):
		""" At the start of a turn, call to update status due to trauma and 
		fatal injuries """
		report = []
		started_fallen = self.status.fallen
		if self.status.fatally_injured == True:
			trauma_increase = self.trauma_resist_check()
			if trauma_increase >= 0:
				if started_fallen == True:
					self.temporary.trauma += trauma_increase
					if self.temporary.trauma > 10 * self.attributes.physique:
						self.status.dead = True
						report.append('%s is dead' % self.name)
					else:
						report.append('%s\'s wounds are worsening' % self.name)
				else:
					report.append('%s has fallen from their wounds' % self.name)
				
		return report
			
	def trauma_resist_check(self):
		""" If temporary.trauma is updated, call to check for the effects of 
		trauma """
		trauma_resist_check = \
			self.attributes.physique + Die().value + Die().value
		
		condition_worsening = self.temporary.trauma - trauma_resist_check
		if condition_worsening >= 0:
			self.status.fallen = True
  
		return condition_worsening
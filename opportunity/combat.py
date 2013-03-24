from random import randint, shuffle
from operator import attrgetter
class Combat(object):
	"""Defines combat, its various stages, the characters involved"""
	def __init__(self,*combatants):
		super(Combat, self).__init__()
		self.combatants = list(combatants)
	def determine_pick_order(self):
		""" Determine the order of dice picking during the Pick phase of the Seizing 
			Opportunity stage """
		# Place self.combatants in skill order.
		shuffle(self.combatants) 
		pick_key = attrgetter(
			'temporary.skill',
			'temporary.position', 
			'temporary.trauma', 
			'attributes.agility', 
			'attributes.intelligence'
		)
		self.combatants.sort(key = pick_key, reverse = True)

		# Get a list of the different skill bands.
		seen = {}
		skill_bands = []
		for combatant in self.combatants:
			skill = combatant.temporary.skill
			if skill in seen:
				continue
			seen[skill] = True
			skill_bands.append(skill)

		# Work out the pick order.
		pick_order = []
		for skill_band in skill_bands:
			for combatant in self.combatants:
				if(combatant.temporary.skill >= skill_band):
					pick_order.append(combatant)
				else:
					break
					
		total_picks = 3 * len(self.combatants)
		while len(pick_order) < total_picks:
			pick_order.extend(self.combatants)

		return pick_order[:total_picks]

	def determine_initiative_order(self):
		""" Determine a character's initiative based on their pool in the 
		Initiative phase of the Seizing Opportunity stage """
		shuffle(self.combatants) 
		pick_key = attrgetter('temporary.initiative', 
					'temporary.position', 
					'temporary.trauma', 
                                        'attributes.agility', 
					'attributes.intelligence')
		self.combatants.sort(key = pick_key, reverse = True)

	def attack(self,attacker, ATT, accuracy, target, DEF):
		""" Make an attack in the Violence stage as the result of an active action.
		ATT is the raw ATT value derived from the red dice used in the action
		accuracy is the value of the highest red dice used in the action
		DEF is the raw DEF value derived from the green dice used in the action """ 
		report = []
		if accuracy <= target.armour.coverage:
			armour_defence = \
				target.armour.value - attacker.weapon.armour_penetration
			if armour_defence > 0:
				DEF += armour_defence
				report.append('%s\'s attack hits armour' % attacker.name)
			else:
				report.append('%s\'s attack breaks through armour' % attacker.name)
		else:
			report.append('%s\'s attack strikes an unarmoured area' % attacker.name)
		
		if (len(attacker.status.melee_lock) > 0):
			encumbered = attacker.weapon.effective_range
			if encumbered > 0:
                                ATT -= encumbered
                                report.append('%s is encumbered by their weapon' % attacker.name)
		elif attacker.status.aimed == True:
                        if target.temporary.position < attacker.temporary.position:
                                ATT += attacker.weapon.effective_range
                                report.append('%s\'s takes an aimed shot' % attacker.name)
			
		if ATT > DEF:
			target.status.aimed = False
			sustained_trauma = attacker.weapon.damage
			if ATT - DEF >= 3:
				if attacker.weapon.blunt == False:
					target.status.fatally_injured = True
					report.append('%s has suffered a fatal injury' % target.name)
				sustained_trauma += 3
				
			target.temporary.trauma += sustained_trauma
			
			pain = (sustained_trauma + 1)/2
			if target.temporary.position < pain:
				target.temporary.position = 0
			else:
				target.temporary.position -= pain
			
			trauma_resist_max = target.attributes.physique + 12
			if sustained_trauma >= trauma_resist_max:
				target.status.dead = True
				report.append('Instant Kill!')
			else:
				fallen = target.trauma_resist_check()			
				if fallen >= 0:
					report.append('%s has fallen' % target.name)
				else:
					report.append('%s is still standing' % target.name)
		else:
			report.append('%s\'s attack does not cause injury' % attacker.name)
			
		return report
			
	def melee_lock(self,combatantA, combatantB):
		""" Create a melee lock pairing between two self.combatants """
		combatantA.status.melee_lock.update(combatantB.status.melee_lock)
		combatantB.status.melee_lock.update(combatantA.status.melee_lock)
		combatantA.status.melee_lock.add(combatantB)	
		combatantB.status.melee_lock.add(combatantA)
		combatantA.status.melee_lock.discard(combatantA)
		combatantB.status.melee_lock.discard(combatantB)
		
		report = []
		names = ([opponent.name + ', ' \
			for opponent in combatantA.status.melee_lock])
		names.extend('and ' + combatantA.name)
		report.append('%s are now locked in close combat' % ''.join(names))
			
		return report
		
	def break_melee_lock(self,combatant):
		""" Break a combatant out of their melee lock """
		report = []
		opponent_names = [opponent.name + ', ' \
			for opponent in combatant.status.melee_lock]
		report.append('%s has broken from close combat with %s' % \
			(combatant.name, ''.join(opponent_names)))
		
		for opponent in combatant.status.melee_lock:
			opponent.status.melee_lock.discard(combatant)
	 
		combatant.status.melee_lock.clear()
		
		return report
		
	def check_melee_lock(self,combatantA, combatantB):
		""" Check if two self.combatants are in melee lock with each other """
		return combatantA in combatantB.status.melee_lock
                        
        


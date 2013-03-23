from opportunity.character import *
from opportunity.dice import *
from opportunity.combat import *

from operator import attrgetter

def test_combat():
	Alice = Character(
		"Alice",
		Attributes(2,2,2),
		Weapon(5,0,1, False),
		Armour(0,0),
		Temporary(3,0,0,0),
		Status(False, False, False))
		
	Bob = Character(
		"Bob",
		Attributes(2,2,2),
		Weapon(1,0,0, True),
		Armour(0,0),
		Temporary(2,0,0,0),
		Status(False, False, False))

	Claire = Character(
		"Claire",
		Attributes(2,2,2),
		Weapon(1,0,0, True),
		Armour(2,3),
		Temporary(2,0,0,0),
		Status(False, False, False))


	# Combat Turn:

	# seizing opportunity:
	# roll
	AliceSet = DiceSet()
	BobSet = DiceSet()
	ClaireSet = DiceSet()

	combat = Combat(Alice,Bob,Claire)
	# pick
	p = combat.determine_pick_order()
	for i in p:
		print i.name

	## To do - need player interaction for picking
	Alice.temporary.pool.append(AliceSet.Dice[1])
	Alice.temporary.pool.append(AliceSet.Dice[2])
	Alice.temporary.pool.append(AliceSet.Dice[5]) 
	Bob.temporary.pool.append(BobSet.Dice[2])
	Bob.temporary.pool.append(BobSet.Dice[4])
	Bob.temporary.pool.append(BobSet.Dice[0])
	Claire.temporary.pool.append(ClaireSet.Dice[2])
	Claire.temporary.pool.append(ClaireSet.Dice[4])
	Claire.temporary.pool.append(ClaireSet.Dice[0])

	# initiative
	for combatant in combat.combatants:
		combatant.calculate_initiative()
		print combatant.name
		print combatant.temporary.initiative

	combat.determine_initiative_order()
	for combatant in combat.combatants:
		print combatant.name
		print combatant.temporary.initiative
		
	# violence:
	## To do
	# round
	print
	print combat.melee_lock(Claire, Alice)
	for n in Bob.status.melee_lock:
		print n.name	
	print combat.melee_lock(Alice, Bob)
	print combat.melee_lock(Bob, Alice)
	print combat.check_melee_lock(Bob, Alice)
	print combat.check_melee_lock(Alice, Bob)
	for n in Bob.status.melee_lock:
		print n.name 
	print combat.break_melee_lock(Bob)
	for n in Bob.status.melee_lock:
		print n.name 
	print combat.check_melee_lock(Bob, Alice)
	print combat.check_melee_lock(Alice, Bob)
	while (Claire.status.fallen == False) and (Claire.status.dead == False):
		AliceDice = Die().value + Die().value
		ClaireDice = Die().value
		print "Alice ATT %d Clair DEF %d" %(AliceDice,ClaireDice)
		print combat.attack(Alice, AliceDice, AliceDice, Claire, ClaireDice)
		print "Claire Trauma %d" %Claire.temporary.trauma
		print
		print Claire.update_status() 
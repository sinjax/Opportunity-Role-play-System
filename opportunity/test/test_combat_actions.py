from opportunity.character import *
from opportunity.dice import *
from opportunity.combat import *

def test_combat():
	Alice = Character(
		"Alice",
		Attributes(2,2,2),
		Weapon(5,0,1, False),
		Armour(0,0),
		Temporary(3,0,0,0),
		Status(False, False, False))

	Claire = Character(
		"Claire",
		Attributes(2,2,2),
		Weapon(1,2,0, True),
		Armour(2,3),
		Temporary(2,0,0,0),
		Status(False, False, False))
	
	AliceSet = DiceSet()
	ClaireSet = DiceSet()

	combat = Combat(Alice, Claire)
        Alice.temporary.pool.append(AliceSet.Dice[1])
        Alice.temporary.pool.append(AliceSet.Dice[2])
        Alice.temporary.pool.append(AliceSet.Dice[5])
        Claire.temporary.pool.append(ClaireSet.Dice[0])    
        Claire.temporary.pool.append(ClaireSet.Dice[2])
        Claire.temporary.pool.append(ClaireSet.Dice[4])    

        report = []
	(response_allowed, action, action_report) = combat.charge(Claire, ClaireSet.Dice[0], ClaireSet.Dice[4], Alice)
	report.extend(action_report)
	if response_allowed:
		(response_allowed, action, action_report) = combat.block(Alice, AliceSet.Dice[2], Claire, action)
		report.extend(action_report)
		if response_allowed:
			(response_allowed, action, action_report) = combat.block(Claire, ClaireSet.Dice[2], Alice, action)
			report.extend(action_report)
	action_report = action()
	if action_report != None:
		report.extend(action_report)
	
	# alice attacks
	(response_allowed, action, action_report) = combat.melee_attack(Alice, AliceSet.Dice[1], Claire)
	report.extend(action_report)
	if response_allowed:
		(response_allowed, action, action_report) = combat.block(Claire, ClaireSet.Dice[2], Alice, action)
		report.extend(action_report)
		if response_allowed:
			(response_allowed, action, action_report) = combat.no_defence(defender, attacker, attack)
			report.extend(action_report)
	action_report = action()
	if action_report != None:
		report.extend(action_report)
		
	print report

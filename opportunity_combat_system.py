from random import randint, shuffle
from operator import attrgetter


class Attributes:
    def __init__(self, physique, agility, intelligence):
        self.physique = physique
        self.agility = agility
        self.intelligence = intelligence
    
class Weapon:    
    def __init__(self, damage, effective_range, armour_penetration):
        self.damage = damage
        self.effective_range = effective_range
        self.armour_penetration = armour_penetration
    
class Armour:
    def __init__(self, value, coverage):
        self.value = value
        self.coverage = coverage
    
class Temporary:
    def __init__(self, skill, position, trauma, initiative):
        self.skill = skill
        self.position = position
        self.trauma = trauma
        self.initiative = initiative
        self.pool = []

class Status:
    def __init__(self, melee_lock, aimed, fallen, fatally_injured):
        self.melee_lock = melee_lock
        self.aimed = aimed
        self.fallen = fallen
        self.fatally_injured = fatally_injured

class Character:
    def __init__(self, name, attributes, weapon, armour, temporary, status):
        self.name = name
        self.attributes = attributes
        self.weapon = weapon
        self.armour = armour
        self.temporary = temporary
        self.status = status
        
    def calculate_initiative(self):
        self.temporary.initiative = self.attributes.agility
        for die in self.temporary.pool:
            self.temporary.initiative += die.value
      
class Die:
    def __init__(self, colour, value = None):
        if(value == None):
            self.roll()
            
    def roll(self):
        self.value = randint(1,6)
    
class DiceSet:    
    def __init__(self):
        self.Dice = [Die("Attack"),
                     Die("Attack"),
                     Die("Defence"),
                     Die("Defence"),
                     Die("Maneuver"),
                     Die("Maneuver")]
                     
    def roll(self):
        for i in range(1,6):
            self.Dice[i].roll()

def determine_pick_order(combatants):
    """ Determines the order of dice picking during the Pick step of Seize 
    Opportunity. """
    
    # Place combatants in skill order.
    shuffle(combatants) 
    pick_key = attrgetter('temporary.skill', 
                          'temporary.position', 
                          'temporary.trauma', 
                          'attributes.agility', 
                          'attributes.intelligence')
    combatants.sort(key = pick_key, reverse = True)
    
    # Get a list of the different skill bands.
    seen = {}
    skill_bands = []
    for combatant in combatants:
        skill = combatant.temporary.skill
        if skill in seen: 
            continue
        seen[skill] = 1
        skill_bands.append(skill)
    
    # Work out the pick order
    pick_order = []
    for skill_band in skill_bands:
        for combatant in combatants:
            if(combatant.temporary.skill >= skill_band):
                pick_order.append(combatant)
            else:
                break
                
    total_picks = 3 * len(combatants)
    while len(pick_order) < total_picks:
        pick_order.extend(combatants)

    return pick_order[:total_picks]

def determine_initiative_order(combatants):
    shuffle(combatants) 
    pick_key = attrgetter('temporary.initiative', 
                          'temporary.position', 
                          'temporary.trauma', 
                          'attributes.agility', 
                          'attributes.intelligence')
    combatants.sort(key = pick_key, reverse = True)

if  __name__ =='__main__':
    Alice = Character(
        "Alice",
        Attributes(2,2,2),
        Weapon(1,0,0),
        Armour(0,0),
        Temporary(3,0,0,0),
        Status(False, False, False, False))
        
    Bob = Character(
        "Bob",
        Attributes(2,2,2),
        Weapon(1,0,0),
        Armour(0,0),
        Temporary(2,0,0,0),
        Status(False, False, False, False))

    Claire = Character(
        "Claire",
        Attributes(2,2,2),
        Weapon(1,0,0),
        Armour(0,0),
        Temporary(2,0,0,0),
        Status(False, False, False, False))
    
    Combatants = [Alice, Bob, Claire]
    
    # seizing opportunity:
    # roll
    AliceSet = DiceSet()
    BobSet = DiceSet()
    ClaireSet = DiceSet()
    
    # pick
    p = determine_pick_order(Combatants)
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
    for combatant in Combatants:
        combatant.calculate_initiative()
        print combatant.temporary.initiative

    determine_initiative_order(Combatants)
    for combatant in Combatants:
        print combatant.temporary.initiative
        
    # violence:
    ## To do
    # round
    ## To do
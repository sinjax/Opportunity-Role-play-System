from random import randint, shuffle
from operator import attrgetter


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

def determine_pick_order(combatants):
    """ Determine the order of dice picking during the Pick phase of the Seizing 
    Opportunity stage """
    
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
        seen[skill] = True
        skill_bands.append(skill)
    
    # Work out the pick order.
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
    """ Determine the a character's initiative based on their pool in the 
    Initiative phase of the Seizing Opportunity stage """
    shuffle(combatants) 
    pick_key = attrgetter('temporary.initiative', 
                          'temporary.position', 
                          'temporary.trauma', 
                          'attributes.agility', 
                          'attributes.intelligence')
    combatants.sort(key = pick_key, reverse = True)

def attack(attacker, ATT, accuracy, target, DEF):
    """ Make an attack in the Violence stage as the result of an active action.
    ATT is the raw ATT value derived from the red dice used in the action
    accuracy is the value of the highest red dice used in the action
    DEF is the raw REF value derived from the green dice used in the action """ 
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
        ATT -= attacker.weapon.effective_range
        report.append('%s is encumbered by their weapon' % attacker.name)
    elif attacker.status.aimed == True:
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
    
def melee_lock(combatantA, combatantB):
    """ Create a melee lock pairing between two combatants """
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
    
def break_melee_lock(combatant):
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
    
def check_melee_lock(combatantA, combatantB):
    """ Check if two combatants are in melee lock with each other """
    return combatantA in combatantB.status.melee_lock

if  __name__ =='__main__':
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
    
    Combatants = [Alice, Bob, Claire]
    
    # Combat Turn:
    
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
        print combatant.name
        print combatant.temporary.initiative
        
    # violence:
    ## To do
    # round
    print
    print melee_lock(Claire, Alice)
    for n in Bob.status.melee_lock:
        print n.name    
    print melee_lock(Alice, Bob)
    print melee_lock(Bob, Alice)
    print check_melee_lock(Bob, Alice)
    print check_melee_lock(Alice, Bob)
    for n in Bob.status.melee_lock:
        print n.name 
    print break_melee_lock(Bob)
    for n in Bob.status.melee_lock:
        print n.name 
    print check_melee_lock(Bob, Alice)
    print check_melee_lock(Alice, Bob)
    while (Claire.status.fallen == False) and (Claire.status.dead == False):
        AliceDice = Die().value + Die().value
        ClaireDice = Die().value
        print "Alice ATT %d Clair DEF %d" %(AliceDice,ClaireDice)
        print attack(Alice, AliceDice, AliceDice, Claire, ClaireDice)
        print "Claire Trauma %d" %Claire.temporary.trauma
        print
        print Claire.update_status() 
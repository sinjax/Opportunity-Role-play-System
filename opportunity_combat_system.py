from random import randint, shuffle
from operator import attrgetter


class Attributes:
    def __init__(self, physique, agility, intelligence):
        self.physique = physique
        self.agility = agility
        self.intelligence = intelligence
    
class Weapon:    
    def __init__(self, damage, effective_range, armour_penetration, blunt):
        self.damage = damage
        self.effective_range = effective_range
        self.armour_penetration = armour_penetration
        self.blunt = blunt
    
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
    def __init__(self, melee_lock_group, aimed, fallen, fatally_injured):
        self.melee_lock_group = melee_lock_group
        self.aimed = aimed
        self.fallen = fallen
        self.fatally_injured = fatally_injured
        self.dead = False

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
            
    def update_status(self):
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
        trauma_resist_check = \
            self.attributes.physique + Die().value + Die().value
        
        condition_worsening = self.temporary.trauma - trauma_resist_check
        if condition_worsening >= 0:
            self.status.fallen = True
  
        return condition_worsening
            
      
class Die:
    def __init__(self, colour = None, value = None):
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
        for die in self.Dice:
            die.roll()

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
    shuffle(combatants) 
    pick_key = attrgetter('temporary.initiative', 
                          'temporary.position', 
                          'temporary.trauma', 
                          'attributes.agility', 
                          'attributes.intelligence')
    combatants.sort(key = pick_key, reverse = True)

def attack(attacker, ATT, accuracy, target, DEF):
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
    
    if (attacker.status.melee_lock_group > 0):
        ATT -= attacker.weapon.effective_range
        report.append('%s\'s is encumbered by their weapon' % attacker.name)
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
    
class melee_lock:
    def __init__(self):
        self.melee_lock_groups = []
        self.next_group_index = 1
        
    def lock(self, combatants): 

        # get list of melee lock groups combatants are already in, and assign 
        # new group to combatants not already melee locked
        seen = {}
        equivalences = []
        allocated_new_group = False
        for combatant in combatants:
            group = combatant.melee_lock_group
            if group in seen: 
                continue
            if group == 0:
                group = next_group_index
                allocated_new_group = True
            seen[group] = True
            equivalences.append(combatant.melee_lock_group)        
            
        if allocated_new_group == True:
            next_group_index += 1
        
        # update melee lock groups
        seen = {}
        groups = []
        for equivalence in equivalences:
            self.melee_lock_groups[equivalence]
            skill = combatant.temporary.skill
            if skill in seen: 
                continue
            seen[skill] = True
            skill_bands.append(skill)
    
        for equivalence in equivalences:
            groups = self.melee_lock_groups[equivalence]
            for equivalence in equivalences:
                if equivalence in groups:
                    continue
                groups.append(equivalence)
            
    def check_lock(self, combatantA, combatantB):
        locked = False
        groupA = combatantA.melee_lock_group
        groupB = combatantB.melee_lock_group
        if groupA > 0 and groupB > 0:
            if groupB in self.melee_lock_groups[groupA]:
                locked = True
        return locked

class action:
    def check_prerequisites(self, combatant):
        pass
        
    def act(self, combatant):
        pass
    

if  __name__ =='__main__':
    Alice = Character(
        "Alice",
        Attributes(2,2,2),
        Weapon(5,0,1, False),
        Armour(0,0),
        Temporary(3,0,0,0),
        Status(False, False, False, False))
        
    Bob = Character(
        "Bob",
        Attributes(2,2,2),
        Weapon(1,0,0, True),
        Armour(0,0),
        Temporary(2,0,0,0),
        Status(False, False, False, False))

    Claire = Character(
        "Claire",
        Attributes(2,2,2),
        Weapon(1,0,0, True),
        Armour(2,3),
        Temporary(2,0,0,0),
        Status(False, False, False, False))
    
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
    while (Claire.status.fallen == False) and (Claire.status.dead == False):
        AliceDice = Die().value + Die().value
        ClaireDice = Die().value
        print "Alice ATT %d Clair DEF %d" %(AliceDice,ClaireDice)
        print attack(Alice, AliceDice, AliceDice, Claire, ClaireDice)
        print "Claire Trauma %d" %Claire.temporary.trauma
        print
        print Claire.update_status() 
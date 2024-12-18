
import glm
from Entities.Entity import Entity

class AliveEntity(Entity,abstract=True):
    # __slots__ = 'actions','pickup_range','inventory','armour_inventory','stats','exp','max_speed','total_health','defense','regen_multiplier','health','strength','max_energy', \
    # 'energy','attack_speed','time_between_attacks','time_to_attack','time_to_regen','regen_time','vision_collider','vision_squared','states','ground','invulnerability_time', \
    # 'time_til_vulnerable','direction','extra_speed','extra_speed_sum','extra_total_health','extra_total_health_sum','extra_regen','extra_regen_sum','extra_strength' ,\
    # 'extra_strength_sum','extra_energy','extra_energy_sum','extra_defense','extra_defense_sum','effects','state','healthbar'
    __slots__ = 'max_hp','health'
    def __init__(self,position:tuple[float,float],size:tuple[float,float]|glm.vec2,max_hp:float,health:float):
        super().__init__(position,size)
        self.max_hp = max_hp
        self.health = health        
        # self.pickup_range = max(*Settings.HITBOX_SIZE[self.species]) * half_sqrt_2 # just a shortcut for finding the length to the corner of a box from the middle when you only know a side length
        # self.inventory = UniversalInventory(Settings.INVENTORY_SPACES_BY_SPECIES[self.species],self)
        # self.armour_inventory = ArmorInventory(*Settings.ARMOUR_SLOTS_BY_SPECIES[self.species])
        # #Stats
        # self.stats = Settings.STATS_BY_SPECIES[self.species].copy()
        # self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # self.max_speed = Settings.MAX_SPEED_BY_SPECIES[self.species] 
        # speed = self.stats['speed'] 
        # self.speed = self.max_speed * speed / (speed + 100)
        # self.total_health = self.stats['constitution'] * 5 + self.stats['strength'] + self.stats['stamina']
        # assert isinstance(self.stats['defense'],int)
        # self.defense = self.stats['defense']
        # self.regen_multiplier = self.stats['constitution'] + self.stats['strength']
        # self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1
        # self.health = self.total_health
        # self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + self.stats['stamina']
        # self.max_energy = self.stats['energy']
        # assert isinstance(self.stats['energy'],int)
        # self.energy = self.stats['energy']
        # self.attack_speed = self.energy / 10
        # self.time_between_attacks = 1/self.attack_speed
        # self.time_to_attack = self.time_between_attacks
        # self.time_to_regen = 0.0 # regen timer
        # self.regen_time = 1.0 # how long in seconds should we wait between regen ticks
        # self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES[self.species]*2,Settings.VISION_BY_SPECIES[self.species]*2)
        # self.vision_squared = Settings.VISION_BY_SPECIES[self.species] ** 2
        # self.states = []
        # self.ground:ground.Ground = ground.Invalid()
        # damage timer

        
        # self.extra_speed:dict[str,float] = {}; self.extra_speed_sum = 0.0
        # self.extra_total_health:dict[str,int] = {}; self.extra_total_health_sum = 0.0
        # self.extra_regen:dict[str,float] = {}; self.extra_regen_sum = 0.0
        # self.extra_strength:dict[str,int] = {}; self.extra_strength_sum = 0.0
        # self.extra_energy:dict[str,int] = {}; self.extra_energy_sum = 0.0
        # self.extra_defense:dict[str,int] = {}; self.extra_defense_sum = 0.0

        # self.effects:list[EntityEffect] = []

    def takeDamage(self,dmg:float):
        self.health -= dmg
        if self.health <= 0:
            self.dead = True
            self.health = 0.0

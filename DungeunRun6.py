import tkinter as tk
from tkinter import ttk
import random, math, time, json, os

# ---------- Config ----------
WINDOW_W = 800
WINDOW_H = 600
ROOM_ROWS = 2
ROOM_COLS = 5
MAX_SKILLS = 9
SAVE_FILE = "player_save.json"

# ---------- Class-based automatic stat growth ----------
CLASS_STAT_GROWTH = {
    'Warrior': {'strength': 1, 'vitality': 1, 'agility': 1, 'intelligence': 0, 'wisdom': 0, 'will': 0, 'constitution': 1},
    'Mage':    {'strength': 0, 'vitality': 0, 'agility': 0, 'intelligence': 2, 'wisdom': 1, 'will': 1, 'constitution': 0},
    'Rogue':   {'strength': 1, 'vitality': 0, 'agility': 2, 'intelligence': 1, 'wisdom': 1, 'will': 0, 'constitution': 0},
    'Cleric':  {'strength': 0, 'vitality': 0, 'agility': 0, 'intelligence': 1, 'wisdom': 1, 'will': 2, 'constitution': 1},
    'Druid':   {'strength': 0, 'vitality': 1, 'agility': 1, 'intelligence': 2, 'wisdom': 2, 'will': 1, 'constitution': 0},
    'Monk':    {'strength': 0, 'vitality': 2, 'agility': 1, 'intelligence': 0, 'wisdom': 0, 'will': 0, 'constitution': 1},
    'Ranger':  {'strength': 1, 'vitality': 0, 'agility': 1, 'intelligence': 1, 'wisdom': 1, 'will': 0, 'constitution': 0},
}

# ---------- Utilities ----------
def clamp(v,a,b): return max(a,min(b,v))
def distance(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

# ---------- Player ----------
class Player:
    def __init__(self,name='Hero',class_name='Warrior'):
        self.name=name; self.class_name=class_name
        self.x=WINDOW_W//2; self.y=WINDOW_H//2; self.size=16
        self.strength=5; self.vitality=5; self.agility=5
        self.intelligence=5; self.wisdom=5; self.will=5; self.constitution=3
        self.level=1; self.xp=0; self.xp_to_next=100
        self.stat_points=5; self.skill_points=0
        self.skills=[]; self.unlocked_skills=[]
        self.populate_skills()
        self.update_stats()
        self.hp = self.max_hp
        self.mana = self.max_mana

    def update_stats(self):
        self.max_hp=50+self.vitality*10
        self.hp=min(getattr(self,'hp',self.max_hp),self.max_hp)
        self.max_mana=20+self.intelligence*10
        self.mana=min(getattr(self,'mana',self.max_mana),self.max_mana)
        self.speed=2+self.agility*0.3
        self.atk=5+self.strength
        self.mag=2+self.will
        self.hp_regen=0.2+self.vitality*0.05
        self.mana_regen=0.1+self.wisdom*0.15

    def populate_skills(self):
        def dark_slash(player, game):
            if player.mana < 5 or not game.room.enemies:
                return
            player.mana -= 5
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            angle_center = math.atan2(target.y - player.y, target.x - player.x)
            num_particles = 6
            arc_radius = 50
            arc_width = math.pi / 3
            px, py = player.x, player.y
            for i in range(num_particles):
                angle = angle_center - arc_width/2 + (i / (num_particles-1)) * arc_width
                x = px + math.cos(angle) * arc_radius * random.uniform(0.7, 1.0)
                y = py + math.sin(angle) * arc_radius * random.uniform(0.7, 1.0)
                size = random.uniform(5, 10)
                game.spawn_particle(x, y, size, 'purple')
                for e in list(game.room.enemies):
                    dx, dy = e.x - px, e.y - py
                    dist = math.hypot(dx, dy)
                    if dist <= arc_radius:
                        angle_to_enemy = math.atan2(dy, dx)
                        diff = (angle_to_enemy - angle_center + math.pi*2) % (math.pi*2)
                        if diff < arc_width/2 or diff > math.pi*2 - arc_width/2:
                            game.damage_enemy(e, player.atk * 1.5)
        def strike(player, game):
            if player.mana < 1: return
            player.mana -= 1
            game.spawn_particle(player.x, player.y, 10, 'yellow')
            for e in list(game.room.enemies):
                if distance((player.x, player.y), (e.x, e.y)) < 30:
                    game.damage_enemy(e, player.atk)

        def ground_pound(player, game):
            if player.mana < 10: return
            player.mana -= 10
            for _ in range(12):
                game.spawn_particle(
                    player.x + random.uniform(-30, 30),
                    player.y + random.uniform(-30, 30),
                    random.uniform(8,12),
                    'brown'
                )
            for e in game.room.enemies:
                if distance((player.x, player.y), (e.x, e.y)) < 70:
                    game.damage_enemy(e, player.atk * 1.5)


        def fist_blast(player, game):
            if player.mana < 5 or not game.room.enemies: return
            player.mana -= 5
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 1.0, 8, 'brown', player.atk*5)

        def shadow_dagger(player, game):
            if player.mana < 5 or not game.room.enemies: return
            player.mana -= 5
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'purple', player.mag*3, owner='player', stype='dagger')

        def fireball(player, game):
            if player.mana < 15 or not game.room.enemies: return
            player.mana -= 15
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 8, 10, 10, 'orange', 50, 'player', ptype='fireball')


        def ice_shard(player, game):
            if player.mana < 15 or not game.room.enemies: return
            player.mana -= 15
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'cyan', player.mag*10)

        def mana_bolt(player, game):
            if player.mana < 3 or not game.room.enemies: return
            player.mana -= 3
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'cyan', player.mag*3, owner='player', stype='bolt')
        def arrow_shot(player, game):
            if player.mana < 1 or not game.room.enemies: return
            player.mana -= 1
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'brown', player.atk*2, owner='player', stype='arrow')
        def chi_blast(player, game):
            if player.hp < 3 or not game.room.enemies: 
                return

            player.hp -= 3
            # Helper function to spawn a bolt
            def spawn_bolt():
                target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
                ang = math.atan2(target.y - player.y, target.x - player.x)
                game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'cyan', player.hp/10, owner='player', stype='bolt')

            # Shoot immediately
            spawn_bolt()

            # Schedule next two bolts after 0.5s and 1.0s
            game.after(500, spawn_bolt)   # 500 ms = 0.5 sec
            game.after(1000, spawn_bolt)  # 1000 ms = 1 sec


        def mana_shield(player, game):
            mana_cost_per_second = 5
            if player.mana <= 0: return
            now = time.time()
            if not hasattr(player, '_mana_shield_last'): player._mana_shield_last = now
            dt = now - player._mana_shield_last
            player._mana_shield_last = now
            cost = mana_cost_per_second * dt
            if player.mana < 10: return
            player.mana -= 10
            game.spawn_particle(player.x, player.y, 20 + player.mag, 'cyan')
            for e in game.room.enemies:
                d = distance((player.x, player.y), (e.x, e.y))
                min_dist = 60 + player.mag
                if d < min_dist:
                    angle = math.atan2(e.y - player.y, e.x - player.x)
                    push_strength = (min_dist - d) * 2
                    e.x += math.cos(angle) * push_strength
                    e.y += math.sin(angle) * push_strength
        def multishot(player, game):
            # Need at least 1 enemy
            if player.mana < 4 or not game.room.enemies: return
            player.mana -= 4
                

            # Pick up to 5 different enemies (closest first)
            enemies = sorted(
                game.room.enemies,
                key=lambda e: distance((player.x, player.y), (e.x, e.y))
            )[:5]

            # Fire an arrow at each target
            for enemy in enemies:
                ang = math.atan2(enemy.y - player.y, enemy.x - player.x)
                game.spawn_projectile(
                    player.x, player.y,
                    ang,
                    7,       # speed
                    3,       # life
                    8,       # radius
                    'brown', # color
                    player.atk * 4,  # damage
                    owner='player',
                    stype='arrow'
                )

        # Assign skills based on class
        self.skills.clear()
        if self.class_name=='Mage':
            self.skills.append({'skill': mana_bolt,'name':'Mana Bolt','key':1,'level':1,'cooldown':0.5,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': mana_shield,'name':'Mana Shield','key':2,'level':5,'cooldown':0,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': fireball,'name':'Fireball','key':3,'level':1,'cooldown':2,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Warrior':
            self.skills.append({'skill': strike,'name':'Rapid Strikes','key':1,'level':1,'cooldown':0,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': ground_pound,'name':'Ground Pound','key':2,'level':5,'cooldown':0.5,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': fist_blast,'name':'Fist Blast','key':3,'level':10,'cooldown':1,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Rogue':
            self.skills.append({'skill': dark_slash,'name':'Dark Slash','key':1,'level':1,'cooldown':0.5,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': shadow_dagger,'name':'Shadow Dagger','key':2,'level':3,'cooldown':0.2,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Cleric':
            self.skills.append({'skill': strike,'name':'Holy Strike','key':1,'level':1,'cooldown':0,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Druid':
            self.skills.append({'skill': strike,'name':'Nature Strike','key':1,'level':1,'cooldown':0,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Monk':
            self.skills.append({'skill': chi_blast,'name':'Chi Strike','key':1,'level':1,'cooldown':1.5,'last_used':0,'cooldown_mod':1.0})
        elif self.class_name=='Ranger':
            self.skills.append({'skill': arrow_shot,'name':'Arrow Shot','key':1,'level':1,'cooldown':0.5,'last_used':0,'cooldown_mod':1.0})
            self.skills.append({'skill': multishot,'name':'Multishot','key':2,'level':3,'cooldown':1,'last_used':0,'cooldown_mod':1.0})


    def gain_xp(self, amount, game=None):
        self.xp += amount
        leveled = False
        levels_gained = 0

        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            levels_gained += 1
            self.stat_points += 2
            self.skill_points += 1
            self.xp_to_next = int(self.xp_to_next * 1.3)

            # Apply class growth
            growth = CLASS_STAT_GROWTH.get(self.class_name, {})
            for stat, value in growth.items():
                setattr(self, stat, getattr(self, stat) + value)

            leveled = True

        # Update player stats after leveling
        if leveled:
            self.update_stats()

            # Scale existing enemies in the current room once
            if game:
                for e in game.room.enemies:
                    if isinstance(e, (Enemy, Boss)):
                        e.scale_with_player(self.level)
                rescale_room_enemies(game.room, self.level)

        return leveled

    def unlock_skills(self):
        for sk in self.skills:
            if sk['level']<=self.level and sk not in self.unlocked_skills:
                if len(self.unlocked_skills)<MAX_SKILLS:
                    self.unlocked_skills.append(sk)

    def to_dict(self):
        return {
            "name": self.name,
            "class_name": self.class_name,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "stat_points": self.stat_points,
            "skill_points": self.skill_points,
            "strength": self.strength,
            "vitality": self.vitality,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "will": self.will,
            "constitution": self.constitution,
            "hp": self.hp,
            "mana": self.mana,
            "unlocked_skills": [sk['name'] for sk in self.unlocked_skills]
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(name=data.get('name','Hero'), class_name=data.get('class_name','Warrior'))
        # Set base stats
        for stat in ['strength','vitality','agility','intelligence','wisdom','will','constitution']:
            if stat in data:
                setattr(p, stat, data[stat])
        p.level = data.get('level',1)
        p.xp = data.get('xp',0)
        p.xp_to_next = data.get('xp_to_next',100)
        p.stat_points = data.get('stat_points',5)
        p.skill_points = data.get('skill_points',0)
        p.update_stats()
        # Re-populate skills
        p.populate_skills()
        # Unlock the saved skills by name
        saved_skills = data.get('unlocked_skills',[])
        for sk in p.skills:
            if sk['name'] in saved_skills:
                p.unlocked_skills.append(sk)
        p.hp = min(data.get('hp', p.max_hp), p.max_hp)
        p.mana = min(data.get('mana', p.max_mana), p.max_mana)
        return p
    def reset(self):
        """Reset character to level 1 and base stats."""
        # Reset core stats
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.stat_points = 5
        self.skill_points = 0

        # Base stats
        base_stats = {'strength':5, 'vitality':5, 'agility':5, 'intelligence':5,
                      'wisdom':5, 'will':5, 'constitution':3}
        for stat, val in base_stats.items():
            setattr(self, stat, val)

        # Clear skills and repopulate for class
        self.skills.clear()
        self.unlocked_skills.clear()
        self.populate_skills()
        self.unlock_skills()

        # Reset HP/Mana
        self.update_stats()
        self.hp = self.max_hp
        self.mana = self.max_mana
# ---------- Enemy/Boss/Projectile/Particle ----------
class Enemy:
    def __init__(self, name, hp, atk, spd, x, y, skills=None):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.spd = spd
        self.x = x
        self.y = y
        self.size = 16
        self.state = 'wander'
        self.wander_target = (x, y)
        self.last_move = time.time()
        self.attack_range = 20
        self.skills = skills or []  # list of dicts: {'skill':func,'cooldown':num,'last_used':time}
        self.attack_cooldown = 1.0
        self.last_attack = 0

    # Add this method to your Enemy class
    def scale_with_player(self, player_level):
        scale_factor = 1 + player_level * 0.1
        self.max_hp = int(self.max_hp * scale_factor)
        self.hp = min(self.hp, self.max_hp)
        self.atk = int(self.atk * scale_factor)
        self.spd = self.spd * (1 + player_level * 0.02)

    def update(self, game):
        now = time.time()
        player = game.player
        d = distance((self.x, self.y), (player.x, player.y))
        self.state = 'chase' if d < 400 else 'wander'

        if self.state == 'chase':
            ang = math.atan2(player.y - self.y, player.x - self.x)
            self.x += math.cos(ang) * self.spd
            self.y += math.sin(ang) * self.spd

            # Pick a usable skill randomly
            usable_skills = []
            for sk in self.skills:
                cd = sk.get('cooldown', 0)
                last = sk.get('last_used', 0)
                if now - last >= cd:
                    usable_skills.append(sk)
            if usable_skills:
                chosen = random.choice(usable_skills)
                chosen['skill'](self, game)
                chosen['last_used'] = now
            # fallback basic attack if in range
            elif d <= self.attack_range and now - self.last_attack >= self.attack_cooldown:
                game.damage_player(self.atk)
                self.last_attack = now

        else:
            if now - self.last_move > 2:
                self.wander_target = (self.x + random.uniform(-50, 50), self.y + random.uniform(-50, 50))
                self.last_move = now
            ang = math.atan2(self.wander_target[1] - self.y, self.wander_target[0] - self.x)
            self.x += math.cos(ang) * self.spd * 0.5
            self.y += math.sin(ang) * self.spd * 0.5
        def gain_xp(self, amount, game=None):
            self.xp += amount
            leveled = False
            while self.xp >= self.xp_to_next:
                self.xp -= self.xp_to_next
                self.level += 1
                self.stat_points += 2
                self.skill_points += 1
                self.xp_to_next = int(self.xp_to_next * 1.3)
                leveled = True
                growth = CLASS_STAT_GROWTH.get(self.class_name, {})
                for stat, value in growth.items():
                    setattr(self, stat, getattr(self, stat) + value)

            self.update_stats()

            # Scale current enemies if game instance is passed
            if leveled and game:
                for e in game.room.enemies:
                    if isinstance(e, Enemy):
                        e.scale_with_player(self.level)

            return leveled


# Enemy skills
def claw_slash(enemy, game):
    # Deals melee damage in a small radius with swipe effect
    arc_radius = 40
    num_particles = 8
    angle_center = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    arc_width = math.pi / 2
    for i in range(num_particles):
        angle = angle_center - arc_width/2 + (i / (num_particles-1)) * arc_width
        x = enemy.x + math.cos(angle) * arc_radius * random.uniform(0.8, 1.2)
        y = enemy.y + math.sin(angle) * arc_radius * random.uniform(0.8, 1.2)
        game.spawn_particle(x, y, random.uniform(5,10), 'green')
    # Deal damage to player if in arc
    if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= arc_radius:
        game.damage_player(enemy.atk * 1.5)
def fire_slash(enemy, game):
    # Deals melee damage in a small radius with swipe effect
    arc_radius = 40
    num_particles = 8
    angle_center = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    arc_width = math.pi / 2
    for i in range(num_particles):
        angle = angle_center - arc_width/2 + (i / (num_particles-1)) * arc_width
        x = enemy.x + math.cos(angle) * arc_radius * random.uniform(0.8, 1.2)
        y = enemy.y + math.sin(angle) * arc_radius * random.uniform(0.8, 1.2)
        game.spawn_particle(x, y, random.uniform(5,10), 'orange')
    # Deal damage to player if in arc
    if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= arc_radius:
        game.damage_player(enemy.atk * 1.5)

def fire_spit(enemy, game):
    ang = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    # Add flame particles along path
    for _ in range(5):
        px = enemy.x + random.uniform(-5,5)
        py = enemy.y + random.uniform(-5,5)
        game.spawn_particle(px, py, random.uniform(3,6), 'orange')
    game.spawn_projectile(enemy.x, enemy.y, ang, 6, 2, 15, 'orange', enemy.atk * 2, 'enemy')


def poison_cloud(enemy, game):
    radius = 50 + enemy.atk
    num_particles = 15
    for _ in range(num_particles):
        x = enemy.x + random.uniform(-radius, radius)
        y = enemy.y + random.uniform(-radius, radius)
        game.spawn_particle(x, y, random.uniform(4,8), 'green')
    if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= radius:
        game.damage_player(enemy.atk * 2)

def dark_bolt(enemy, game):
    # Ranged rock projectile
    ang = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    game.spawn_projectile(enemy.x, enemy.y, ang, 20, 2.5, 10, 'purple', enemy.atk * 3, 'enemy')

def life_bolt(enemy, game):
    # If no enemies, do nothing
    if not game.room.enemies:
        return

    # Find enemy that lost the MOST health
    target = max(
        game.room.enemies,
        key=lambda e: (e.max_hp - e.hp)
    )

    # Compute angle toward that enemy
    ang = math.atan2(target.y - enemy.y, target.x - enemy.x)

    # Spawn projectile owned by enemy
    # damage value will be used as "healing"
    game.spawn_projectile(
        enemy.x, enemy.y,
        ang,                # angle toward the target
        20,                 # speed
        2.5,                # life
        10,                 # radius
        'yellow',           # color
        enemy.atk * 3,      # heal amount
        'enemy_lifebolt'    # special owner type
    )

def ice_blast(enemy, game):
    radius = 60
    num_shards = 8
    for i in range(num_shards):
        angle = (i / num_shards) * 2 * math.pi
        x = enemy.x + math.cos(angle) * radius
        y = enemy.y + math.sin(angle) * radius
        game.spawn_particle(x, y, random.uniform(3,6), 'cyan')
    if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= radius:
        game.damage_player(enemy.atk)
        if hasattr(game.player, 'speed'):
            game.player.speed *= 0.7

def summon_minion(enemy, game):
    minionR = 0
    # Spawns a weak minion nearby
    x = enemy.x + random.randint(-30, 30)
    y = enemy.y + random.randint(-30, 30)
    minion = Enemy("Minion", 30, 4, 1.2, x, y)

    game.room.enemies.append(minion)

def dash_strike(enemy, game):
    """Enhanced dash skill: faster, more damage, and adds visual effect."""
    ang = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    
    # Dash movement: double speed
    dash_distance = enemy.spd * 20  # faster than normal
    enemy.x += math.cos(ang) * dash_distance
    enemy.y += math.sin(ang) * dash_distance

    # Visual effect: spawn trailing particles
    for _ in range(8):
        offset_x = enemy.x + random.uniform(-5, 5)
        offset_y = enemy.y + random.uniform(-5, 5)
        size = random.uniform(10, 10)
        game.spawn_particle(offset_x, offset_y, size, 'green')  # can be customized

    # Attack damage
    if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= 25:
        damage = enemy.atk * 2.5  # stronger than before
        game.damage_player(damage)

def rock_throw(enemy, game):
    # Ranged rock projectile
    ang = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
    game.spawn_projectile(enemy.x, enemy.y, ang, 10, 10, 40, 'brown', enemy.atk * 1.5, 'enemy')

def self_heal(enemy, game):
    """Heals the enemy with a visual particle effect."""
    heal_amount = enemy.atk * 1.2
    enemy.hp = min(enemy.max_hp, enemy.hp + heal_amount)

    # Spawn a burst of green particles around the enemy
    num_particles = 12
    radius = enemy.size + 10
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius)
        x = enemy.x + math.cos(angle) * dist
        y = enemy.y + math.sin(angle) * dist
        size = random.uniform(5, 10)
        game.spawn_particle(x, y, size, 'yellow')

    # Optional: make the enemy flash
# claw_slash, fire_spit, poison_cloud, ice_blast, summon_minion, dash_strike, rock_throw, self_heal

def create_enemy_types_by_dungeon():
    return {
        1: [  # Dungeon 1: Forest
            lambda x, y: Enemy("Goblin", 30, 5, 1.5, x, y, skills=[{'skill': claw_slash, 'cooldown': 1.5, 'last_used': 0}]),
            lambda x, y: Enemy("Poison Spider", 25, 4, 2.2, x, y, skills=[{'skill': poison_cloud, 'cooldown': 0.5, 'last_used': 0}]),
            lambda x, y: Enemy("Bandit", 35, 6, 3, x, y, skills=[{'skill': dash_strike, 'cooldown': 2, 'last_used': 0}]),
        ],
        2: [  # Dungeon 2: Volcano
            lambda x, y: Enemy("Fire Imp", 35, 6, 2.0, x, y, skills=[{'skill': fire_slash, 'cooldown': 2, 'last_used': 0}]),
            lambda x, y: Enemy("Flame Elemental", 50, 8, 1.5, x, y, skills=[
                {'skill': fire_spit, 'cooldown': 2, 'last_used': 0},
                
            ]),
            lambda x, y: Enemy("Troll", 100, 12, 0.8, x, y, skills=[
                {'skill': rock_throw, 'cooldown': 5, 'last_used': 0},
                {'skill': self_heal, 'cooldown': 2, 'last_used': 0}
            ]),
        ],
        3: [  # Dungeon 3: Ice Cavern
            lambda x, y: Enemy("Ice Golem", 100, 10, 0.6, x, y, skills=[{'skill': ice_blast, 'cooldown': 0, 'last_used': 0}]),
            lambda x, y: Enemy("Dark Mage", 40, 7, 1.2, x, y, skills=[
                {'skill': dark_bolt, 'cooldown': 2, 'last_used': 0},
                {'skill': ice_blast, 'cooldown': 3, 'last_used': 0}
            ]),
        ],
        4: [  # Dungeon 4: Shadow Realm
            lambda x, y: Enemy("Summoner", 50, 5, 1.0, x, y, skills=[
                {'skill': dark_bolt, 'cooldown': 0.5, 'last_used': 0},
                {'skill': summon_minion, 'cooldown': 10, 'last_used': 0}]),
            lambda x, y: Enemy("Healer", 50, 8, 1.5, x, y, skills=[
                {'skill': life_bolt, 'cooldown': 2, 'last_used': 0}]),
            lambda x, y: Enemy("Venom Lurker", 30, 10, 4, x, y, skills=[
                {'skill': poison_cloud, 'cooldown': 0.3, 'last_used': 0},
                {'skill': dash_strike, 'cooldown': 2, 'last_used': 0},
            
                
            ]),
        ],
    }
def spawn_enemies_for_dungeon(room, dungeon_id, player_level, count=6):
    enemy_pools = create_enemy_types_by_dungeon()
    pool = enemy_pools.get(dungeon_id, [])
    for _ in range(count):
        if not pool:
            break
        et = random.choice(pool)
        x = random.randint(50, WINDOW_W - 50)
        y = random.randint(50, WINDOW_H - 50)
        enemy = et(x, y)

        # Scale stats with player level
        scale_factor = 1 + player_level * 0.2
        enemy.max_hp = int(enemy.max_hp * scale_factor)
        enemy.hp = enemy.max_hp
        enemy.atk = int(enemy.atk * scale_factor)
        enemy.spd *= (1 + player_level * 0.02)

        room.enemies.append(enemy)



class Boss(Enemy):
    def __init__(self, name, x, y, boss_type='Generic', max_hp=500, atk=15, speed=1.2):
        super().__init__(name, max_hp, atk, speed, x, y)
        self.boss_type = boss_type
        self.size = 30
        self.color = 'orange'
        self.skills = []
        self.last_used_skill_time = {}
        self.init_by_type()

    def scale_with_player(self, player_level):
        scale_factor = 1 + player_level * 0.5  # Bosses scale slightly faster
        self.max_hp = int(self.max_hp * scale_factor)
        self.hp = min(self.hp, self.max_hp)
        self.atk = int(self.atk * scale_factor)
        self.spd = self.spd * (1 + player_level * 0.03)
    def init_by_type(self):
        """Assign stats and skills based on boss type"""
        if self.boss_type == 'FireLord':
            self.max_hp += 600
            self.hp = self.max_hp
            self.atk += 40
            self.size = 35
            self.fire_rate = 1.5
            self.skills = [
                {'skill': self.fireball_attack, 'cooldown': 2},
                {'skill': self.flame_wave, 'cooldown': 4},
                {'skill': self.heal, 'cooldown': 3}
            ]
        elif self.boss_type == 'IceGiant':
            self.max_hp += 800
            self.hp = self.max_hp
            self.atk += 60
            self.size = 40
            self.skills = [
                {'skill': self.ice_shard_attack, 'cooldown': 2},
                {'skill': self.freeze_aura, 'cooldown': 4},
                {'skill': self.heal, 'cooldown': 3},
                {'skill': self.ice_blast, 'cooldown': 3}
            ]
        elif self.boss_type == 'ShadowWraith':
            self.max_hp += 500
            self.hp = self.max_hp
            self.atk += 60
            self.size = 10
            self.spd = 9
            self.skills = [
                {'skill': self.direball, 'cooldown': 2},
                {'skill': self.arcane_storm, 'cooldown': 4},
                {'skill': self.heal, 'cooldown': 3}
            ]
        elif self.boss_type == 'EarthTitan':
            self.max_hp += 900
            self.hp = self.max_hp
            self.atk += 80
            self.size = 40
            self.skills = [
                {'skill': self.rock_throw, 'cooldown': 3},
                {'skill': self.poison_rain, 'cooldown': 3},
                {'skill': self.heal, 'cooldown': 3}
            ]
    # ---------- Example Skills ----------
    def fireball_attack(self, game):
        """Shoots a spread of fireballs"""
        player = game.player
        ang = math.atan2(player.y - self.y, player.x - self.x)
        for delta in [-0.2, 0, 0.2]:
            game.spawn_projectile(self.x, self.y, ang + delta, 6, 3, 10, 'orange', self.atk*10, 'enemy')
    def direball(self, game):
        """Shoots a spread of fireballs"""
        player = game.player
        ang = math.atan2(player.y - self.y, player.x - self.x)
        for delta in [-0.2, 0, 0.2]:
            game.spawn_projectile(self.x, self.y, ang + delta, 6, 3, 20, 'purple', self.atk*5, 'enemy')
    def summon_minions(self, game):
        for _ in range(2):
            x = self.x + random.randint(-40, 40)
            y = self.y + random.randint(-40, 40)
            minion = Enemy("FlameElemental", 30, 5, 1.5, x, y)
            game.room.enemies.append(minion)
    def rock_throw(enemy, game):
        # Ranged rock projectile
        ang = math.atan2(game.player.y - enemy.y, game.player.x - enemy.x)
        game.spawn_projectile(enemy.x, enemy.y, ang, 10, 10, 40, 'brown', enemy.atk * 1.5, 'enemy')
    def ice_blast(enemy, game):
        radius = 200
        num_shards = 20
        for i in range(num_shards):
            angle = (i / num_shards) * 2 * math.pi
            x = enemy.x + math.cos(angle) * radius
            y = enemy.y + math.sin(angle) * radius
            game.spawn_particle(x, y, random.uniform(3,6), 'cyan')
        if distance((enemy.x, enemy.y), (game.player.x, game.player.y)) <= radius:
            game.damage_player(self.atk * 10)
            if hasattr(game.player, 'speed'):
                game.player.speed *= 0.7
    def shockwave_slam(self, game):
        radius = 80
        game.spawn_particle(self.x, self.y, 40, 'yellow')  # visual impact
        player = game.player
        if distance((self.x,self.y),(player.x,player.y)) <= radius:
            game.damage_player(self.atk * 2)
            # knockback
            angle = math.atan2(player.y - self.y, player.x - self.x)
            player.x += math.cos(angle) * 30
            player.y += math.sin(angle) * 30
    def poison_rain(self, game):
        for _ in range(5):
            x = self.x + random.uniform(-150, 150)
            y = self.y + random.uniform(-150, 150)
            game.spawn_particle(x, y, 10, 'green')
            if distance((x,y),(game.player.x, game.player.y)) < 20:
                game.damage_player(self.atk * 0.8)

    def flame_wave(self, game):
        """AoE flame around boss"""
        for e in game.room.enemies:
            if e != self: continue
        for _ in range(20):
            x = self.x + random.uniform(-120,120)
            y = self.y + random.uniform(-120,120)
            game.spawn_particle(x, y, random.uniform(5,10), 'red')
        if distance((self.x,self.y),(game.player.x,game.player.y))<120:
            game.damage_player(self.atk*5)
    
    def ice_shard_attack(self, game):
        """Shoots shards in all directions"""
        num_shards = 8
        for i in range(num_shards):
            angle = i/num_shards*2*math.pi
            game.spawn_projectile(self.x, self.y, angle, 5, 2, 8, 'cyan', self.atk*5, 'enemy')

    def freeze_aura(self, game):
        """Slows player if nearby"""
        for _ in range(20):
            x = self.x + random.uniform(-120,120)
            y = self.y + random.uniform(-120,120)
            game.spawn_particle(x, y, random.uniform(5,10), 'cyan')
        if distance((self.x, self.y), (game.player.x, game.player.y)) < 80:
            game.player.speed *= 0.5
            game.spawn_particle(game.player.x, game.player.y, 15, 'blue')
    def heal(enemy, game):
        """Heals the enemy with a visual particle effect."""
        heal_amount = enemy.atk * 20
        enemy.hp = min(enemy.max_hp, enemy.hp + heal_amount)

        # Spawn a burst of green particles around the enemy
        num_particles = 12
        radius = enemy.size + 10
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            x = enemy.x + math.cos(angle) * dist
            y = enemy.y + math.sin(angle) * dist
            size = random.uniform(5, 10)
            game.spawn_particle(x, y, size, 'yellow')

    def arcane_storm(self, game):
        player = game.player
        angle_center = math.atan2(player.y - self.y, player.x - self.x)
        num_proj = 10
        arc_width = math.pi / 2
        for i in range(num_proj):
            angle = angle_center - arc_width/2 + (i / (num_proj-1)) * arc_width
            game.spawn_projectile(self.x, self.y, angle, 5, 3, 8, 'purple', self.atk*10, 'enemy')

    def update(self, dt, game):
        """Move and use skills"""
        # Move towards player
        player = game.player
        ang = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(ang) * self.spd
        self.y += math.sin(ang) * self.spd

        now = time.time()
        # Use skills
        for sk in self.skills:
            last_used = self.last_used_skill_time.get(sk['skill'], 0)
            if now - last_used >= sk['cooldown']:
                sk['skill'](game)
                self.last_used_skill_time[sk['skill']] = now
def spawn_boss_for_room(room, dungeon_id):
    boss_x, boss_y = WINDOW_W//2, WINDOW_H//2
    boss_types = {
        1: 'EarthTitan',
        2: 'FireLord',
        3: 'IceGiant',
        4: 'ShadowWraith'
    }
    boss_name = f"Dungeon {dungeon_id} Boss"
    boss_type = boss_types.get(dungeon_id, 'Generic')
    boss = Boss(boss_name, boss_x, boss_y, boss_type)
    room.enemies.append(boss)

class Projectile:
    def __init__(self,x,y,angle,speed,life,radius,color,damage,owner='player', ptype='normal', stype='basic'):
        self.x=x; self.y=y; self.angle=angle; self.speed=speed
        self.life=life; self.radius=radius; self.color=color; self.damage=damage; self.owner=owner
        self.ptype = ptype; self.stype = stype 
    def update(self,dt,game):
        self.x += math.cos(self.angle)*self.speed
        self.y += math.sin(self.angle)*self.speed
        self.life -= dt
        if self.x<0 or self.x>WINDOW_W or self.y<0 or self.y>WINDOW_H: self.life=0; return
        if self.owner=='player':
            for e in list(game.room.enemies):
                if distance((self.x,self.y),(e.x,e.y))<=self.radius+e.size:
                    if self.ptype == 'fireball':
                        for e in list(game.room.enemies):
                            if distance((self.x, self.y), (e.x, e.y)) <= self.radius + e.size:
                                # Spawn big orange circle
                                aoe_radius = 50
                                for _ in range(20):
                                    angle = random.uniform(0, 2*math.pi)
                                    dist = random.uniform(0, aoe_radius)
                                    px = e.x + math.cos(angle) * dist
                                    py = e.y + math.sin(angle) * dist
                                    size = random.uniform(10, 20)
                                    game.spawn_particle(px, py, size, 'orange')
                                    size = random.uniform(10, 20)
                                    game.spawn_particle(px, py, size, 'red')
                                
                                # Damage nearby enemies
                                for en in list(game.room.enemies):
                                    if distance((e.x, e.y), (en.x, en.y)) <= aoe_radius:
                                        game.damage_enemy(en, self.damage)

                                self.life = 0
                                return

                    else:
                        game.damage_enemy(e,self.damage); self.life=0; return
        elif self.owner=='enemy':
            p=game.player
            if distance((self.x,self.y),(p.x,p.y))<=self.radius+p.size:
                game.damage_player(self.damage); self.life=0; return
        elif self.owner == 'enemy_lifebolt':
            # home target = most injured enemy
            if game.room.enemies:
                target = max(
                    game.room.enemies,
                    key=lambda e: (e.max_hp - e.hp)
                )

                # Check collision with that target
                if distance((self.x, self.y), (target.x, target.y)) <= self.radius + target.size:
                    # Heal enemy instead of damage
                    target.hp = min(target.max_hp, target.hp + self.damage)
                    return
        def spawn_aoe_fire(self, game, target_enemy):
            """Spawn a big orange AoE circle at the enemy's position."""
            aoe_radius = 50  # size of explosion
            num_particles = 20

            # Damage all enemies in the AoE
            for e in list(game.room.enemies):
                if distance((target_enemy.x, target_enemy.y), (e.x, e.y)) <= aoe_radius:
                    game.damage_enemy(e, self.damage)

            # Spawn visual particles
            for _ in range(num_particles):
                angle = random.uniform(0, 2*math.pi)
                dist = random.uniform(0, aoe_radius)
                x = target_enemy.x + math.cos(angle) * dist
                y = target_enemy.y + math.sin(angle) * dist
                size = random.uniform(5, 15)
                game.spawn_particle(x, y, size, 'orange')

class Particle:
    def __init__(self,x,y,size,color,life=0.5):
        self.x=x; self.y=y; self.size=size; self.color=color; self.life=life
    def update(self,dt): self.life-=dt

# ---------- Room ----------
class Room:
    def __init__(self, row, col, dungeon_id=1, player_level=1):
        self.row = row
        self.col = col
        self.enemies = []

        if (row, col) == (0, 0):  # starting room empty
            return

        depth = row + col
        # Spawn enemies scaled to player level
        spawn_enemies_for_dungeon(self, dungeon_id, player_level, count=4 + depth)

        if row == 0 and col == 4:
            spawn_boss_for_room(self, dungeon_id)

# ---------- GameFrame: playable game ----------
class GameFrame(tk.Frame):
    def __init__(self,parent,player,on_quit_to_menu,dungeon_id=1):
        super().__init__(parent)
        self.parent = parent
        self.player = player
        self.on_quit_to_menu = on_quit_to_menu
        self.dungeon_id = dungeon_id 
        self.canvas = tk.Canvas(self,width=WINDOW_W,height=WINDOW_H,bg='black')
        self.canvas.pack()
        self.keys = {}
        self.room_row=0; self.room_col=0
        self.dungeon={}
        self.room=self.get_room(0,0)
        self.projectiles=[]; self.particles=[]
        self.mouse_pos=(WINDOW_W//2,WINDOW_H//2)
        self.show_stats=False
        self.dead=False; self.respawn_time=0; self.respawn_delay=5
    
        self.bind_all('<KeyPress>', self.on_key_down)
        self.bind_all('<KeyRelease>', self.on_key_up)
        self.canvas.bind('<Button-1>', self.handle_stat_click)

        self.last_time=time.time()
        self.after(16,self.loop)

    def get_room(self, row, col):
        key = (row, col)
        if key not in self.dungeon:
            self.dungeon[key] = Room(row, col, self.dungeon_id, player_level=self.player.level)
        return self.dungeon[key]

    def on_key_down(self,e):
        self.keys[e.keysym]=True
        if e.keysym.lower()=='p': self.show_stats = not self.show_stats
        if e.keysym=='Escape': self.on_quit_to_menu()

    def on_key_up(self,e): self.keys[e.keysym]=False

    def spawn_projectile(self, x, y, angle, speed, life, radius, color, damage, owner="player", ptype='normal', stype="basic"):
        self.projectiles.append(Projectile(x, y, angle, speed, life, radius, color, damage, owner, ptype, stype))


    def spawn_particle(self,x,y,size,color):
        self.particles.append(Particle(x,y,size,color))

    def damage_player(self,amount):
        if self.dead: return
        amount = max(0, amount - self.player.constitution)
        self.player.hp -= amount
        if self.player.hp <=0:
            self.dead=True
            self.respawn_time=self.respawn_delay
            print("You died! Respawning...")

    def damage_enemy(self,e,amount):
        e.hp -= amount
        if e.hp <=0 and e in self.room.enemies:
            self.player.gain_xp(e.max_hp*2)
            self.room.enemies.remove(e)

    def update_entities(self,dt):
        for e in list(self.room.enemies):
            if isinstance(e, Boss):
                e.update(dt, self)
            else:
                e.update(self)  # <--- CHANGE TO: e.update(self)
        for p in list(self.projectiles): p.update(dt,self)
        self.projectiles=[p for p in self.projectiles if p.life>0]
        for part in self.particles: part.update(dt)
        self.particles=[p for p in self.particles if p.life>0]
        self.player.unlock_skills()

    def update_player(self,dt):
        p=self.player
        p.hp=min(p.max_hp, p.hp+p.hp_regen*dt)
        p.mana=min(p.max_mana, p.mana+p.mana_regen*dt)

        if self.dead:
            self.respawn_time -= dt
            if self.respawn_time<=0:
                p.x = WINDOW_W//2; p.y = WINDOW_H//2
                p.hp = p.max_hp; p.mana = p.max_mana
                self.dead=False
                self.room_row=0; self.room_col=0; self.room=self.get_room(0,0)
                print("Respawned!")
            return

        # movement
        if self.keys.get('w'): p.y -= p.speed
        if self.keys.get('s'): p.y += p.speed
        if self.keys.get('a'): p.x -= p.speed
        if self.keys.get('d'): p.x += p.speed
        if self.keys.get('Up'):
            p.y -= p.speed
        if self.keys.get('Down'):
            p.y += p.speed
        if self.keys.get('Left'):
            p.x -= p.speed
        if self.keys.get('Right'):
            p.x += p.speed

        # room transitions
        if p.x<0:
            self.room_col=max(0,self.room_col-1); p.x=WINDOW_W-10; self.room=self.get_room(self.room_row,self.room_col)
        if p.x>WINDOW_W:
            self.room_col=min(ROOM_COLS-1,self.room_col+1); p.x=10; self.room=self.get_room(self.room_row,self.room_col)
        if p.y<0:
            self.room_row=max(0,self.room_row-1); p.y=WINDOW_H-10; self.room=self.get_room(self.room_row,self.room_col)
        if p.y>WINDOW_H:
            self.room_row=min(ROOM_ROWS-1,self.room_row+1); p.y=10; self.room=self.get_room(self.room_row,self.room_col)
        p.x=clamp(p.x,0,WINDOW_W); p.y=clamp(p.y,0,WINDOW_H)

        # skills usage
        now=time.time()
        for sk in p.unlocked_skills:
            key=str(sk['key'])
            if self.keys.get(key) or self.keys.get('KP_'+key):
                base_cd = sk.get('cooldown',0); mod=sk.get('cooldown_mod',1.0)
                last_used=sk.get('last_used',0)
                effective_cd = base_cd*mod
                if effective_cd<=0:
                    sk['skill'](p,self); sk['last_used']=now
                elif now-last_used>=effective_cd:
                    sk['skill'](p,self); sk['last_used']=now
                    sk['cooldown_mod']=max(0.2, mod*0.995)

    def handle_stat_click(self,event):
        if not self.show_stats or self.player.stat_points<=0: return
        mx,my=event.x,event.y
        stat_y_start=120; stat_height=30
        stats=['strength','vitality','agility','constitution','intelligence','wisdom','will']
        for i,stat in enumerate(stats):
            btn_x=600; btn_y=stat_y_start+i*stat_height
            btn_w,btn_h=30,20
            if btn_x<mx<btn_x+btn_w and btn_y<my<btn_y+btn_h:
                setattr(self.player,stat,getattr(self.player,stat)+1)
                self.player.stat_points -= 1
                self.player.update_stats()

    def draw(self):
        self.canvas.delete('all')
        px, py = self.player.x, self.player.y
        size = 12
        self.canvas.create_oval(px-size-2, py-size-2, px+size+2, py+size+2, fill='white')  # outline
        self.canvas.create_oval(px-size, py-size, px+size, py+size, fill='cyan')           # player body

        for e in self.room.enemies:
            ex, ey = e.x, e.y
            if isinstance(e, Boss):
                boss_shapes = {
                    "FireLord": ("rectangle", "orange"),
                    "IceGiant": ("diamond", "cyan"),
                    "ShadowWraith": ("triangle", "purple"),
                    "EarthTitan": ("oval", "brown"),
                }
                outline_width = 3  # thickness of outline
                outline_color = "white"
                shape, color = boss_shapes.get(e.boss_type, ("oval", "orange"))

                size = e.size

                if shape == "oval":
                    self.canvas.create_oval(
                        ex-size, ey-size, ex+size, ey+size,
                        fill=color, outline=outline_color, width=outline_width
                    )

                elif shape == "rectangle":
                    self.canvas.create_rectangle(
                        ex-size, ey-size, ex+size, ey+size,
                        fill=color, outline=outline_color, width=outline_width
                    )

                elif shape == "triangle":
                    points = [ex, ey-size, ex+size, ey+size, ex-size, ey+size]
                    self.canvas.create_polygon(
                        points, fill=color, outline=outline_color, width=outline_width
                    )

                elif shape == "diamond":
                    points = [ex, ey-size, ex+size, ey, ex, ey+size, ex-size, ey]
                    self.canvas.create_polygon(
                        points, fill=color, outline=outline_color, width=outline_width
                    )

                continue


            enemy_shapes = {
                "Goblin": ("oval", "green"),
                "Poison Spider": ("hexagon", "purple"),
                "Bandit": ("rectangle", "brown"),
                "Fire Imp": ("triangle", "orange"),
                "Flame Elemental": ("diamond", "red"),
                "Troll": ("rectangle", "darkgray"),
                "Ice Golem": ("square", "cyan"),
                "Dark Mage": ("triangle", "purple"),
                "Summoner": ("oval", "pink"),
                "Venom Lurker": ("oval", "lime"),
                "Healer": ("triangle", "yellow"),
            }

            shape, color = enemy_shapes.get(e.name, ("oval", "gray"))

            if shape == "oval":
                self.canvas.create_oval(ex-e.size, ey-e.size, ex+e.size, ey+e.size, fill=color)
            elif shape == "rectangle":
                self.canvas.create_rectangle(ex-e.size, ey-e.size, ex+e.size, ey+e.size, fill=color)
            elif shape == "triangle":
                points = [ex, ey-e.size, ex+e.size, ey+e.size, ex-e.size, ey+e.size]
                self.canvas.create_polygon(points, fill=color)
            elif shape == "square":
                self.canvas.create_rectangle(ex-e.size, ey-e.size, ex+e.size, ey+e.size, fill=color)
            elif shape == "diamond":
                points = [ex, ey-e.size, ex+e.size, ey, ex, ey+e.size, ex-e.size, ey]
                self.canvas.create_polygon(points, fill=color)
            elif shape == "hexagon":
                points = [
                    ex, ey-e.size,
                    ex+e.size*0.87, ey-e.size*0.5,
                    ex+e.size*0.87, ey+e.size*0.5,
                    ex, ey+e.size,
                    ex-e.size*0.87, ey+e.size*0.5,
                    ex-e.size*0.87, ey-e.size*0.5
                ]
                self.canvas.create_polygon(points, fill=color)

            # Draw health above the enemy
            health_text = f"{e.hp}/{e.max_hp}"
            self.canvas.create_text(ex, ey - e.size - 10, text=health_text, fill='white')
            
        boss_in_room = None
        for e in self.room.enemies:
            if isinstance(e, Boss):
                boss_in_room = e
                break

        if boss_in_room:
            # Draw boss health bar at top
            bar_width = 400
            bar_height = 20
            x0 = (WINDOW_W - bar_width)//2
            y0 = 20
            hp_frac = boss_in_room.hp / boss_in_room.max_hp if boss_in_room.max_hp else 0
            self.canvas.create_rectangle(x0, y0, x0+bar_width, y0+bar_height, fill='gray')
            self.canvas.create_rectangle(x0, y0, x0 + int(bar_width*hp_frac), y0+bar_height, fill='red')
            self.canvas.create_text(WINDOW_W//2, y0 + bar_height//2, text=f"{boss_in_room.name}", fill='white', font=('Arial','12','bold'))
            health_text = f"{boss_in_room.hp}/{boss_in_room.max_hp}"
            self.canvas.create_text(ex, ey - e.size - 5, text=health_text, fill='white')

        

        for proj in self.projectiles:
            x, y, r = proj.x, proj.y, proj.radius
            if proj.stype == 'basic':
                # Simple circle
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=proj.color)
            if proj.stype == 'arrow':
                angle = proj.angle
                x, y = proj.x, proj.y
                r = proj.radius  # base radius
                scale = 0.4  # shrink factor

                # ----- Arrow tip (triangle) -----
                tip_length = r * 4 * scale
                tip = [
                    x + math.cos(angle) * tip_length, y + math.sin(angle) * tip_length,  # tip point
                    x - math.cos(angle + math.pi/6) * tip_length/2, y - math.sin(angle + math.pi/6) * tip_length/2 - 1,  # left base
                    x - math.cos(angle - math.pi/6) * tip_length/2, y - math.sin(angle - math.pi/6) * tip_length/2 + 1  # right base
                ]
                self.canvas.create_polygon(tip, fill='gray')  # tip gray

                # ----- Arrow shaft (rectangle) -----
                shaft_length = tip_length * 1.5
                shaft_width = r / 2 * scale
                perp_angle = angle + math.pi / 2
                corners = [
                    x - math.cos(perp_angle) * shaft_width - math.cos(angle) * shaft_length, y - math.sin(perp_angle) * shaft_width - math.sin(angle) * shaft_length,
                    x + math.cos(perp_angle) * shaft_width - math.cos(angle) * shaft_length, y + math.sin(perp_angle) * shaft_width - math.sin(angle) * shaft_length,
                    x + math.cos(perp_angle) * shaft_width, y + math.sin(perp_angle) * shaft_width,
                    x - math.cos(perp_angle) * shaft_width, y - math.sin(perp_angle) * shaft_width
                ]
                self.canvas.create_polygon(corners, fill=proj.color)

                # ----- Fletching at the back -----
                fletch_length = r * 3 * scale
                fletch_width = r * scale
                back_x = x - math.cos(angle) * shaft_length
                back_y = y - math.sin(angle) * shaft_length

                fletch_angles = [-math.pi/8, 0, math.pi/8]
                for fa in fletch_angles:
                    ftip_x = back_x - math.cos(angle + fa) * fletch_length
                    ftip_y = back_y - math.sin(angle + fa) * fletch_length
                    base1_x = back_x - math.cos(angle + fa + math.pi/2) * fletch_width/2
                    base1_y = back_y - math.sin(angle + fa + math.pi/2) * fletch_width/2
                    base2_x = back_x + math.cos(angle + fa + math.pi/2) * fletch_width/2
                    base2_y = back_y + math.sin(angle + fa + math.pi/2) * fletch_width/2
                    self.canvas.create_polygon([ftip_x, ftip_y, base1_x, base1_y, base2_x, base2_y], fill='white')

            elif proj.stype == 'dagger':
                # Arrow = triangle + rectangle + triangle along angle
                length = r*4
                width = r
                # Tip triangle
                tip = [
                    x + math.cos(proj.angle)*length/2, y + math.sin(proj.angle)*length/2,
                    x + math.cos(proj.angle + 2.5)*width, y + math.sin(proj.angle + 2.5)*width,
                    x + math.cos(proj.angle - 2.5)*width, y + math.sin(proj.angle - 2.5)*width
                ]
                self.canvas.create_polygon(tip, fill=proj.color)
                # Shaft rectangle
                x1 = x - math.cos(proj.angle)*length/2
                y1 = y - math.sin(proj.angle)*length/2
                self.canvas.create_rectangle(x1-width/2, y1-width/2, x1+width/2, y1+width/2, fill=proj.color)
            elif proj.stype == 'bolt':
                # Long rectangle
                length = r*6
                width = r*1.5
                x1 = x - math.cos(proj.angle)*length/2
                y1 = y - math.sin(proj.angle)*length/2
                x2 = x + math.cos(proj.angle)*length/2
                y2 = y + math.sin(proj.angle)*length/2
                # Compute perpendicular offset for width
                dx = math.sin(proj.angle)*width/2
                dy = -math.cos(proj.angle)*width/2
                points = [x1-dx, y1-dy, x1+dx, y1+dy, x2+dx, y2+dy, x2-dx, y2-dy]
                self.canvas.create_polygon(points, fill=proj.color)


        for part in self.particles:
            self.canvas.create_oval(part.x-part.size,part.y-part.size,part.x+part.size,part.y+part.size,fill=part.color)

        # HUD: HP/Mana/XP
        self.canvas.create_rectangle(10,10,210,30,fill='gray')
        hpw=int((self.player.hp/self.player.max_hp)*200) if self.player.max_hp else 0
        self.canvas.create_rectangle(10,10,10+hpw,30,fill='red')

        self.canvas.create_rectangle(10,35,210,55,fill='gray')
        mw=int((self.player.mana/self.player.max_mana)*200) if self.player.max_mana else 0
        self.canvas.create_rectangle(10,35,10+mw,55,fill='blue')

        self.canvas.create_rectangle(10,60,210,70,fill='gray')
        xpw=int((self.player.xp/self.player.xp_to_next)*200) if self.player.xp_to_next else 0
        self.canvas.create_rectangle(10,60,10+xpw,70,fill='green')
        self.canvas.create_text(220,60,text=f'LV {self.player.level}',fill='white',anchor='nw')
        
        # Skills icons + cooldown overlay
        now=time.time()
        for i,sk in enumerate(self.player.unlocked_skills[:6]):
            x0=10+i*60; y0=80; size=50
            self.canvas.create_rectangle(x0,y0,x0+size,y0+size,fill='blue')
            base_cd=sk.get('cooldown',0); mod=sk.get('cooldown_mod',1.0); last_used=sk.get('last_used',0)
            effective_cd=base_cd*mod
            cd_remaining=max(0,effective_cd-(now-last_used))
            if effective_cd>0 and cd_remaining>0:
                frac=clamp(cd_remaining/effective_cd,0.0,1.0)
                overlay_h=int(size*frac)
                self.canvas.create_rectangle(x0,y0,x0+size,y0+overlay_h,fill='grey')
            self.canvas.create_text(x0+size/2,y0+size/2,text=sk['name'][0],fill='white')

        if self.show_stats: self.draw_stats_panel()
        self.canvas.create_text(650,10,text=f'Room: ({self.room_row},{self.room_col})',fill='white')
    def draw_minimap(self):
        map_x, map_y = WINDOW_W - 120, 10
        cell_size = 20
        
        for row in range(ROOM_ROWS):
            for col in range(ROOM_COLS):
                x0 = map_x + col * cell_size
                y0 = map_y + row * cell_size
                
                color = 'green' if (row, col) == (self.room_row, self.room_col) else 'gray'
                if (row, col) in self.dungeon:
                    color = 'lightblue' if (row, col) != (self.room_row, self.room_col) else 'green'
                
                self.canvas.create_rectangle(x0, y0, x0+cell_size, y0+cell_size, 
                                            fill=color, outline='white')
                # Skills icons + cooldown overlay
    def draw_stats_panel(self):
        p=self.player
        self.canvas.create_rectangle(100,100,700,500,fill='#222')
        stats=['strength','vitality','agility','constitution','intelligence','wisdom','will',]
        y_start=120; stat_height=30
        for i,stat in enumerate(stats):
            val=getattr(p,stat)
            self.canvas.create_text(120,y_start+i*stat_height,anchor='nw',text=f'{stat.upper()}: {val}',fill='white',font=('Arial','14'))
            if p.stat_points>0:
                self.canvas.create_rectangle(600,y_start+i*stat_height,630,y_start+i*stat_height+20,fill='green')
                self.canvas.create_text(615,y_start+i*stat_height+10,text='+',fill='white')
        self.canvas.create_text(120,350,text=f'                                              Stat Points Available: {p.stat_points}',fill='yellow',font=('Arial','14'))

    def loop(self):
        now=time.time(); dt=now-self.last_time; self.last_time=now
        self.update_player(dt)
        self.update_entities(dt)
        self.draw()
        self.after(16,self.loop)
# ---------- Main window with Home Screen ----------
class MainApp(tk.Tk):
    SAVE_FILE = "player_save.json"

    def reset_character(self):
        if not hasattr(self, 'preview_player'):
            return
        from tkinter import messagebox
        if messagebox.askyesno("Reset Character", "Are you sure you want to reset your character?"):
            self.preview_player.reset()
            self.class_chosen = False  # allow class selection again
            self.update_preview()
            # Rebuild home to show class buttons again
            self.build_home()
            self.save_player(self.preview_player.to_dict())

    def __init__(self):
        super().__init__()
        self.title("Dungeon LitRPG - Hub")
        self.geometry("900x700")
        self.resizable(False, False)

        self.class_chosen = False  # NEW: track if player has chosen a class

        self.player_data = self.load_player() or {"name": "Hero", "class_name": ""}
        self.selected_class = self.player_data.get("class_name", "")
        if self.selected_class:
            self.class_chosen = True

        self.name_var = tk.StringVar(value=self.player_data.get("name", "Hero"))
        self.preview_player = Player(self.name_var.get(), self.selected_class or "Warrior")
        self.preview_player.unlock_skills()

        self.home_frame = ttk.Frame(self)
        self.home_frame.pack(fill='both', expand=True)
        self.game_frame_container = None

        self.build_home()

    def build_home(self):
        for w in self.home_frame.winfo_children(): w.destroy()
        title = ttk.Label(self.home_frame, text="Dungeon Hub", font=("Arial", 24))
        title.pack(pady=10)

        top = ttk.Frame(self.home_frame); top.pack(pady=8)
        ttk.Label(top, text="Name:").grid(row=0, column=0, sticky='e')
        ttk.Entry(top, textvariable=self.name_var, width=20).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(top, text="Class:").grid(row=0, column=2, sticky='e', padx=(20,0))

        # Class buttons frame
        self.class_buttons_frame = ttk.Frame(top)
        self.class_buttons_frame.grid(row=0, column=3, sticky='w')
        self.class_buttons = []

        if not self.class_chosen:
            classes = ['Warrior','Mage','Rogue','Cleric','Druid','Monk','Ranger']
            for cls in classes:
                b = ttk.Button(self.class_buttons_frame, text=cls, command=lambda c=cls: self.choose_class(c))
                b.pack(side='left', padx=4)
                self.class_buttons.append(b)

        # Reset button
        ttk.Button(self.home_frame, text="Reset Character", width=30, command=self.reset_character).pack(pady=4)

        # Preview panel
        preview = ttk.LabelFrame(self.home_frame, text="Player Preview", padding=10)
        preview.pack(pady=10, fill='x', padx=20)
        self.preview_text = tk.Text(preview, height=7, width=70, bg='#111', fg='white')
        self.preview_text.pack(padx=4, pady=4)
        self.update_preview()

        # Dungeon selection
        dungeon_frame = ttk.LabelFrame(self.home_frame, text="Dungeons", padding=10)
        dungeon_frame.pack(pady=10)
        for i in range(1,5):
            ttk.Button(dungeon_frame, text=f"Dungeon {i} ", width=30,
                       command=lambda d=i: self.start_dungeon(d)).pack(pady=4)

    def choose_class(self, cls):
        self.selected_class = cls
        self.class_chosen = True  # mark that class has been chosen
        self.preview_player = Player(self.name_var.get(), cls)
        self.preview_player.unlock_skills()
        self.update_preview()
        # hide buttons
        for b in self.class_buttons:
            b.pack_forget()

    def update_preview(self):
        p = self.preview_player
        lines = [
            f"Name: {p.name}",
            f"Class: {p.class_name}",
            f"Level: {p.level}  XP: {p.xp}/{p.xp_to_next}",
            f"HP: {p.max_hp}   Mana: {p.max_mana}",
            f"STR:{p.strength}  VIT:{p.vitality}  AGI:{p.agility}  CON:{p.constitution}  INT:{p.intelligence}  WIS:{p.wisdom}  WIL:{p.will}",
            "Unlocked Skills: " + (", ".join(sk['name'] for sk in p.unlocked_skills) if p.unlocked_skills else "(none)")
        ]
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert(tk.END, "\n".join(lines))

    def quit_to_menu(self):
        if self.game_frame_container:
            player = self.game_frame_container.player
            self.save_player(player.to_dict())
            self.preview_player = player  # update preview with last played player
            self.game_frame_container.destroy()
            self.game_frame_container = None

        self.home_frame.pack(fill='both', expand=True)
        self.build_home()
    def start_dungeon(self, dungeon_id):
        player = Player.from_dict(self.preview_player.to_dict())
        self.home_frame.pack_forget()
        if self.game_frame_container:
            self.game_frame_container.destroy()
        # pass dungeon_id here
        self.game_frame_container = GameFrame(self, player, on_quit_to_menu=self.quit_to_menu, dungeon_id=dungeon_id)
        self.game_frame_container.pack()
    # ---------- Saving / Loading ----------
    def save_player(self,data):
        try:
            with open(self.SAVE_FILE,'w') as f: json.dump(data,f)
        except Exception as e:
            print("Error saving player:", e)

    def load_player(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE,'r') as f: return json.load(f)
            except Exception as e:
                print("Error loading player:", e)
        return None

if __name__=="__main__":
    app = MainApp()
    app.mainloop()



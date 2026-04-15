import tkinter as tk
from tkinter import simpledialog
import random, math, time

# ---------- Config ----------
WINDOW_W = 800
WINDOW_H = 600
ROOM_ROWS = 5
ROOM_COLS = 5
MAX_SKILLS = 9

# ---------- Class-based automatic stat growth ----------
CLASS_STAT_GROWTH = {
    'Warrior': {'strength': 1, 'vitality': 1, 'agility': 1, 'intelligence': 0, 'wisdom': 0, 'will': 0},
    'Mage':    {'strength': 0, 'vitality': 0, 'agility': 0, 'intelligence': 1, 'wisdom': 1, 'will': 1},
    'Rogue':   {'strength': 1, 'vitality': 0, 'agility': 2, 'intelligence': 0, 'wisdom': 1, 'will': 0},
}

# ---------- Utilities ----------
def clamp(v,a,b): return max(a,min(b,v))
def distance(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

# ---------- Player ----------
class Player:
    def __init__(self,name='Hero',class_name='Warrior'):
        self.name=name; self.class_name=class_name
        self.x=WINDOW_W//2; self.y=WINDOW_H//2; self.size=16
        # Stats
        self.strength=5; self.vitality=5; self.agility=5
        self.intelligence=5; self.wisdom=5; self.will=5
        self.update_stats()
        # Leveling
        self.level=1; self.xp=0; self.xp_to_next=100
        self.stat_points=5; self.skill_points=0
        # Skills
        self.skills=[]; self.unlocked_skills=[]
        self.populate_skills()
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
        # All possible skills
        def dark_slash(player, game):
            if player.mana < 5 or not game.room.enemies:
                return  # Not enough mana or no enemies
            player.mana -= 5

            # Find nearest enemy
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            angle_center = math.atan2(target.y - player.y, target.x - player.x)

            # Spawn slash particles in a short arc in front of player
            num_particles = 6
            arc_radius = 50  # range of attack
            arc_width = math.pi / 3  # 60 degree slash
            px, py = player.x, player.y

            for i in range(num_particles):
                angle = angle_center - arc_width/2 + (i / (num_particles-1)) * arc_width
                x = px + math.cos(angle) * arc_radius * random.uniform(0.7, 1.0)
                y = py + math.sin(angle) * arc_radius * random.uniform(0.7, 1.0)
                size = random.uniform(5, 10)
                game.spawn_particle(x, y, size, 'purple')

            # Damage enemies within the arc
                for e in list(game.room.enemies):
                    dx, dy = e.x - px, e.y - py
                    dist = math.hypot(dx, dy)
                    if dist <= arc_radius:
                        angle_to_enemy = math.atan2(dy, dx)
                        diff = (angle_to_enemy - angle_center + math.pi*2) % (math.pi*2)
                        if diff < arc_width/2 or diff > math.pi*2 - arc_width/2:
                            game.damage_enemy(e, player.atk * 1.5)  # rogue melee damage
 

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
            # Auto-aim at nearest enemy
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 1.0, 8, 'brown', player.atk*5)
        def shadow_dagger(player, game):
            if player.mana < 5 or not game.room.enemies: return
            player.mana -= 5
            # Auto-aim at nearest enemy
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 6, 1.0, 8, 'purple', player.atk*2)
        def fireball(player, game):
            if player.mana < 10 or not game.room.enemies: return
            player.mana -= 10
            target = min(game.room.enemies, key=lambda e: distance((player.x, player.y), (e.x, e.y)))
            ang = math.atan2(target.y - player.y, target.x - player.x)
            game.spawn_projectile(player.x, player.y, ang, 5, 2.0, 30 + player.mag, 'orange', player.mag*5)

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
            game.spawn_projectile(player.x, player.y, ang, 6, 3, 8, 'white', player.mag*2)
        def mana_shield(player, game):
            mana_cost_per_second = 5  # Mana consumed per second
            if player.mana <= 0:
                return  # stop if no mana left

            # Consume mana based on frame time
            now = time.time()
            if not hasattr(player, '_mana_shield_last'):
                player._mana_shield_last = now
            dt = now - player._mana_shield_last
            player._mana_shield_last = now

            cost = mana_cost_per_second * dt
            if player.mana < 10:
                return
            player.mana -= 10

            game.spawn_particle(player.x, player.y, 20 + player.mag, 'cyan')

            # Push enemies away if they are too close
            for e in game.room.enemies:
                d = distance((player.x, player.y), (e.x, e.y))
                min_dist = 60 + player.mag  # radius of shield
                if d < min_dist:
                    angle = math.atan2(e.y - player.y, e.x - player.x)
                    push_strength = (min_dist - d) * 2  # stronger push if closer
                    e.x += math.cos(angle) * push_strength
                    e.y += math.sin(angle) * push_strength


        # Add skills depending on class
        if self.class_name == 'Mage':
            self.skills.append({'skill': fireball, 'name': 'Fireball', 'key': 3, 'level': 5, 'cooldown': 1.5, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': mana_bolt, 'name': 'Mana Bolt', 'key': 1, 'level': 1, 'cooldown': 0.8, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': ice_shard, 'name': 'Ice Shard', 'key': 4, 'level': 10, 'cooldown': 2, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': mana_shield, 'name': 'Mana Shield', 'key': 2, 'level': 3, 'cooldown': 0, 'last_used': 0,  'cooldown_mod': 1.0})

        if self.class_name == 'Warrior':
            self.skills.append({'skill': ground_pound, 'name': 'Ground Pound', 'key': 2, 'level': 3, 'cooldown': 0.5, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': fist_blast, 'name': 'Fist Blast', 'key': 3, 'level': 5, 'cooldown': 0.5, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': strike, 'name': 'Rapid Strikes', 'key': 1, 'level': 1, 'cooldown': 0, 'last_used': 0})
        if self.class_name == 'Rogue':
            self.skills.append({'skill': dark_slash, 'name': 'Dark Slash', 'key': 1, 'level': 1, 'cooldown': 0.5, 'last_used': 0,  'cooldown_mod': 1.0})
            self.skills.append({'skill': shadow_dagger, 'name': 'Shadow Dagger', 'key': 2, 'level': 3, 'cooldown': 1.5, 'last_used': 0,  'cooldown_mod': 1.0})


    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.stat_points += 2  # optional: keep manual points
            self.skill_points += 1
            self.xp_to_next = int(self.xp_to_next * 1.3)
            leveled = True

            # ---------- Automatic class-based stat growth ----------
            growth = CLASS_STAT_GROWTH.get(self.class_name, {})
            for stat, value in growth.items():
                setattr(self, stat, getattr(self, stat) + value)

        self.update_stats()  # recalc HP, Mana, Atk, etc
        return leveled

    def unlock_skills(self):
        for sk in self.skills:
            if sk['level']<=self.level and sk not in self.unlocked_skills:
                self.unlocked_skills.append(sk)
                print(f"Unlocked skill: {sk['name']}")

# ---------- Enemy ----------
class Enemy:
    def __init__(self, name, hp, atk, spd, x, y):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.spd = spd
        self.x = x
        self.y = y
        self.size = 16  # collision size
        self.state = 'wander'
        self.wander_target = (x, y)
        self.last_move = time.time()
        self.attack_range = 20      # can only hit player within this distance
        self.attack_cooldown = 1.0  # seconds between attacks
        self.last_attack = 0        # timestamp of last attack

    def update(self, game):
        now = time.time()
        player = game.player
        # distance to player
        d = distance((self.x, self.y), (player.x, player.y))

        # switch state
        self.state = 'chase' if d < 150 else 'wander'

        if self.state == 'chase':
            # move toward player
            ang = math.atan2(player.y - self.y, player.x - self.x)
            self.x += math.cos(ang) * self.spd
            self.y += math.sin(ang) * self.spd

            # attack if close and cooldown ready
            if d <= self.attack_range and (now - self.last_attack) >= self.attack_cooldown:
                game.damage_player(self.atk)
                self.last_attack = now
        else:
            # wander: pick a target occasionally
            if now - self.last_move > 2:
                self.wander_target = (self.x + random.uniform(-50, 50), self.y + random.uniform(-50, 50))
                self.last_move = now
            # move toward wander target
            ang = math.atan2(self.wander_target[1] - self.y, self.wander_target[0] - self.x)
            self.x += math.cos(ang) * self.spd * 0.5
            self.y += math.sin(ang) * self.spd * 0.5
class Enemy2:
    def __init__(self, name, hp, atk, spd, x, y):
        self.name = name
        self.max_hp = hp*10
        self.hp = hp
        self.atk = atk*4
        self.spd = spd*2
        self.x = x
        self.y = y
        self.size = 30  # collision size
        self.state = 'wander'
        self.wander_target = (x, y)
        self.last_move = time.time()
        self.attack_range = 20      # can only hit player within this distance
        self.attack_cooldown = 1.0  # seconds between attacks
        self.last_attack = 0        # timestamp of last attack

    def update(self, game):
        now = time.time()
        player = game.player
        # distance to player
        d = distance((self.x, self.y), (player.x, player.y))

        # switch state
        self.state = 'chase' if d < 300 else 'wander'

        if self.state == 'chase':
            # move toward player
            ang = math.atan2(player.y - self.y, player.x - self.x)
            self.x += math.cos(ang) * self.spd
            self.y += math.sin(ang) * self.spd

            # attack if close and cooldown ready
            if d <= self.attack_range and (now - self.last_attack) >= self.attack_cooldown:
                game.damage_player(self.atk)
                self.last_attack = now
        else:
            # wander: pick a target occasionally
            if now - self.last_move > 2:
                self.wander_target = (self.x + random.uniform(-50, 50), self.y + random.uniform(-50, 50))
                self.last_move = now
            # move toward wander target
            ang = math.atan2(self.wander_target[1] - self.y, self.wander_target[0] - self.x)
            self.x += math.cos(ang) * self.spd * 0.5
            self.y += math.sin(ang) * self.spd * 0.5
class Boss:
    def __init__(self, name, x, y, max_hp=500, atk=15, speed=1.2):
        self.name = name
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.speed = speed

        self.size = 30  # boss hitbox
        self.last_shot = 0
        self.fire_rate = 2.0  # seconds per fireball

    def update(self, dt, game):
        """Boss moves toward player & shoots fireballs"""

        player = game.player
        px, py = player.x, player.y

        # ---- Move toward player ----
        ang = math.atan2(py - self.y, px - self.x)
        self.x += math.cos(ang) * self.speed
        self.y += math.sin(ang) * self.speed

        # ---- Shoot fireball ----
        now = time.time()
        if now - self.last_shot >= self.fire_rate:
            self.shoot_fireball(game, ang)
            self.last_shot = now

    def shoot_fireball(self, game, angle):
        """Boss uses player's fireball projectile but targets player"""

        # fireball stats
        speed = 6
        life = 2
        radius = 10
        damage = 10
        color = "orange"

        proj = Projectile(
            x=self.x,
            y=self.y,
            angle=angle,
            speed= speed,
            life=life,
            radius=radius,
            color=color,
            damage=damage,
            owner="boss"
        )

        game.projectiles.append(proj)

# ---------- Projectile & Particle ----------
class Projectile:
    def __init__(self, x, y, angle, speed, life, radius, color, damage, owner="player"):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.life = life
        self.radius = radius
        self.color = color
        self.damage = damage
       
        # NEW: projectile belongs to player or enemy
        self.owner = owner

    def update(self, dt, game):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= dt

        # Remove if out of bounds
        if self.x < 0 or self.x > WINDOW_W or self.y < 0 or self.y > WINDOW_H:
            self.life = 0
            return

        # --- PLAYER PROJECTILES HIT ENEMIES ---
        if self.owner == "player":
            for e in list(game.room.enemies):
                if distance((self.x, self.y), (e.x, e.y)) <= self.radius + e.size:
                    game.damage_enemy(e, self.damage)
                    self.life = 0
                    return

        # --- ENEMY PROJECTILES HIT PLAYER ---
        if self.owner == "enemy":
            px, py = game.player.x, game.player.y
            if distance((self.x, self.y), (px, py)) <= self.radius + game.player.size:
                game.damage_player(self.damage)
                self.life = 0
                return


class Particle:
    def __init__(self,x,y,size,color,life=0.5):
        self.x=x; self.y=y; self.size=size; self.color=color; self.life=life
    def update(self,dt): self.life-=dt

# ---------- Room ----------
class Room:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.enemies = []

        # --- FIXED ROOM TYPES ---
        if (row, col) == (0, 0):
            # SPAWN ROOM -> No enemies
            return

        elif (row, col) == (0, 1):
            # Room 1: small number of weak enemies
            self.spawn_enemies(goblins=3)
            

        elif (row, col) == (0, 2):
            # Room 2: more weak enemies
            self.spawn_enemies(goblins=6)

        elif (row, col) == (1, 0):
            # Room 3: mixed weak + 1 stronger enemy
            self.spawn_enemies(goblins=5, orcs=1)

        elif (row, col) == (1, 1):
            # Room 4: mixed, difficulty increases
            self.spawn_enemies(goblins=6, orcs=2)
        elif (row, col) == (0, 0):
            # Room 4: mixed, difficulty increases
            self.enemies.append(Boss("Fire Lord", hp=500, atk=15, spd=1.2, x=WINDOW_W//2, y=WINDOW_H//2))
        # --- AUTOMATIC SCALING FOR ALL OTHER ROOMS ---
        else:
            depth = row + col
            goblins = 4 + depth * 2
            orcs = max(0, depth - 2)
            trolls = max(0, depth - 4)

            self.spawn_enemies(
                goblins=goblins,
                orcs=orcs,
                trolls=trolls
            )

    # --------------------------------------------------
    # Enemy Spawner
    # --------------------------------------------------
    def spawn_enemies(self, goblins=0, orcs=0, trolls=0):
        for _ in range(goblins):
            self.enemies.append(
                Enemy("Goblin", 30, 5, 1.5,
                      random.randint(50, WINDOW_W-50),
                      random.randint(50, WINDOW_H-50))
            )

        for _ in range(orcs):
            self.enemies.append(
                Enemy2("Orc", 50, 8, 1.0,
                       random.randint(50, WINDOW_W-50),
                       random.randint(50, WINDOW_H-50))
            )

        for _ in range(trolls):
            self.enemies.append(
                Enemy2("Troll", 80, 12, 0.8,
                       random.randint(50, WINDOW_W-50),
                       random.randint(50, WINDOW_H-50))
            )


# ---------- Game App ----------
class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Dungeon LitRPG'); self.geometry(f'{WINDOW_W}x{WINDOW_H}'); self.resizable(False,False)
        self.canvas=tk.Canvas(self,width=WINDOW_W,height=WINDOW_H,bg='black'); self.canvas.pack()
        self.keys={}; self.player=None; self.room=None; self.dungeon={}
        self.projectiles=[]; self.particles=[]; self.mouse_pos=(WINDOW_W//2,WINDOW_H//2)
        self.room_row=0; self.room_col=0
        self.show_stats=False
        self.bind('<KeyPress>',self.on_key_down)
        self.bind('<KeyRelease>',self.on_key_up)
        self.canvas.bind('<Button-1>', self.handle_stat_click)
        self.create_player(); self.last_time=time.time(); self.after(16,self.loop)
        self.dead = False
        self.respawn_time = 0
        self.respawn_delay = 5  # respawn after 5 seconds
        

    
    def create_player(self):
        name=simpledialog.askstring('Name','Enter your name:',parent=self) or 'Hero'
        cls=simpledialog.askstring('Class','Choose class: Warrior, Mage, Rogue',parent=self)
        cls=cls.capitalize() if cls and cls.capitalize() in ('Warrior','Mage','Rogue') else 'Warrior'
        self.player=Player(name,cls)
        self.room=self.get_room(0,0)
    
    def get_room(self,row,col):
        key=(row,col)
        if key not in self.dungeon: self.dungeon[key]=Room(row,col)
        return self.dungeon[key]
    
    # ---------- Input ----------
    def on_key_down(self,e):
        self.keys[e.keysym]=True
        if e.keysym.lower()=='p':
            self.show_stats = not self.show_stats
            
    
    def on_key_up(self,e): self.keys[e.keysym]=False
    
    def mouse_angle_from_player(self):
        mx,my=self.mouse_pos; px,py=self.player.x,self.player.y
        return math.atan2(my-py,mx-px)
    
    # ---------- Damage ----------
    def damage_player(self, amount):
        if self.dead:
            return  # ignore damage while dead

        self.player.hp -= amount
        if self.player.hp <= 0:
            self.dead = True
            self.player.level = max(1, self.player.level - 1)  # lose 1 level
            self.respawn_time = self.respawn_delay
            print("You died! Respawning in 5 seconds...")


    def damage_enemy(self, e, amount):
        e.hp -= amount
        if e.hp <= 0 and e in self.room.enemies:
            self.player.gain_xp(e.max_hp*2)  # XP based on enemy strength
            self.room.enemies.remove(e)


    # ---------- Updates ----------
    def update_entities(self,dt):
        for e in list(self.room.enemies): e.update(self)
        for p in list(self.projectiles): p.update(dt,self)
        self.projectiles=[p for p in self.projectiles if p.life>0]
        for part in self.particles: part.update(dt)
        self.particles=[p for p in self.particles if p.life>0]
        self.player.unlock_skills()
    
    def update_player(self, dt):
        if not self.player:
            return  # safety check

        p = self.player

        # --- Regeneration ---
        p.hp = min(p.max_hp, p.hp + p.hp_regen * dt)
        p.mana = min(p.max_mana, p.mana + p.mana_regen * dt)

        # --- Death / Respawn ---
        if self.dead:
            self.respawn_time -= dt
            if self.respawn_time <= 0:
                # Teleport to spawn and reset stats
                p.x = WINDOW_W // 2
                p.y = WINDOW_H // 2
                p.hp = p.max_hp
                p.mana = p.max_mana
                self.dead = False
                self.room_row = 0
                self.room_col = 0
                self.room = self.get_room(self.room_row, self.room_col)
                print("Respawned!")
            return  # skip movement/skills while dead

        # --- Movement ---
        if self.keys.get('w'): p.y -= p.speed
        if self.keys.get('s'): p.y += p.speed
        if self.keys.get('a'): p.x -= p.speed
        if self.keys.get('d'): p.x += p.speed

        # --- Room transitions ---
        if p.x < 0:
            self.room_col = max(0, self.room_col - 1)
            p.x = WINDOW_W - 10
            self.room = self.get_room(self.room_row, self.room_col)
        if p.x > WINDOW_W:
            self.room_col = min(ROOM_COLS - 1, self.room_col + 1)
            p.x = 10
            self.room = self.get_room(self.room_row, self.room_col)
        if p.y < 0:
            self.room_row = max(0, self.room_row - 1)
            p.y = WINDOW_H - 10
            self.room = self.get_room(self.room_row, self.room_col)
        if p.y > WINDOW_H:
            self.room_row = min(ROOM_ROWS - 1, self.room_row + 1)
            p.y = 10
            self.room = self.get_room(self.room_row, self.room_col)

        p.x = clamp(p.x, 0, WINDOW_W)
        p.y = clamp(p.y, 0, WINDOW_H)

        # --- Skills with cooldown ---
        now = time.time()
        for sk in p.unlocked_skills:
            key = str(sk['key'])
            if self.keys.get(key) or self.keys.get('KP_' + key):
                base_cd = sk.get('cooldown', 0)
                mod = sk.get('cooldown_mod', 1.0)
                last_used = sk.get('last_used', 0)
                if now - last_used >= base_cd * mod:
                    sk['skill'](p, self)
                    sk['last_used'] = now

                    # Reduce cooldown multiplier slightly each cast
                    sk['cooldown_mod'] = max(0.2, mod * 0.999)  # 5% faster per cast, min 20% of base


    
    # ---------- Projectiles & Particles ----------
    def spawn_projectile(self,x,y,angle,speed,life,radius,color,damage):
        self.projectiles.append(Projectile(x,y,angle,speed,life,radius,color,damage))
    def spawn_particle(self,x,y,size,color): self.particles.append(Particle(x,y,size,color))
    
    # ---------- Stat allocation ----------
    def handle_stat_click(self,event):
        if not self.show_stats or self.player.stat_points<=0: return
        mx,my=event.x,event.y
        stat_y_start=120; stat_height=30
        stats=['strength','vitality','agility','intelligence','wisdom','will']
        for i,stat in enumerate(stats):
            btn_x=600; btn_y=stat_y_start+i*stat_height
            btn_w, btn_h=30,20
            if btn_x<mx<btn_x+btn_w and btn_y<my<btn_y+btn_h:
                setattr(self.player,stat,getattr(self.player,stat)+1)
                self.player.stat_points-=1
                self.player.update_stats()
    
    # ---------- Draw ----------
    def draw(self):
        self.canvas.delete('all')
        px, py = self.player.x, self.player.y
        self.canvas.create_oval(px-10, py-10, px+10, py+10, fill='cyan')
        for e in self.room.enemies:
            color = 'red'
            if isinstance(e, Boss): color = 'orange'
            self.canvas.create_oval(
                e.x - e.size, e.y - e.size,
                e.x + e.size, e.y + e.size,
                fill=color
            )


        for proj in self.projectiles: self.canvas.create_oval(proj.x-proj.radius,proj.y-proj.radius,proj.x+proj.radius,proj.y+proj.radius,fill=proj.color)
        for part in self.particles: self.canvas.create_oval(part.x-part.size,part.y-part.size,part.x+part.size,part.y+part.size,fill=part.color)
        # HUD
        self.canvas.create_rectangle(10,10,210,30,fill='gray')
        self.canvas.create_rectangle(10,10,10+int((self.player.hp/self.player.max_hp)*200),30,fill='red')
        self.canvas.create_rectangle(10,35,210,55,fill='gray')
        self.canvas.create_rectangle(10,35,10+int((self.player.mana/self.player.max_mana)*200),55,fill='blue')
        self.canvas.create_rectangle(10,60,210,70,fill='gray')
        self.canvas.create_rectangle(10,60,10+int((self.player.xp/self.player.xp_to_next)*200),70,fill='green')
        self.canvas.create_text(220,60,text=f'LV {self.player.level}',fill='white',anchor='nw')
        # Skills
        for i, sk in enumerate(self.player.unlocked_skills[:6]):
            x0=10+i*60; y0=80; size=50
            self.canvas.create_rectangle(x0,y0,x0+size,y0+size,fill='blue')
            self.canvas.create_text(x0+size/2,y0+size/2,text=sk['name'][0],fill='white')
            
    # Draw cooldown overlay
        now = time.time()
        for i, sk in enumerate(self.player.unlocked_skills[:3]):
            x0 = 10 + i*60
            y0 = 80
            size = 50

            # Draw background
            self.canvas.create_rectangle(x0, y0, x0 + size, y0 + size, fill='blue')

            # Draw cooldown overlay
            base_cd = sk.get('cooldown', 0)
            mod = sk.get('cooldown_mod', 1.0)
            last_used = sk.get('last_used', 0)
            cd_remaining = max(0, base_cd * mod - (now - last_used))
            if cd_remaining > 0:
                frac = cd_remaining / (base_cd * mod)
                self.canvas.create_rectangle(x0, y0, x0 + size, y0 + size * frac, fill='grey')

        # Draw skill initial
        self.canvas.create_text(x0 + size/2, y0 + size/2, text=sk['name'][0], fill='white')

        # Draw skill initial
        self.canvas.create_text(x0 + size/2, y0 + size/2, text=sk['name'][0], fill='white')
            # Stats panel
        if self.show_stats: self.draw_stats_panel()
        self.canvas.create_text(650,10,text=f'Room: ({self.room_row},{self.room_col})',fill='white')
        for i, sk in enumerate(self.player.unlocked_skills[:3]):
            x0=10+i*60; y0=80; size=50
            self.canvas.create_text(x0+size/2,y0+size/2,text=sk['name'][0],fill='white')
        
    def draw_stats_panel(self):
        p=self.player
        self.canvas.create_rectangle(100,100,700,500,fill='#222')
        stats=['strength','vitality','agility','intelligence','wisdom','will']
        y_start=120; stat_height=30
        for i,stat in enumerate(stats):
            val=getattr(p,stat)
            self.canvas.create_text(120,y_start+i*stat_height,anchor='nw',text=f'{stat.upper()}: {val}',fill='white',font=('Arial',14))
            if p.stat_points>0:
                # Draw clickable plus
                self.canvas.create_rectangle(600,y_start+i*stat_height,630,y_start+i*stat_height+20,fill='green')
                self.canvas.create_text(615,y_start+i*stat_height+10,text='+',fill='white')
        self.canvas.create_text(120,350,text=f'Stat Points Available: {p.stat_points}',fill='yellow',font=('Arial',14))
    
    # ---------- Main loop ----------
    def loop(self):
        now=time.time(); dt=now-self.last_time; self.last_time=now
        self.update_player(dt); self.update_entities(dt); self.draw(); self.after(16,self.loop)

if __name__=='__main__':
    app=GameApp()
    app.mainloop()

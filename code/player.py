import pygame #type:ignore
from settings import*
from support import *
from timer import Timer #type:ignore


class Player(pygame.sprite.Sprite):
    def __init__(self,pos,group,collision_sprites,tree_sprites,interaction, soil_layer):
            super().__init__(group)

            self.import_assets() # has to be on the top because we need the dictionary
            # we need to get the status instead of making a status
            self.status = 'down_axe'
            self.frame_index = 0
            #general setup
            self.image = self.animations[self.status][self.frame_index]
            self.rect = self.image.get_rect(center = pos)
            self.hitbox = self.rect.copy().inflate((-126,-70))
            self.z = LAYERS['main'] # using layers to display the surface to get the right 3d effect

            #movement attributes
            self.direction = pygame.math.Vector2() # default value is 0,0
            self.pos = pygame.math.Vector2(self.rect.center)
            self.speed = 200

            #collision
            self.collision_sprites = collision_sprites

            self.timers = {
                 'tool use': Timer(350,self.use_tool),
                 'tool switch': Timer(200),
                 'seed use': Timer(350,self.use_seed),
                 'seed switch': Timer(200)
            }
            self.tools = ['hoe','axe','water']
            self.tool_index = 0
            self.selected_tool = self.tools[self.tool_index]

            #seeds
            self.seeds = ['corn','tomato']
            self.seed_index = 0
            self.selected_seed = self.seeds[self.seed_index]
            self.item_inventory = {
                'wood': 0,
                'apple': 0,
                'corn': 0,
                'tomato': 0
            }
            self.tree_sprites = tree_sprites
            self.interaction = interaction
            self.sleep = False
            self.soil_layer = soil_layer


    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)


    def get_target_pos(self):
         self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
         
    
    def use_seed(self):
         self.soil_layer.plant_seed(self.target_pos, self.selected_seed)

    def animate(self,dt):
         self.frame_index += 4*dt # this goes through the various frames for an animation
         if self.frame_index >= len(self.animations[self.status]):
              self.frame_index = 0              
         self.image = self.animations[self.status][int(self.frame_index)] #it is a float that is why it has to be converted to int

    def get_status(self):
         # if the player is idle
         #add _idle to the status
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        #tool use - axe, water etc.
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0]+'_'+ self.selected_tool


    def import_assets(self): # dictionary animations, containing all states of the player; the names have to correspond with the graphics file
         self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
         for animation in self.animations.keys():
              full_path = '../graphics/character/'+ animation
              self.animations[animation] = import_folder(full_path) # importing all the images
    #interactions with player; elif is used as you don't want both keys to be pressed, but you could certainy do that
    def input(self):
            # the order of if statements also causes problems - I can move a certain way while holding a key but not the other way due to priority of the if statements
            #try fixin this issue
            keys = pygame.key.get_pressed()
            if not self.timers['tool use'].active and not self.timers['seed use'].active and not self.sleep:
                if keys[pygame.K_UP]:
                    self.direction.y = -1 #the movement becomes fixed
                    self.status = 'up'
                elif keys[pygame.K_DOWN]:
                    self.direction.y = 1
                    self.status = 'down'
                else: # this fixes the movement after the button is not pressed
                    self.direction.y = 0
                if keys[pygame.K_RIGHT]:
                    self.direction.x = 1
                    self.status = 'right'
                elif keys[pygame.K_LEFT]:
                    self.direction.x = -1
                    self.status = 'left'
                else:
                    self.direction.x = 0

                #tool use
                if keys[pygame.K_SPACE]:
                    #timer for tool use
                    self.timers['tool use'].activate()
                    self.direction = pygame.math.Vector2()
                    self.frame_index = 0
                #change tools
                if keys[pygame.K_q] and not self.timers['tool switch'].active:
                    self.timers['tool switch'].activate()
                    self.tool_index += 1
                    self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                    self.selected_tool = self.tools[self.tool_index]
                
                #seed use
                if keys[pygame.K_LCTRL]:
                    #timer for tool use
                    self.timers['seed use'].activate()
                    self.direction = pygame.math.Vector2()
                    self.frame_index = 0
                #change seed
                if keys[pygame.K_e] and not self.timers['seed switch'].active:
                    self.timers['seed switch'].activate()
                    self.seed_index += 1
                    self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                    self.selected_seed = self.seeds[self.seed_index]
                
                if keys[pygame.K_RETURN]:
                    collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
                    if collided_interaction_sprite:
                        if collided_interaction_sprite[0].name == 'Trader':
                            pass
                        else:
                            self.status = 'left_idle'
                            self.sleep = True


    def update_timers(self):
         for timer in self.timers.values():
              timer.update()

    def collision(self,direction):
         for sprite in self.collision_sprites.sprites():
              if hasattr(sprite,'hitbox'):
                   if sprite.hitbox.colliderect(self.hitbox):
                        if direction == 'horizontal':
                            if self.direction.x > 0:
                                self.hitbox.right = sprite.hitbox.left
                            if self.direction.x<0:
                                self.hitbox.left = sprite.hitbox.right
                            self.rect.centerx = self.hitbox.centerx
                            self.pos.x = self.hitbox.centerx
                        if direction == 'vertical':
                            if self.direction.y > 0:
                                self.hitbox.bottom = sprite.hitbox.top
                            if self.direction.y<0:
                                self.hitbox.top = sprite.hitbox.bottom
                            self.rect.centery = self.hitbox.centery
                            self.pos.y = self.hitbox.centery
                             

    def move(self,dt):
        #issue - speeds get add up when moving on both axis
        #normalizing a vector to fix the speed issue - getting a unit vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize() # only normalizes vectors with some length

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        
        # rect stores int but dt uses float - fixed by self.pos
    
    def update(self,dt):
        self.input()
        
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt) # have to call the function
        self.animate(dt)
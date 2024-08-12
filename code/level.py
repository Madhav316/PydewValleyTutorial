import pygame #type:ignore
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame # type: ignore
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain
from random import randint



class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		self.soil_layer = SoilLayer(self.all_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset,self.player)
		
		#sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 3
		self.soil_layer.raining = self.raining

	def setup(self):
		tmx_data = load_pygame('../data/map.tmx')

		#house - all layers have to be imported separately; you can make these 2 for loops more elegant
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x,y,surf in tmx_data.get_layer_by_name(layer).tiles(): # gives you all the tiles in this layer
				Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,LAYERS['house bottom'])
		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x,y,surf in tmx_data.get_layer_by_name(layer).tiles(): # gives you all the tiles in this layer
				Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,LAYERS['main'])
		#Fence
		for x,y,surf in tmx_data.get_layer_by_name('Fence').tiles(): # gives you all the tiles in this layer
			Generic((x*TILE_SIZE,y*TILE_SIZE),surf,[self.all_sprites,self.collision_sprites],LAYERS['main']) # you could remove layers['main']
		#water
		water_frames = import_folder('../graphics/water')
		for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x*TILE_SIZE,y*TILE_SIZE),water_frames, self.all_sprites)

		#WildFlower
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])
		
		#Tree
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites,self.tree_sprites],obj.name,self.player_add)
		
		#player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x,obj.y),
					group = self.all_sprites,
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer)
			if obj.name == 'Bed':
				Interaction((obj.x,obj.y),(obj.width,obj.height),self.interaction_sprites, obj.name)
		#collision tile
		for x,y,surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x*TILE_SIZE,y*TILE_SIZE),pygame.Surface((TILE_SIZE,TILE_SIZE)),self.collision_sprites)

		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground'])
		
	def player_add(self,item):
		self.player.item_inventory[item] += 1

	def reset(self):
		
		
		self.soil_layer.remove_water()
		self.raining = randint(0,10) > 3
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()


		#apples
		for tree in self.tree_sprites.sprites():
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()


	def run(self,dt):
		self.display_surface.fill('black')
		#self.all_sprites.draw(self.display_surface)
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)

		# rain
		if self.raining:
			self.rain.update()

		#transition overlay
		self.overlay.display()
		if self.player.sleep:
			self.transition.play()

class CameraGroup(pygame.sprite.Group):
	#we are creating a special group to get the camera
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2() # camera will have the opposite direction of the player, we will draw the map in the opposite direction
		
	def custom_draw(self,player):
		#ensures player is in the center of the camera
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
		#displaying in layers
		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery): #makes it look really nice
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image,offset_rect) # to draw a sprite you need both the image and rect
				
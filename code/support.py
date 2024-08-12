import pygame #type:ignore
from os import walk #allows you to walk through different folders


def import_folder(path):
    surface_list = []
    # walk gives a list of al of the folders and their files, they are just names right now
    for _,_, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image # you can test i by printing the full path
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
            
    return surface_list

def import_folder_dict(path):
    surface_dict = {}
    for _,_, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image 
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf

    return surface_dict
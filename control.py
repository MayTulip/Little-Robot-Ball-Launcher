# Mei Yang (mny8), Jia Lin Zhu (jz352)
# Final Project
# May 19, 2017

#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import pygame # Import Library and initialize pygame
from pygame.locals import*
from pygame import mixer
import os
import detect_shapes as ds
import picamera
import numpy as np
import argparse
import cv2

os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
pygame.mouse.set_visible(False)
#pygame.mouse.set_visible(True)

# setup pins for servos
GPIO.setmode(GPIO.BCM)

GPIO.setup(13, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

# define constants for display
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]

title_font = pygame.font.Font(None, 40)
my_font = pygame.font.Font(None, 30)

# initialize variables
q = False
mode = 0 # 0 = not started, 1 = automatic, 2 = manual
timer = 0
motion = 0 # for manual mode, 0 = stop, 1 = forward, 2 = backward
aim = False # for manual mode

# start servos with zero duty cycle
launch = GPIO.PWM(5, 1/0.0215)
launch.start(0)
pl = GPIO.PWM(6, 1/0.0215)
pl.start(0)
pr = GPIO.PWM(13, 1/0.0215)
pr.start(0)

screen = pygame.display.set_mode([320, 240])
cam = picamera.PiCamera()

# display title page
screen.fill(WHITE) # Erase the Work space

title_img = pygame.image.load('image/title.jpg')
title_img = pygame.transform.scale(title_img, (240, 200))
screen.blit(title_img,(40,40))

title = title_font.render("Get Tom!", 1, BLACK)
screen.blit(title,(110,10))

pygame.display.flip() # display workspace on screen

# start music
mixer.init()
mixer.music.load('image/music.mp3')
mixer.music.play()
music_timer = time.time()

time.sleep(5)

while (q == False):
        # restart music
        if (time.time() - music_timer >= 60) :
               mixer.music.play()
               music_timer = time.time() 

        timer = timer + 1
        time.sleep(0.05)
        
        screen.fill(WHITE) # Erase the Work space

        if mode == 0:
                # display page to select mode
                blue_button = pygame.image.load('image/blue.png')
                blue_button = pygame.transform.scale(blue_button, (140, 40))
                screen.blit(blue_button,(30,100))

                yellow_button = pygame.image.load('image/yellow.jpg')
                yellow_button = pygame.transform.scale(yellow_button, (100, 40))
                screen.blit(yellow_button,(200,100))

                red_button = pygame.image.load('image/red.png')
                red_button = pygame.transform.scale(red_button, (80, 40))
                screen.blit(red_button,(42,200))
                
                my_buttons = {'Quit':(80, 220), 'Automatic':(100,120), 'Manual':(250, 120)}
                
                for my_text, text_pos in my_buttons.items():
                        text_surface = my_font.render(my_text, True, BLACK)
                        rect = text_surface.get_rect(center=text_pos)
                        screen.blit(text_surface, rect)
                        
                for event in pygame.event.get():
                        if(event.type is MOUSEBUTTONDOWN):
                                pos = pygame.mouse.get_pos()
                        elif(event.type is MOUSEBUTTONUP):
                                pos = pygame.mouse.get_pos()
                                x,y = pos
                                if y < 240 and y > 190 and x < 120 and x > 40:
                                        q = True
                                elif mode == 0 and y < 155 and y > 85 and x < 180 and x > 20:
                                        mode = 1
                                elif mode == 0 and y < 155 and y > 85 and x <320 and x > 170:
                                        mode = 2

                pygame.display.flip() # display workspace on screen

        # automatic mode
        elif mode == 1:
                # move forward
                pl.ChangeFrequency(1/0.02162) 
                pl.ChangeDutyCycle(100*1.62/21.62) 
                pr.ChangeFrequency(1/0.0213) 
                pr.ChangeDutyCycle(100*1.3/21.3)  

                # display page with quit button
                red_button = pygame.image.load('image/red.png')
                red_button = pygame.transform.scale(red_button, (80, 40))
                screen.blit(red_button,(42,200))

                quit_button = my_font.render("Quit", True, BLACK)
                screen.blit(quit_button,(60,210))   

                label = title_font.render("Searching...", 1, BLACK)
                screen.blit(label,(100,100))

                for event in pygame.event.get():
                        if(event.type is MOUSEBUTTONDOWN):
                                pos = pygame.mouse.get_pos()
                        elif(event.type is MOUSEBUTTONUP):
                                pos = pygame.mouse.get_pos()
                                x,y = pos
                                if y < 240 and y > 190 and x < 120 and x > 40:
                                        q = True

                pygame.display.flip() # display workspace on screen

                # take a picture every 0.5 sec
                if(timer % 10 == 0):
                        cam.capture('image.png')

                        # load the image
                        image = cv2.imread("image.png")

                        # find all the 'dark gray' shapes in the image
                        lower = np.array([30, 30, 30])
                        upper = np.array([50, 50, 50])
                        shapeMask = cv2.inRange(image, lower, upper)

                        # find the contours in the mask
                        (cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

                        detected = False

                        for c in cnts:
                                area = cv2.contourArea(c)

                                # large 'dark gray' area found
                                if(area > 1000):
                                        detected = True
                                        target = c
                                        break
                                        
                        if(detected):
                                # display page with sad Tom
                                detected_img = pygame.image.load('image/detected.jpg')
                                detected_img = pygame.transform.scale(detected_img, (245, 200))
                                screen.blit(detected_img,(40,0))

                                pygame.display.flip() # display workspace on screentime.sleep(0.2)

                                # stop the robot
                                pl.ChangeDutyCycle(0)
                                pr.ChangeDutyCycle(0)

                                correct_position = False
                                
                                while(q == False and correct_position == False):
                                        # restart music
                                        if (time.time() - music_timer >= 60) :
                                               mixer.music.play()
                                               music_timer = time.time() 

                                        for event in pygame.event.get():
                                                if(event.type is MOUSEBUTTONDOWN):
                                                        pos = pygame.mouse.get_pos()
                                                elif(event.type is MOUSEBUTTONUP):
                                                        pos = pygame.mouse.get_pos()
                                                        x,y = pos
                                                        if y < 240 and y > 190 and x < 120 and x > 40:
                                                                q = True

                                        pygame.display.flip() # display workspace on screentime.sleep(0.2)
                                        
                                        # take another image when robot is stopped to confirm firing
                                        cam.capture('image.png')

                                        # load the image
                                        image = cv2.imread("image.png")

                                        # find all the 'dark gray' shapes in the image
                                        lower = np.array([30, 30, 30])
                                        upper = np.array([50, 50, 50])
                                        shapeMask = cv2.inRange(image, lower, upper)

                                        # find the contours in the mask
                                        (cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_SIMPLE)

                                        detected = False

                                        for c in cnts:
                                                area = cv2.contourArea(c)
                                                # large 'dark gray' area found
                                                if(area > 1000):
                                                        detected = True
                                                        target = c
                                                        break
                                                
                                        # target no longer in view
                                        if detected == False:
                                                # move backward
                                                pl.ChangeFrequency(1/0.02138) 
                                                pl.ChangeDutyCycle(100*1.38/21.38) 
                                                pr.ChangeFrequency(1/0.0217) 
                                                pr.ChangeDutyCycle(100*1.7/21.7)  
  
                                                time.sleep(0.2)

                                                # stop the robot
                                                pl.ChangeDutyCycle(0)
                                                pr.ChangeDutyCycle(0)

                                        # target is in view        
                                        else:                                                
                                                # compute the center of the contour
                                                m = cv2.moments(target)
                                                cX = int(m["m10"] / m["m00"])

                                                # if target is too far ahead
                                                if cX > 1200:
                                                        # move forward
                                                        pl.ChangeFrequency(1/0.02162) 
                                                        pl.ChangeDutyCycle(100*1.62/21.62) 
                                                        pr.ChangeFrequency(1/0.0213) 
                                                        pr.ChangeDutyCycle(100*1.3/21.3)  

                                                        time.sleep(0.2)

                                                        # stop the robot
                                                        pl.ChangeDutyCycle(0)
                                                        pr.ChangeDutyCycle(0)

                                                # if target is too far behind
                                                elif cX < 400:                                                                                                        # move backward
                                                        # move backward
                                                        pl.ChangeFrequency(1/0.02138) 
                                                        pl.ChangeDutyCycle(100*1.38/21.38) 
                                                        pr.ChangeFrequency(1/0.0217) 
                                                        pr.ChangeDutyCycle(100*1.7/21.7)  

                                                        time.sleep(0.2)

                                                        # stop the robot
                                                        pl.ChangeDutyCycle(0)
                                                        pr.ChangeDutyCycle(0)

                                                # if target is in the center  
                                                else:
                                                        correct_position = True
                                                        
                                # fire!       
                                launch.ChangeFrequency(1/0.023) 
                                launch.ChangeDutyCycle(100*3/23)

                                time.sleep(2)

                                launch.ChangeFrequency(1/0.0215)
                                launch.ChangeDutyCycle(100*1.5/21.5)

                                # display firing page
                                screen.fill(WHITE) # Erase the Work space

                                fire_img = pygame.image.load('image/fire.jpeg')
                                fire_img = pygame.transform.scale(fire_img, (240, 240))
                                screen.blit(fire_img,(40,0))

                                pygame.display.flip() # display workspace on screen
                                
                                time.sleep(2)

                                # target found, quit the program
                                q = True

        # manual mode
        else:
                # display page with up, down, stop, aim buttons
                red_button = pygame.image.load('image/red.png')
                red_button = pygame.transform.scale(red_button, (80, 40))
                screen.blit(red_button,(42,200))

                up_button = pygame.image.load('image/up.png')
                up_button = pygame.transform.scale(up_button, (80, 80))
                screen.blit(up_button,(70,10))

                down_button = pygame.image.load('image/down.png')
                down_button = pygame.transform.scale(down_button, (80, 80))
                screen.blit(down_button,(170, 10))

                stop_button = pygame.image.load('image/stop.png')
                stop_button = pygame.transform.scale(stop_button, (80, 80))
                screen.blit(stop_button,(70,110))

                aim_button = pygame.image.load('image/aim.jpg')
                aim_button = pygame.transform.scale(aim_button, (70, 70))
                screen.blit(aim_button,(170, 110))

                quit_button = my_font.render("Quit", True, BLACK)
                screen.blit(quit_button,(60,210))    

                for event in pygame.event.get():
                        if(event.type is MOUSEBUTTONDOWN):
                                pos = pygame.mouse.get_pos()
                        elif(event.type is MOUSEBUTTONUP):
                                pos = pygame.mouse.get_pos()
                                x,y = pos
                                if y < 240 and y > 190 and x < 120 and x > 40:
                                        q = True
                                elif y < 90 and y > 10 and x < 150 and x > 70:
                                        motion = 1
                                elif y < 90 and y > 10 and x < 250 and x > 170:
                                        motion = 2
                                elif y < 190 and y > 110 and x < 150 and x > 70: 
                                        motion = 0
                                elif y < 190 and y > 110 and x < 250 and x > 170:
                                        motion = 0
                                        aim = True

                pygame.display.flip() # display workspace on screen

                if motion == 0: # stop
                        pl.ChangeDutyCycle(0)  
                        pr.ChangeDutyCycle(0)

                elif motion == 1: # move forward
                        pl.ChangeFrequency(1/0.02162) 
                        pl.ChangeDutyCycle(100*1.62/21.62) 
                        pr.ChangeFrequency(1/0.0213) 
                        pr.ChangeDutyCycle(100*1.3/21.3)

                elif motion == 2: # move backward                                                                                                       # move backward
                        pl.ChangeFrequency(1/0.02138) 
                        pl.ChangeDutyCycle(100*1.38/21.38) 
                        pr.ChangeFrequency(1/0.0217) 
                        pr.ChangeDutyCycle(100*1.7/21.7)

                # if user wants to aim
                if aim == True:
                        # take a picture
                        cam.capture('image.jpg')
                        img_rgb = cv2.imread('image.jpg', 0)

                        # read in template to compare with
                        template = cv2.imread('template.jpg',0)
                        w, h = template.shape[::-1]

                        res = cv2.matchTemplate(img_rgb,template,cv2.TM_CCOEFF_NORMED)
                        threshold = 0.6 # can change threshold
                        # find where the 2 images match
                        loc = np.where( res >= threshold)

                        # if a large region of area match
                        if len(loc) == 2 and len(loc[0]) >= 20:
                                user_input = False

                                # display page with fire button
                                screen.fill(WHITE) # Erase the Work space

                                aim_button = pygame.image.load('image/aim.jpg')
                                aim_button = pygame.transform.scale(aim_button, (80, 80))
                                screen.blit(aim_button,(140, 50))

                                quit_button = my_font.render("Quit", True, BLACK)
                                screen.blit(quit_button,(60,210))    

                                # user has not clicked the fire button
                                while user_input == False:
                                        # restart music
                                        if (time.time() - music_timer >= 60) :
                                               mixer.music.play()
                                               music_timer = time.time() 

                                        for event in pygame.event.get():
                                                if(event.type is MOUSEBUTTONDOWN):
                                                        pos = pygame.mouse.get_pos()
                                                elif(event.type is MOUSEBUTTONUP):
                                                        pos = pygame.mouse.get_pos()
                                                        x,y = pos
                                                        if y < 240 and y > 190 and x < 120 and x > 40:
                                                                user_input = True
                                                                q = True
                                                        elif y < 130 and y > 50 and x < 220 and x > 140:
                                                                user_input = True
                                                                fire = True

                                        pygame.display.flip() # display workspace on screen

                                if fire == True:     
                                        # fire!       
                                        launch.ChangeFrequency(1/0.023) 
                                        launch.ChangeDutyCycle(100*3/23)

                                        time.sleep(2)

                                        launch.ChangeFrequency(1/0.0215)
                                        launch.ChangeDutyCycle(100*1.5/21.5)

                                        # display firing page
                                        screen.fill(WHITE) # Erase the Work space

                                        fire_img = pygame.image.load('image/fire.jpeg')
                                        fire_img = pygame.transform.scale(fire_img, (240, 240))
                                        screen.blit(fire_img,(40,0))

                                        pygame.display.flip() # display workspace on screen

                                        time.sleep(2)

                                        # target found, quit the program
                                        q = True   
                        
                        # if images do not match, target not in view
                        else:
                                aim = False

                                # display the 'not detected' page
                                screen.fill(WHITE) # Erase the Work space

                                label1 = title_font.render("Not detected.", 1, BLACK)
                                screen.blit(label1,(80,50))
                                label2 = title_font.render("Keep moving!", 1, BLACK)
                                screen.blit(label2,(80,110))

                                pygame.display.flip() # display workspace on screen

                                time.sleep(5)

# display end screen
screen.fill(WHITE) # Erase the Work space

end_img = pygame.image.load('image/end.jpg')
end_img = pygame.transform.scale(end_img, (320, 240))
screen.blit(end_img,(0,0))

end_title = pygame.image.load('image/end_title.jpg')
end_title = pygame.transform.scale(end_title, (120, 90))
screen.blit(end_title,(200,0))

pygame.display.flip() # display workspace on screen

time.sleep(5)

launch.stop()
pl.stop()
pr.stop()
GPIO.cleanup()

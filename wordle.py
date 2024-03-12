#Omar Shahwan 3/12/2024
'''Program is a wordle puzzle that opens a pygame application with 6 guesses of 5-letter words the user can make
to guess the right word from a list of 5 letter words from the English dictionary. Letters in the right spot in
the guess are marked green, letters that are in the answer, but not guessed in the right spot are marked yellow,
and letter not in the correct word are marked grey. If the correct answer isn't found within the first 6 guesses,
the user loses the game, and is prompted to try a new game'''
import pygame
import sys #used later for x button to smoothly close application
import random #used to randomize the correct word answer from the word list for each different puzzle 
from words import * #imports list of 5 letter words from the english language from the words.py file

pygame.init() #Initialize program, activate the game

#Defining constants

WIDTH, HEIGHT = 633, 900 #Set application's width and height

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) #apply width and height to application screen
BACKGROUND = pygame.image.load("materials/Starting Tiles.png") #Import tile image from "materials" file for background to put letters in
BACKGROUND_RECT = BACKGROUND.get_rect(center=(317, 300)) #Center the tiles on the screen in a rectangular shape
ICON = pygame.image.load("materials/Icon.png") #World "W" Icon on top left of application

pygame.display.set_caption("Wordle!") #Caption next to icon on top left of screen
pygame.display.set_icon(ICON) #Initiate the icon stored previously

#Input color values for each color to be used later
GREEN = "#6aaa64"
YELLOW = "#c9b458"
GREY = "#787c7e"
OUTLINE = "#d3d6da" #Used for empty tiles (light gray outline)
FILLED_OUTLINE = "#878a8c" #Used for tiles with a letter in them (Darker bolded outline)

#First word solution of each puzzle will always be 'coder'
CORRECT_WORD = "coder"

ALPHABET = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"] #Listing keyboard-format letters for later use

GUESSED_LETTER_FONT = pygame.font.Font("materials/FreeSansBold.otf", 50) #Font of letters guessed in tiles set to 50
AVAILABLE_LETTER_FONT = pygame.font.Font("materials/FreeSansBold.otf", 25) #Font of letters on keyboard under the guesses set to 25

SCREEN.fill("white") #Defaul color of application areas will be white
SCREEN.blit(BACKGROUND, BACKGROUND_RECT) #Place the background that was set earlier
pygame.display.update() #Update screen to display

#Space between letters on the x & y

LETTER_X_SPACING = 85
LETTER_Y_SPACING = 12
LETTER_SIZE = 75

#Global variables

guesses_count = 0 #Initial number of used guesses (max is 6)

#guesses will store guesses as a 2D list. A guess will be a list of letters.
#The list will be iterated through and each letter in each guess will be drawn on the screen.
guesses = [[]] * 6 #2D list containing multiples lists, each list is one guess which contains letter objects

current_guess = [] #Stores current guess...
current_guess_string = "" #...and guess letters from 1 through 5 letters...
current_letter_bg_x = 110 #...where next letter is drawn on x axis


#Indicators is a list storing all the Indicator object. An indicator is that button thing with all the letters you see.
indicators = [] #list for the keyboard

game_result = "" #Empty during the game but becomes "W" when you win or "L" for when you lose


class Letter: #Letter class to used create a letter object using indicator class later
    def __init__(self, text, bg_position):
        #Initializes all the variables, including text, color, position, size, etc.
        self.bg_color = "white" #Background color of tile when a letter is typed (before guess is entered)
        self.text_color = "black" #Background color of letter that is typed but not yet entered
        self.bg_position = bg_position #Indicates where the background should be placed 
        self.bg_x = bg_position[0] #Shortcuts to get our x & y from our background position
        self.bg_y = bg_position[1] 
        self.bg_rect = (bg_position[0], self.bg_y, LETTER_SIZE, LETTER_SIZE) #Rectangalizes background and controls letter size
        self.text = text #Stores letter in its actual text 
        self.text_position = (self.bg_x+36, self.bg_position[1]+34) #Controls where text is on the screen (offset of 36 and 34 on x and y axes) 
        self.text_surface = GUESSED_LETTER_FONT.render(self.text, True, self.text_color) #Renders text and puts it in pygame surface
        self.text_rect = self.text_surface.get_rect(center=self.text_position) #Puts text surface on the screen with its color

    def draw(self):
        #Puts the letter and text on the screen at the desired positions.
        pygame.draw.rect(SCREEN, self.bg_color, self.bg_rect) #Draw rectangle on the screen with background color, self.bg_rect determines size and postition
        if self.bg_color == "white": #if it equals green, yellow, or gray, there is no outline to indicate this guess has already been used and the letters have been entered
            pygame.draw.rect(SCREEN, FILLED_OUTLINE, self.bg_rect, 3) #3 is thickness of outline
        self.text_surface = GUESSED_LETTER_FONT.render(self.text, True, self.text_color) #create text surface again for new color
        SCREEN.blit(self.text_surface, self.text_rect) #place text surface back on screen
        pygame.display.update()

    def delete(self):
        #Fills the deleted letter's spot with the default square, emptying it.
        pygame.draw.rect(SCREEN, "white", self.bg_rect)
        pygame.draw.rect(SCREEN, OUTLINE, self.bg_rect, 3)
        pygame.display.update()

class Indicator:
    def __init__(self, x, y, letter):
        #Initializes variables such as color, size, position, and letter for keyboard under the tiles
        self.x = x
        self.y = y
        self.text = letter
        self.rect = (self.x, self.y, 57, 75) #x and y positions, width of 57 and height of 75
        self.bg_color = OUTLINE #light grey background color

    def draw(self): #DRAW method
        #Puts the indicator and its text on the screen at the desired position.
        pygame.draw.rect(SCREEN, self.bg_color, self.rect) #
        self.text_surface = AVAILABLE_LETTER_FONT.render(self.text, True, "white")
        self.text_rect = self.text_surface.get_rect(center=(self.x+27, self.y+30))
        SCREEN.blit(self.text_surface, self.text_rect)
        pygame.display.update()

#Drawing the indicators on the screen:

indicator_x, indicator_y = 20, 600

for i in range(3):
    for letter in ALPHABET[i]: #loop to write each indicator spaced out from one another
        new_indicator = Indicator(indicator_x, indicator_y, letter)
        indicators.append(new_indicator)
        new_indicator.draw()
        indicator_x += 60
    indicator_y += 100
    if i == 0:
        indicator_x = 50
    elif i == 1:
        indicator_x = 105

def check_guess(guess_to_check):
    #Goes through each letter and checks if it should be green, yellow, or grey.
    global current_guess, current_guess_string, guesses_count, current_letter_bg_x, game_result #reference global variables
    game_decided = False #temporary local variable to check whether game ended in win/loss or stil continuing
    for i in range(5): #5 letter word
        lowercase_letter = guess_to_check[i].text.lower() #referencing guess_to_check, a list of letters, lowercase text value of the variable
        if lowercase_letter in CORRECT_WORD: #if lowercase level is in the word 
            if lowercase_letter == CORRECT_WORD[i]: #and in the right position (index number)
                guess_to_check[i].bg_color = GREEN #then mark background color as green
                for indicator in indicators: #cycle through indicators on keyboard image and change appropriate letter(s) to green
                    if indicator.text == lowercase_letter.upper(): 
                        indicator.bg_color = GREEN #change background color to green
                        indicator.draw()
                guess_to_check[i].text_color = "white" #change the color of the letter with a green background to a white font to match the new background better than black
                if not game_decided: #cycling through each letter, if one letter is grey, game_decided would be true, so if there are no grey colors, then all of them were green
                    game_result = "W" #when all letters are found green (not grey or not game_decided which means grey) display game result as W for win
            else: #letter is correctly in the word but not in the right position
                guess_to_check[i].bg_color = YELLOW #change background color to yellow
                for indicator in indicators: #cycle through indicators on keyboard image and change appropriate letter(s) to yellow
                    if indicator.text == lowercase_letter.upper(): 
                        indicator.bg_color = YELLOW
                        indicator.draw()
                guess_to_check[i].text_color = "white" #change text color to white with its yellow background contrasting
                game_result = "" #should be blank in case more guesses are available
                game_decided = True #didn't win the game (yet) since a yellow mismatched letter appeared
        else: #if letter isn't in the word at all, and completely wrong
            guess_to_check[i].bg_color = GREY #change color background to grey
            for indicator in indicators: #cycle through indicators on keyboard image and change appropriate letter(s) to grey
                if indicator.text == lowercase_letter.upper(): 
                    indicator.bg_color = GREY
                    indicator.draw()
            guess_to_check[i].text_color = "white" #white text now that it has a grey background
            game_result = "" #should be blank in case more guesses are available
            game_decided = True #didn't win the game (yet) since an incorrect grey letter appeared
        guess_to_check[i].draw() #draw each guess on the screen
        pygame.display.update() 
    
    guesses_count += 1 #player has just made a guess, so guess count increases by one
    current_guess = [] #just started the next guess, so it should start as blank
    current_guess_string = "" #string is also blank
    current_letter_bg_x = 110 #reset x distance back to 110

    if guesses_count == 6 and game_result == "": #once all 6 guess have been used and there is no "W" as the game result,
        game_result = "L" #show the game result as "L", symbolizing a lost game

def play_again():
    #Puts the play again text on the screen.
    pygame.draw.rect(SCREEN, "white", (10, 600, 1000, 600)) #draw white rectangle to cover the screen and old indicators
    play_again_font = pygame.font.Font("materials/FreeSansBold.otf", 40) #set the font type and size for the play again text
    play_again_text = play_again_font.render("Press ENTER to Play Again!", True, "black") #render the message prompting user to play again onto the screen, black color
    play_again_rect = play_again_text.get_rect(center=(WIDTH/2, 700)) #rectangularly center the play again text onto the middle of the screen 
    word_was_text = play_again_font.render(f"The word was {CORRECT_WORD}!", True, "black") #announce correct word for the puzzle that just ended
    word_was_rect = word_was_text.get_rect(center=(WIDTH/2, 650)) #center it horizontally and play it just  below the play again text
    SCREEN.blit(word_was_text, word_was_rect) #put both texts on the screen
    SCREEN.blit(play_again_text, play_again_rect)
    pygame.display.update() 

def reset():
    #Accesses and resets all global variables to their default states.
    global guesses_count, CORRECT_WORD, guesses, current_guess, current_guess_string, game_result
    SCREEN.fill("white") #fill the screen with white
    SCREEN.blit(BACKGROUND, BACKGROUND_RECT) #then also put the background on the screen
    guesses_count = 0 #reset the guesses count back to 0
    CORRECT_WORD = random.choice(WORDS) #randomize the next correct word from the word list
    guesses = [[]] * 6  #Reverse all of the following variables back to their empty states
    current_guess = []
    current_guess_string = ""
    game_result = ""
    pygame.display.update() #update all of the above to the pygame
    for indicator in indicators: #revert all indicators on the keyboard
        indicator.bg_color = OUTLINE #back to their original back ground color
        indicator.draw() #and then draw them back

def create_new_letter():
    #Creates a new letter and adds it to the guess.
    global current_guess_string, current_letter_bg_x #reference global variables for current guess in string form and current x position of letter background 
    current_guess_string += key_pressed #pressed key adds to the current string of letters
    new_letter = Letter(key_pressed, (current_letter_bg_x, guesses_count*100+LETTER_Y_SPACING)) #the letter is the pressed key, referencing the desired x position and linearly increasing y position by +100 to its orginal position at the first guess (y=12) 
    current_letter_bg_x += LETTER_X_SPACING #the current letter background x position should be increased by letter x spacing (85 pixels)
    guesses[guesses_count].append(new_letter) #2D list referencing current less and appending new letter to store the archive of all previous guesses and keep them on screen
    current_guess.append(new_letter) #list of the guess appends the new letter
    for guess in guesses: 
        for letter in guess:
            letter.draw() #Finally draw the programmed letter onto the screen

def delete_letter():
    #Deletes the last letter from the guess.
    global current_guess_string, current_letter_bg_x #Reference global variables
    guesses[guesses_count][-1].delete() #guesses at the index guesses_count, or current guess in the liswdt of guesses, at the index -1, getting the last element in the list of guesses
    guesses[guesses_count].pop() #.delete draws a rectangle at the screen which makes it look like the letter was removed but was rather over taken by another shape, while .pop() removes last letter (element) from being stored in the actual list, a python method for lists (i.e. coder -> code)
    current_guess_string = current_guess_string[:-1] #indexing with string slicing to say [0:-1]. This indexes within the string and string slices elements from 0 to -1, the last letter of the string, and omits it
    current_guess.pop() #Accesses current guess list and removes last element from it, as current guess is not necessarily in the archive of previous guesses
    current_letter_bg_x -= LETTER_X_SPACING #the current letter background x position should be decreased by letter x spacing (85 pixels) 

while True:
    if game_result != "": #when the game result occurs (either L or W)
        play_again() #initiate play again function after game is over
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #quit application by clicking 'x' on top right
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: #If ENTER key is clicked once a game result occurs, game is reset for a new wordle puzzle 
                if game_result != "":
                    reset()
                else: #if the game result isn't apparent yet and the game is yet to finish, and the player is pressing ENTER:
                    if len(current_guess_string) == 5 and current_guess_string.lower() in WORDS: #when length of guess becomes 5 letters and falls in the word list,
                        check_guess(current_guess) #Use check guess function to check if the current guess is correct
            elif event.key == pygame.K_BACKSPACE: #backspace button for deleting letter
                if len(current_guess_string) > 0: #If current guess isn't empty,
                    delete_letter() #Delete letter function to backspace one letter
            else:
                key_pressed = event.unicode.upper() #Now for the rest of the keys,
                if key_pressed in "QWERTYUIOPASDFGHJKLZXCVBNM" and key_pressed != "": #if any other key is pressed that is a letter
                    if len(current_guess_string) < 5: #as long as the current letter count is less than 5 (the max)
                        create_new_letter() #type the letter using the create new letter function into the appropriate tile
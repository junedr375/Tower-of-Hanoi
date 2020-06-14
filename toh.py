import pygame, sys, time
import doctest
SPACE_PER_PEG = 200

game_done = False
framerate = 60

# game vars:
steps = 0
n_disks = 3
disks = []
towers_midx = [120, 320, 520]
pointing_at = 0
floating = False
floater = 0

# colors:
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
gold = (239, 229, 51)
blue = (78,162,196)
grey = (170, 170, 170)
green = (77, 206, 145)

############################### Functions for playing game ####################################
class PlayGame():
    def blit_text(screen, text, midtop, aa=True, font=None, font_name = None, size = None, color=(255,0,0)):
        if font is None:                                    # font option is provided to save memory if font is
            font = pygame.font.SysFont(font_name, size)     # already loaded and needs to be reused many times
        font_surface = font.render(text, aa, color)
        font_rect = font_surface.get_rect()
        font_rect.midtop = midtop
        screen.blit(font_surface, font_rect)

    def menu_screen():  # to be called before starting actual game loop
        global screen, n_disks, game_done
        menu_done = False
        while not menu_done:  # every screen/scene/level has its own loop
            screen.fill(white)
            PlayGame.blit_text(screen, 'Towers of Hanoi', (323,122), font_name='sans serif', size=90, color=grey)
            PlayGame.blit_text(screen, 'Towers of Hanoi', (320,120), font_name='sans serif', size=90, color=gold)
            PlayGame.blit_text(screen, 'Use arrow keys to select difficulty:', (320, 220), font_name='sans serif', size=30, color=black)
            PlayGame.blit_text(screen, str(n_disks), (320, 260), font_name='sans serif', size=40, color=blue)
            PlayGame.blit_text(screen, 'Press ENTER to continue', (320, 320), font_name='sans_serif', size=30, color=black)
            
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        menu_done = True
                        game_done = True
                    if event.key == pygame.K_RETURN:
                        menu_done = True
                    if event.key in [pygame.K_RIGHT, pygame.K_UP]:
                        n_disks += 1
                        if n_disks > 10:
                            n_disks = 10
                    if event.key in [pygame.K_LEFT, pygame.K_DOWN]:
                        n_disks -= 1
                        if n_disks < 1:
                            n_disks = 1
                if event.type == pygame.QUIT:
                    menu_done = True
                    game_done = True
            pygame.display.flip()
            clock.tick(60)

    def game_over(): # game over screen
        global screen, steps
        screen.fill(white)
        min_steps = 2**n_disks-1
        PlayGame.blit_text(screen, 'You Won!', (320, 200), font_name='sans serif', size=72, color=gold)
        PlayGame.blit_text(screen, 'You Won!', (322, 202), font_name='sans serif', size=72, color=gold)
        PlayGame.blit_text(screen, 'Your Steps: '+str(steps), (320, 360), font_name='mono', size=30, color=black)
        PlayGame.blit_text(screen, 'Minimum Steps: '+str(min_steps), (320, 390), font_name='mono', size=30, color=red)
        if min_steps==steps:
            PlayGame.blit_text(screen, 'You finished in minumum steps!', (320, 300), font_name='mono', size=26, color=green)
        pygame.display.flip()
        time.sleep(2)   # wait for 2 secs 
        pygame.quit()   #pygame exit
        sys.exit()  #console exit

        
    def make_disks():
        global n_disks, disks
        disks = []
        height = 20
        ypos = 397 - height
        width = n_disks * 23
        for i in range(n_disks):
            disk = {}
            disk['rect'] = pygame.Rect(0, 0, width, height)
            disk['rect'].midtop = (120, ypos)
            disk['val'] = n_disks-i
            disk['tower'] = 0
            disks.append(disk)
            ypos -= height+3
            width -= 23


    def draw_disks():
        global screen, disks
        for disk in disks:
            pygame.draw.rect(screen, blue, disk['rect'])
        return

    def draw_ptr():
        ptr_points = [(towers_midx[pointing_at]-7 ,440), (towers_midx[pointing_at]+7, 440), (towers_midx[pointing_at], 433)]
        pygame.draw.polygon(screen, red, ptr_points)
        return

    def check_won():
        global disks
        over = True
        for disk in disks:
            if disk['tower'] != 2:
                over = False
        if over:
            time.sleep(0.2)
            PlayGame.game_over()

    def reset():
        global steps,pointing_at,floating,floater
        steps = 0
        pointing_at = 0
        floating = False
        floater = 0
        PlayGame.menu_screen()
        PlayGame.make_disks()


################################### Functions to Simulate #######################################

class Simulate():
    def hanoi(pegs, start, target, n):  #Function to solve the puzzle
        assert len(pegs[start]) >= n, 'not enough disks on peg'
        if n == 1:
            pegs[target].append(pegs[start].pop())
            yield pegs
        else:
            aux = 3 - start - target  # start + target + aux = 3
            for i in Simulate.hanoi(pegs, start, aux, n-1): yield i
            for i in Simulate.hanoi(pegs, start, target, 1): yield i
            for i in Simulate.hanoi(pegs, aux, target, n-1): yield i

    def display_pile_of_pegs(pegs, start_x, start_y, peg_height, screen):
        
        #Given a pile of pegs, displays them on the screen, nicely inpilated like in a piramid.
        
        for i, pegwidth in enumerate(pegs):

            pygame.draw.rect(
                screen,
                (78, 162, 196), #blue color
                (
                  start_x + (SPACE_PER_PEG - pegwidth)/2 , # Handles alignment putting pegs in the middle, like a piramid
                  start_y - peg_height * i,         # Pegs are one on top of the other, height depends on iteration
                  pegwidth,
                  peg_height
                )
            )


    def hanoi_simulation(number_of_pegs, base_width, peg_height, sleeping_interval):
        
        # Visually shows the process of optimal solution of an hanoi tower problem.
        

        pegs = [[i * base_width for i in reversed(range(1, number_of_pegs+1))], [], []]
        positions = Simulate.hanoi(pegs, 0, 2, number_of_pegs)

        for position in positions:
            screen.fill((255, 255, 255)) 
            for i, pile in enumerate(position):
                Simulate.display_pile_of_pegs(pile, 2 + SPACE_PER_PEG*i, 550, peg_height, screen)
            pygame.display.update()
            time.sleep(sleeping_interval)
        minimum_steps = pow(2,number_of_pegs) - 1    
        print("Number of minimum step is : " + str(minimum_steps))

        pygame.quit()
###################################################################################################################

choice = int(input("Enter Your choice : \nPress 1 to Simulate\nPress 2 for Play Game\n"))

if choice == 1:
   

    number_of_pegs =int(input("Enter the number of disks\n"))
    
    pygame.init()
    pygame.display.set_caption("Towers of Hanoi")
    screen = pygame.display.set_mode((700,600))
 
    Simulate.hanoi_simulation(
         number_of_pegs,
         base_width = 25,
         peg_height = 30,
         sleeping_interval = 0.5
    )
    
    

elif choice == 2:

    pygame.init()
    pygame.display.set_caption("Towers of Hanoi")
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    
    PlayGame.menu_screen()
    PlayGame.make_disks()

    while not game_done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PlayGame.reset()
                if event.key == pygame.K_q:
                    game_done = True
                if event.key == pygame.K_RIGHT:
                    pointing_at = (pointing_at+1)%3
                    if floating:
                        disks[floater]['rect'].midtop = (towers_midx[pointing_at], 100)
                        disks[floater]['tower'] = pointing_at
                if event.key == pygame.K_LEFT:
                    pointing_at = (pointing_at-1)%3
                    if floating:
                        disks[floater]['rect'].midtop = (towers_midx[pointing_at], 100)
                        disks[floater]['tower'] = pointing_at
                if event.key == pygame.K_UP and not floating:
                    for disk in disks[::-1]: 
                        if disk['tower'] == pointing_at:
                            floating = True
                            floater = disks.index(disk)
                            disk['rect'].midtop = (towers_midx[pointing_at], 100)
                            break
                if event.key == pygame.K_DOWN and floating:
                    for disk in disks[::-1]:
                        if disk['tower'] == pointing_at and disks.index(disk)!=floater:
                            if disk['val']>disks[floater]['val']:
                                floating = False
                                disks[floater]['rect'].midtop = (towers_midx[pointing_at], disk['rect'].top-23)
                                steps += 1
                            break
                    else: 
                        floating = False
                        disks[floater]['rect'].midtop = (towers_midx[pointing_at], 400-23)
                        steps += 1
        screen.fill(white)
       
        PlayGame.draw_disks()
        PlayGame.draw_ptr()
        PlayGame.blit_text(screen, 'Steps: '+str(steps), (320, 20), font_name='mono', size=30, color=black)
        pygame.display.flip()
        if not floating:PlayGame.check_won()
        clock.tick(framerate)
else :
    print("Enter a valid choice\n")


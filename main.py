import PySimpleGUI as sg
import time
import pygame
import threading


sg.theme('DarkAmber') 
sg.set_options(font=('Helvetica', 13, 'bold'))

"""
Pomodoro 
w < 25m: 5m
25m < w < 50m: 8m
50m < w < 90m: 10m
> 90m: 15m

- Work time count
- Relax time count
"""
# CONST
REST_TIME = [5, 8, 10, 15]  # minutes
WORKING_TIME = [25, 50, 90] # minutes
MINIMUM_WORK_TIME = 15   # minutes

# FUNCTIONS
def rest_time_calculate(work_time):
    if work_time < WORKING_TIME[0] * 60:
        rest_time = REST_TIME[0] * 60 
    elif WORKING_TIME[0] * 60 <= work_time < WORKING_TIME[1] * 60:
        rest_time = REST_TIME[1] * 60
    elif WORKING_TIME[1] * 60 <= work_time < WORKING_TIME[2] * 60:
        rest_time = REST_TIME[2] * 60
    elif WORKING_TIME[2] * 60 <= work_time:
        rest_time = REST_TIME[3] * 60
    return rest_time


def rest_time_count(window, element, rest_time):
    while True:
        if rest_time >= 0:
            minutes, seconds = divmod(rest_time, 60)
            window[element].update(f'{minutes:02d}:{seconds:02d}')
            rest_time -= 1
            event, value = window.read(timeout=1000)
            if event == 'Exit' or event == sg.WIN_CLOSED:
                window.close()
                return exit()
        else:
            break
            




def alarm_sound():
    # Play the alarm sound
    pygame.mixer.init()
    pygame.mixer.music.load('sound/alarm.mp3')
    pygame.mixer.music.play(-1)
    # Popup 
    pop_up = sg.popup_ok("Time's up! Let's get back to work.", title='Popup', keep_on_top=True)
   
    pygame.mixer.music.stop()  # Stop the alarm sound

# Layout
"""
Part 1: Time count for working time
Current session/ Current session time/ Total working time/ 
Button Start/ Rest
*************
Part 2: Set rest time countdown 
Rest time countdown/ Popup window-alarm/ 
*************
Part 3: Rest time exceeded
Exceeded rest time/ Total rest time/ Total exceeded rest time/
"""

layout1 = [[sg.Text('Current session', size=(20, 2)), sg.Text('0', size=(20, 2), key='-CURRENT_SESSION-')],
           [sg.Text('Current session time', size=(20, 2))], 
           [sg.Text('00:00', size=(None, 3), justification='center', key='-CURRENT_SESSION_TIME-', font=(None,40), pad=((50, 0), 0))],
           [sg.Text('Total working time', size=(20, 2)), sg.Text('00:00', size=(20, 2), key='-TOTAL_WORKING_TIME-')],
           [sg.Button('Start', key='-BUTTON11-'), sg.Button('Rest', key='-BUTTON12-', disabled=True)]]

layout2 = [[sg.Text('Resting time', size=(20, 4))], 
           [sg.Text('00:00', size=(None, 3), justification='center', key='-RESTING_TIME-', font=(None,40), pad=((50, 0), 0))]]

layout3 = [[sg.Text('Exceeded rest time', size=(20, 4))], 
           [sg.Text('00:00', size=(None, 3), justification='center', key='-EXCEEDED_TIME-', font=(None,40), pad=((50, 0), 0))],
           [sg.Text('Total rest time', size=(20, 2)), sg.Text('00:00', size=(20, 2), key='-TOTAL_REST_TIME-')],
           [sg.Text('Total exceeded rest time', size=(20, 2)), sg.Text('00:00', size=(20, 2), key='-TOTAL_EXCEEDED_TIME-')]
           ]



layout = [[sg.Column(layout1, size=(400, 400)), sg.VSeparator(), sg.Column(layout2, size=(250, 400)), sg.VSeparator(), sg.Column(layout3, size=(400, 400))],
          [sg.Exit()],
          ]

# Window
window = sg.Window('Pomodoro', layout, margins=(100, 100))

# Main function
def main():
    work_time = []
    total_rest_time = 0
    total_exceeded_rest_time = []
    session = 0
    start_time = 0
    rest_time = 0
    current_exceeded_time = 0
    running = False
    resting = False
    exceed_resting = False
    while True:
        event, value = window.read(timeout=500)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        
        # Part 1
        current_time = time.time()
        if event == '-BUTTON11-':   # Start Button
            start_time = time.time()
            exceed_resting = False
            total_exceeded_rest_time.append(current_exceeded_time)
            running = True
            session += 1
            window['-BUTTON11-'].update(disabled=True)
            window['-CURRENT_SESSION-'].update(f'{session}')


        if running:
            # Current session time
            elapsed_time = int(current_time - start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            window['-CURRENT_SESSION_TIME-'].update(f'{minutes:02d}:{seconds:02d}')
            if elapsed_time > MINIMUM_WORK_TIME * 60:  # Work enough time to rest
                window['-BUTTON12-'].update(disabled=False)
            # Total time
            total_time = elapsed_time + sum(work_time)
            minutes, seconds = divmod(total_time, 60)
            window['-TOTAL_WORKING_TIME-'].update(f'{minutes:02d}:{seconds:02d}')

        if event == '-BUTTON12-':
            running = False
            resting = True
            window['-BUTTON12-'].update(disabled=True)
            window['-BUTTON11-'].update(disabled=False)
            work_time.append(elapsed_time)
            start_time = 0
            rest_time = rest_time_calculate(elapsed_time)
            total_rest_time += rest_time + current_exceeded_time

        
        # Part 2
        if resting == True:
            rest_time_count(window, '-RESTING_TIME-', rest_time)
            resting = False
            exceed_resting = True
            start_time = time.time()
            threading.Thread(target=alarm_sound(), daemon=True).start()

          
        # Part 3
        current_time = time.time()
        if exceed_resting == True:
            # Current session exceeded time
            current_exceeded_time = int(current_time - start_time)
            minutes, seconds = divmod(current_exceeded_time, 60)
            window['-EXCEEDED_TIME-'].update(f'{minutes:02d}:{seconds:02d}')
            # Total rest time
            total_time =  total_rest_time + current_exceeded_time
            minutes, seconds = divmod(total_time, 60)
            window['-TOTAL_REST_TIME-'].update(f'{minutes:02d}:{seconds:02d}')
            # Total exceeded rest time
            total_time = current_exceeded_time + sum(total_exceeded_rest_time)
            minutes, seconds = divmod(total_time, 60)
            window['-TOTAL_EXCEEDED_TIME-'].update(f'{minutes:02d}:{seconds:02d}')


    window.close()



if __name__ == '__main__':
    main()
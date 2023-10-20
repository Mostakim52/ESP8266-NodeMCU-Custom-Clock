import machine
import time
import networkconfig
import usocket as socket
import ntptime
import urequests as requests

printstate = False
errorcounts = 0

#a 7 segment display class
class display():
    def __init__(self,gpioPins,num):
        self.sevenPins = [False]*7 #sets all pins to false or OFF
        self.gpio = [0]*7 #initializes all gpio to 0
        for i in range(7): self.gpio[i] = machine.Pin(gpioPins[i],machine.Pin.OUT) #sets gpio pins to be as OUTPUT
        self.disp = num #display number for a particular display. 0-3 as 4 displays are being used
        
gpioPins = (5,4,0,2,14,12,13) #gpio pins of NodeMCU ESP8266
d = [None]*4 #global display array set to array Nothing at first
for i in range(4): d[i] = display(gpioPins,i) #initializes all 4 display viariables

#code explained later to show why 2 clocks are used to sync 4 displays
clk1= machine.Pin(15, machine.Pin.OUT) #gpio pin for clock 1 
clk2= machine.Pin(16, machine.Pin.OUT) #gpio pin for clock 2

#using A0 pin as button as no more free pins available
button = machine.ADC(0)

#resets a particular display to have all pins to OFF or 0
def resetgpio(d): #d is any one of the 4 displays passed as parameter
    for i in range(7): d.sevenPins[i] = False
    setgpio(d)


def sync(num):
    global clk1,clk2
    if num == 0:
        clk1.value(0)
    elif num == 1:
        clk2.value(1)
    elif num == 2:
        clk1.value(1)
    elif num == 3: 
        clk2.value(0)
    
def setgpio(d):
    for i in range(7): 
        d.gpio[i].value(d.sevenPins[i])
    sync(d.disp)

def convert_to_7seg_char(char):
        character_patterns = { #7 segment truth table pin data for almost all letters. True means led ON
    'a': (True, True, True, False, True, True, True),
    'b': (False, False, True, True, True, True, True),
    'c': (True, False, False, True, True, True, False),
    'd': (False, True, True, True, True, False, True),
    'e': (True, False, False, True, True, True, True),
    'f': (True, False, False, False, True, True, True),
    'g': (True, True, True, True, False, True, True),
    'h': (False, False, True, False, True, True, True),
    'i': (False, False, True, False, False, False, False),
    'j': (False, True, True, True, False, False, False),
    'l': (False, False, False, True, True, True, False),
    'n': (False, False, True, False, True, False, True),
    'o': (False, False, True, True, True, False, True),
    'p': (True, True, False, False, True, True, True),
    'q': (True, True, True, False, False, True, True),
    'r': (False, False, False, False, True, False, True),
    's': (True, False, True, True, False, True, True),
    't': (False, False, False, True, True, True, True),
    'u': (False, True, True, True, True, True, False),
    'y': (False, True, True, True, False, True, True),
    'z': (True, True, False, True, True, False, True),
    ' ': (False, False, False, False, False, False, False),
    
    }
        #checks if given letter exists in truth table
        if char.lower() in character_patterns:
            return character_patterns[char.lower()]
        else:
            raise ValueError("Character not supported")
        
def custommessage():
    global d
    letters = "happy birthday" #this will be the sentence displayed. Try to build sentences using letters that are supported by a 7 segment display
    
    for i in range(len(letters)):
        segments =  convert_to_7seg_char(letters[i])
        for i in range(7): d[0].sevenPins[i] = segments[i]

        for j in range(4): setgpio(d[j])
        for k in range(3,0,-1):
            for i in range(7): d[k].sevenPins[i] = d[k-1].sevenPins[i]

        time.sleep(0.3)
        buttonchecker()
        if not printstate: return
        
        
def SevSeg(d,number):
    #Truth Table for numbers.
    TruthTable = ((True,True,True,True,True,True,False),
                  (False,True,True,False,False,False,False),
                  (True,True,False,True,True,False,True),
                  (True,True,True,True,False,False,True),
                  (False,True,True,False,False,True,True),
                  (True,False,True,True,False,True,True),
                  (True,False,True,True,True,True,True),
                  (True,True,True,False,False,False,False),
                  (True,True,True,True,True,True,True),
                  (True,True,True,True,False,True,True))
    for i in range(7): #sets the truth table value for a given number within a display
        d.sevenPins[i] = TruthTable[number][i]
    
def weathermode(d):
    print("Entered weathermode.......")
    city = 'Dhaka' #City within a country
    country_code = 'BD' #This will be your country code. In my case, I'm from Bangladesh so BD.
    open_weather_map_api_key = '' #This will be your own open weather api key. You can sign up and get one if you don't have
    open_weather_map_url = (
        f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&APPID={open_weather_map_api_key}'
    )
    #gets weather data and extracts only temperature from it
    weather_data = requests.get(open_weather_map_url,timeout = 10)
    if weather_data.status_code != 200: return
    raw_temperature = weather_data.json().get('main', {}).get('temp', 0) - 273.15
    temperature_str = "{:.1f}".format(raw_temperature)


    #sets 1st and 2nd display to show °C
    resetgpio(d[0])
    d[0].sevenPins[0] = True
    d[0].sevenPins[3] = True
    d[0].sevenPins[4] = True
    d[0].sevenPins[5] = True

    resetgpio(d[1])
    d[1].sevenPins[0] = True
    d[1].sevenPins[1] = True
    d[1].sevenPins[5] = True
    d[1].sevenPins[6] = True
    
    #sets 3rd and 4th display to show current temperature
    SevSeg(d[2],int(temperature_str[1]))
    SevSeg(d[3],int(temperature_str[0]))

    for i in range(16):
        setgpio(d[i % 4])

    time.sleep(5)


def numcountdown():
    #this function sets displays to show current time
    global printstate,d
    digit = [0]*4
    hourbefore = time.localtime()[3] # gets current time from esp8266
    hourafter = 0
    while True:
        hourafter = time.localtime()[3]
        hours = hourafter+6 
        hours = hours%12 #converting time to 12hr format
        if hours == 0: hours = 12
        minutes = time.localtime()[4]
        timeafter = time.localtime()[5]
        if hours==0:
            digit[2] = 1
            digit[3] = 2
        elif (hours>0 and hours<10):
            digit[2] = int(str(hours))
            digit[3] = 0
        else: 
            digit[2] = int(str(hours)[1])
            digit[3] = int(str(hours)[0])

        if minutes==0:
            digit[0] = 0
            digit[1] = 0
        elif minutes>0 and minutes<10:
            digit[0] = int(str(minutes))
            digit[1] = 0
        else: 
            digit[0] = int(str(minutes)[1])
            digit[1] = int(str(minutes)[0])

        #sets each display to display a particular digit
        for i in range(4):
            SevSeg(d[i],digit[i])
            setgpio(d[i])
        if (timeafter==45): weathermode(d)  #every 45 seconds, the weather temperature will be displayed

        if (hourafter-hourbefore>=1): #esp8266 loses track of time so resyncing time
            hourbefore = hourafter
            print('Syncing time......')
            ntptime.settime()
        
        time.sleep(0.3)
        buttonchecker() #Checks if user has pressed button every loop
        if printstate: return

def buttonchecker():
    #function to check if user has pressed button
    #no more usable pins in esp8266 so using the A0 pin which is connected to a button and resistor
    #button and resistor send a readable value
    #using that value to know if button is pushed
    global printstate
    if button.read() > 900:
        printstate = not printstate
        for i in range(0,8): resetgpio(d[i % 4])
        time.sleep(1)
                
def outputchooser():
    global d,printstate
    while True:
        if printstate: 
            custommessage()
        else: 
            numcountdown()
        time.sleep(0.1)

def check_internet_connection():
    #this function is used to check if esp8266 is connected to internet
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('8.8.8.8', 53))
        s.close()
        return True
    except:
        return False
  
def animate():
    #this function creates an animation in the displays while the esp8266 sets up
    #the animation buys esp8266 time to connect to the internet

    global d
    for j in range(4): resetgpio(d[j])
    animate_time = 0.05

    for l in range(2):
        for i in range(4):
            d[i].sevenPins[0] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[1] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[2] = True
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[3] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[4] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[5] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[6] = True 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)

        for i in range(4):
            d[i].sevenPins[0] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[1] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[2] = False
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[3] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[4] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[5] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
            d[i].sevenPins[6] = False 
            for k in range(4): setgpio(d[k])
            time.sleep(animate_time)
        
animate()

while True:
    try:
        if not check_internet_connection():
            d[0].sevenPins[4] = True
            d[1].sevenPins[0] = True
            d[1].sevenPins[4] = True
            d[1].sevenPins[5] = True
            d[1].sevenPins[6] = True
            d[2].sevenPins[2] = True
            d[2].sevenPins[4] = True
            d[2].sevenPins[5] = True
            d[3].sevenPins[1] = True
            d[3].sevenPins[2] = True
            d[3].sevenPins[3] = True
            d[3].sevenPins[4] = True
            d[3].sevenPins[5] = True
            for i in range(4): setgpio(d[i])
            #uses networkconfig.py to set up a hotspot which you can connect then get into a webpage using 192.168.4.1 and enter your WiFi credentials
            networkconfig.start()
            print("Setting....")
            for i in range(4): animate()
            ntptime.settime()
        else: 
            for i in range(2): animate()
            ntptime.settime()
            outputchooser()
    except Exception as e:

        #if no internet connection then an error message is displayed in the displays
        print(e)
        d[3].sevenPins[0] = True
        d[3].sevenPins[1] = False
        d[3].sevenPins[2] = False
        d[3].sevenPins[3] = True
        d[3].sevenPins[4] = True
        d[3].sevenPins[5] = True
        d[3].sevenPins[6] = True

        d[0].sevenPins[0] = d[2].sevenPins[0] = False
        d[0].sevenPins[1] = d[2].sevenPins[1] = False
        d[0].sevenPins[2] = d[2].sevenPins[2] = False
        d[0].sevenPins[3] = d[2].sevenPins[3] = False
        d[0].sevenPins[4] = d[2].sevenPins[4] = True
        d[0].sevenPins[5] = d[2].sevenPins[5] = False
        d[0].sevenPins[6] = d[2].sevenPins[6] = True

        d[1].sevenPins[0] = False
        d[1].sevenPins[1] = False
        d[1].sevenPins[2] = True
        d[1].sevenPins[3] = True
        d[1].sevenPins[4] = True
        d[1].sevenPins[5] = False
        d[1].sevenPins[6] = True

        for i in range(4): setgpio(d[i])
        errorcounts = errorcounts + 1
        if errorcounts>=2: machine.reset()
        time.sleep(3)
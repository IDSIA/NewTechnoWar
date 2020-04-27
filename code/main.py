from core.agents import Agent, Parameters
from core.state import StateOfTheBoard

done = False

stateOfTheBoard = StateOfTheBoard((4,4))

redParameters = Parameters('red', {})
blueParameters = Parameters('blue', {})

redAgent = Agent(stateOfTheBoard, 0, redParameters)
blueAgent = Agent(stateOfTheBoard, 0, blueParameters)


while not done:
    redAction = redAgent.takeAction()

    # ...update the board... 
    # ...just change values in Dictionary... 
    # ...change values in all red and all blue classes... 
    
    blueAction = blueAgent.takeAction()

    # ...update the board... 
    # ...just change values in Dictionary... 
    # ...change values in all red and all blue classes... 

    # check if end

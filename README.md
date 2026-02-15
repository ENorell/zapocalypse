# Zapocalypse

## Game
Wizard battle royale multiplayer game

`python -m main_pygame`

## Code
Developed with Python and Pygame. Attempts to follow a "Clean Architecture" setup by splitting the code into layers.
Note that code in an upper layer may not depend directly on code from a lower layer.

### Domain
Governs the main game rules and interactions between entities in the game. Agnostic to pixels, graphics, mouse-clicks, controllers etc.

### Interactors
This layer contains application logic for each scene in the game that will "orchestrate" the domain objects. 
It translates user inputs into actions in the game domain and then decides what to present to the screen. 
Still no mention of pixels or concrete input mechanisms.

### Interface
Presenters and Controllers are responsible for the translations between the objects used in the interactors and the raw input and output of the computer.
Here, as much as possible is determined regarding pixels, positions etc. such that the next layer (which is harder to test) can simply put the data on the screen.

### View
A thin layer with external frameworks such as pygame that govern the game window, collecting keyboard and mouse events etc. and pass them to controllers.
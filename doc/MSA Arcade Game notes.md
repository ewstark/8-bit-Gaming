# MSA Arcade Game

## Architecture

See the file "MSA Arcade Game.drawio" for a diagram of the system architecture.

In abstraction, the system is formed by three primary components: the **Game Engine** which executes the main game loop, the **Graphics Engine** which renders each scene of the animated game, and the **Audio Engine** which asynchronously manages, mixes, and produces game sounds and background music.

These three primary components have equivalent PyGame components within the prototype PC system.  These PyGame components can be mapped, via their APIs, to the corresponding hardware components using a bridge device.


## Abstract Processing Overview

### Game Loop
 * get time delta
 * get user input
   * upon player quit:
     * exit Game Loop
 * calculate asset updates
   * write new asset data to current **Game Data RAM** page
   * upon events (collisions, enemy spawn/death, player attack, etc.):
     * start/stop sounds, lights, or change background music
   * upon game-over condition (e.g., final player death):
     * exit Game Loop
 * flip **Game Data RAM** page
   * _optional:_ confirm previous page was fully consumed by **Graphics Engine**

### Graphics Engine
 * upon **Game Data RAM** flip:
   * render screen from new data
 * _optional:_ upon timer:
   * update animations

### Audio Engine
 * upon timer tick:
   * calculate and move audio data to output buffer
 * upon register write:
   * read reg, process event
 * upon register read:
   * write reg

## Mock Game: **Canary Crush**

As a part of learning all aspects of the gaming ecosystem, I'm creating an example game called **Canary Crush**. It is in the style of early-1980's free-standing arcade games. In particular, I'm shamelessly modeling the game after Pengo. It is a simple 2D top-down game that should be easy to replicate. It provides a means for testing interactions with various components such as the game loop, the user interface, 2D pixel art (sprites), and asynchronous audio event processing.

**Canary Crush** is targeted to 320x240 graphics in landscape orientation with 4 bits-per-pixel (16-color) palette-based colors.

    Using 16x16 pixel reference cells, screen grid is 20 wide by 15 high.
    The play area is 13x13 cells with a 1-cell border wall.

                            1 1 1 1 1 1 1 1 1 1 2
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
       +-----------------------------------------+
     0 |w w w w w w w w w w w w w w w   Canary   |
     1 |w                           w   Crush!   |
     2 |w                           w            |
     3 |w                           w  Game-Art  |
     4 |w                           w  Game-Art  |
     5 |w                           w  Game-Art  |
     6 |w                           w            |
     7 |w             x             w P1: 1234567|
     8 |w                           w #lvl #lives|
     9 |w                           w            |
    10 |w                           w P2: 1234567|
    11 |w                           w #lvl #lives|
    12 |w                           w            |
    13 |w                           w MSA Arcade |
    14 |w w w w w w w w w w w w w w w  (c) 1981  |
       +-----------------------------------------+

### Game Story

You are a canary stuck in a mine! A maze of rocks surrounds you. You can slide the rocks if nothing is behind them. You can crush rocks that can't move. Gas clouds are chasing you. Avoid or destroy them by smashing them with rocks. They can also be stunned when player slams a common wall. Stunned clouds move slowly for a period of time and can be trampled upon.

Amongst the rocks are parts of a ventilation system. These can be slid but not broken. When sliding, they won't go past each other but will stick together. Connect them to automatically disperse all gas clouds. New gas clouds will be periodically born from "seed rocks". Destroy all clouds or repair the ventilation shaft to complete the level. The further you descend into the mine, the gas clouds will become more numerous, quick, and aggressive.

Example of game setup at start of game:

    +-----------------------------------------+
    |w w w w w w w w w w w w w w w   Canary   |
    |w   G     w                 w   Crush!   |
    |w w w w   V w w w   w V w G w            |
    |w         w           w     w  Game-Art  |
    |w w w w   V w w w     w w   w  Game-Art  |
    |w               w       w   w  Game-Art  |
    |w   w   w   w w w   w w w   w            |
    |w   w w w     P             w P1: 0000000|
    |w   w       w   w w w w w w w #1      ooo|
    |w w w w w w w   w     w     w            |
    |w       w             w w   w P2: 0000000|
    |w   w       w w   w         w #1      ooo|
    |w G w w w w V w   w   w w w w            |
    |w         w       w     G   w MSA Arcade |
    |w w w w w w w w w w w w w w w  (c) 1982  |
    +-----------------------------------------+
    P = player
    w = wall
    G = gas cloud
    V = ventilation shaft


### Possible Expansion

The **Game Story** above outlines the basic game and initial target. Below are some additional considerations for expansion:
* New obstacles, such as holes in the floor, and enemies may be introduced at deeper levels.
* Have some blocks be frozen in place and require an extra turn to break or push them.
* Have the floors of some empty cells break-open to reveal lava that slows player but not gas clouds
* At random times and locations, the letters 'E', 'X', 'T', 'R', and 'A' will appear in blocks for a brief period of time. If the player breaks the block in time, they collect that letter. If they collect all letters, they get an extra life.


### Sprite Inventory

* Wall block
  * normal
  * breaking, phase1..4
  * seed location
  * letter block, E/X/T/R/A
* Ventilation shaft
  * 4 different parts
* Canary
  * standing, right & up (left & down are derived as H/V flips)
  * pushing, right & up (left & down are derived as H/V flips)
  * dying, phase1..4
  * victory, phase1..4
* Gas cloud
  * normal, phase1..4
  * agitated, phase1..4
  * stunned, phase1..4
  * crushed (stuck to edge of block, one face that is rotated as needed)
  * dying, phase1..4
* GUI
  * title screen
  * game background
  * player life (egg in nest)


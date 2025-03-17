# MSA Arcade Game

## Architecture

___TBD___


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
   * upon game-over (final player death): 
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

# MSA Arcade Game

## Game Loop
 * get time delta
 * get user input
   * upon quit: exit Game Loop
 * calculate asset updates
   * write new asset data
   * upon events: emit sounds, lights, or change background music
   * upon game-over: exit Game Loop
 * flip game data page

## Graphics Engine
 * upon game data page flip:
   * render screen from new data
 * upon timer:  <-- _optional_
   * update animations

## Audio Engine
 * upon timer tick:
   * calculate and move audio data to output buffer
 * upon register write:
   * read reg, process event
 * upon register read:
   * write reg

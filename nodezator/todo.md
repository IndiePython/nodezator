- adjust:
  - text viewer;
  - redrawing when performing window resize setups;

For the redrawing step, the `our3rdlibs.behaviour.watch_window_size()` function should always draw the window with `APP_REFS.window_manager.draw()` after that, it should also check whether a `APP_REFS.draw_after_window_resize_setups` exists, executing it if does and deleting the argument immediately. This argument would be set during the window resize setup of editors/viewers/forms when they were focused. Think about what to do regarding widgets that use loop holders as well.

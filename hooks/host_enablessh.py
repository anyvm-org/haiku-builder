# Drive Haiku's GUI to open a terminal, then paste enablessh.local into it.
#
# Host-side hook: exec()'d into build.py's globals so it can call pauseVNC(),
# vncKey() / vncMoveClick(), _screen_text_value(), inputFile(), the `osname`
# pipeline global, and time.sleep() directly. No subprocess to vncdotool here
# -- the vnc* helpers live in build.py.

# Pause the background screen-capture loop -- we are about to drive the GUI
# ourselves and don't want OCR fighting us for the VNC port.
pauseVNC()

# Two Right arrows clear the first-run language dialog on this ISO.
vncKey("right")
vncKey("right")

time.sleep(60)

# Click on the desktop to make sure we have focus, then poke the dialog again.
vncMoveClick(200, 200)
time.sleep(5)
vncMoveClick(300, 300)

vncKey("right")
vncKey("right")

# Super+Alt+T opens a Haiku terminal. Sometimes it doesn't take on the first
# try (the dialog hasn't actually been dismissed yet), so retry until the
# shell banner shows up on screen.
vncKey("super-alt-t")
time.sleep(5)

while "Welcome to the Haiku shell" not in _screen_text_value(osname):
    vncKey("super-alt-t")
    time.sleep(3)

time.sleep(30)

# Paste enablessh.local into the terminal via vncdotool typefile.
inputFile(osname, "enablessh.local")

time.sleep(30)

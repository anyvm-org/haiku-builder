# Drive Haiku's GUI to open a terminal, then paste enablessh.local into it.
#
# Host-side hook: exec()'d into build.py's globals so it can call pauseVNC(),
# _screen_text_value(), inputFile(), the `osname` pipeline global, and
# time.sleep() directly. Direct vncdotool key/mouse events go via subprocess
# because build.py's wrappers (string/enter/tab/...) are keyboard-only.

# Pause the background screen-capture loop -- we are about to drive the GUI
# ourselves and don't want OCR fighting us for the VNC port.
pauseVNC()

# Two Right arrows clear the first-run language dialog on this ISO.
subprocess.run(["vncdotool", "key", "right"])
subprocess.run(["vncdotool", "key", "right"])

time.sleep(60)

# Click on the desktop to make sure we have focus, then poke the dialog again.
subprocess.run(["vncdotool", "move", "200", "200", "click", "1"])
time.sleep(5)
subprocess.run(["vncdotool", "move", "300", "300", "click", "1"])

subprocess.run(["vncdotool", "key", "right"])
subprocess.run(["vncdotool", "key", "right"])

# Super+Alt+T opens a Haiku terminal. Sometimes it doesn't take on the first
# try (the dialog hasn't actually been dismissed yet), so retry until the
# shell banner shows up on screen.
subprocess.run(["vncdotool", "key", "super-alt-t"])
time.sleep(5)

while "Welcome to the Haiku shell" not in _screen_text_value(osname):
    subprocess.run(["vncdotool", "key", "super-alt-t"])
    time.sleep(3)

time.sleep(30)

# Paste enablessh.local into the terminal via vncdotool typefile.
inputFile(osname, "enablessh.local")

time.sleep(30)

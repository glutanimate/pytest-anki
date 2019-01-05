sudo apt-get update
sudo apt-get install portaudio19-dev xvfb git
python3 -m pip install PyQt5==5.9 sip
start-stop-daemon --start --pidfile ~/xvfb.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset
export DISPLAY=:99
if [ -e "install_anki.sh" ]
then
    source install_anki.sh
else
    source anki_testing/install_anki.sh
fi

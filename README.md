carillon
========

Arduino Carillon project - Jim Bumgardner 2014

This is the Arduino code and backend server for my Arduino / XBee / Carillon project, in which I am using an Arduino to play the bells on a mass-market 9-bell christmas ornament, like this one: 

http://www.amazon.com/Caroling-Christmas-Bells-Pre-Tuned-Musical/dp/B00DELS3RO

The arduino script is set up for an Arduino using an XBee radio to receive serial messages (although it can also work with straight serial via the USB port).  It supports a simple protocol that plays melodies on the bells, which are connected to pins 5 - 13 (Low - High pitched)

The backend, implmented in Python/Flask, does a few different things:

   * It chimes the bells on the quarter hour in the style of Big Ben.

   * It listens for pushed notes from the PushBullet service (which in turn, can be scripted using IFTTT).
      * Notes whose body matches 'tune: <melody>' are played by the chimes.
      * Notes whose body mathces 'song: <name>' also work, using a transcription service, which converts to the lower-level protocol.
      * Examples: 
         * When your Nest Thermostat is set to 'Home', it can play "Home on the Range"
         * When you make an EBay sale, it can play "We're in the Money"
         * If the NY Times publishes a story on Ebola, play 'Fever'
         * Play messages when you receive SMS messages from specific people
         * Play 'Happy Birthday' on birthdays

   * There is a REST API so you can trigger tunes from other home automation systems (e.g. motion detectors)
      
   * There is a web interface to mute the bells, and to set a mute schedule (e.g. don't play the bells at night) (IN PROGRESS)


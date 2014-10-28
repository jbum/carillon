carillon
========

Arduino Carillon project - Jim Bumgardner 2014

This is the Arduino code and backend server for my Arduino / XBee / Carillon project, in which I am using an Arduino to play the bells on a mass-market 9-bell christmas ornament, like this one: 

http://www.amazon.com/Caroling-Christmas-Bells-Pre-Tuned-Musical/dp/B00DELS3RO
(Note: You can find them a little cheaper on EBay.)

The bells can be mounted on a christmas tree, or more permanently.  They play different tunes to announce interesting events.

Examples: 

   * The bells can chime on the quarter hour, like a [fancy clock](http://en.wikipedia.org/wiki/Westminster_Quarters).
   * When your Nest Thermostat is set to 'Home', the bells can play "Home on the Range"
   * If your thermostat gets really cold, they can play "Baby it's cold outside"
   * Make an Ebay Sale? Play "We're in the Money"
   * If the NY Times publishes a story on Ebola, play 'Fever'
   * Play messages when you receive SMS messages from specific people
   * Play 'Happy Birthday' on birthdays
   * Play the bells from your phone
   * etc...

Most of the above features can be scripted using IFTTT in conjunction with the PushBullet channel.

The arduino script is set up for an Arduino using an XBee radio to receive serial messages from a server in another part of the house (an alternate version works with straight serial via the USB port).  It supports a simple protocol that plays melodies on the bells, which are connected to pins 5 - 13 (Low - High pitched)

The backend, implmented in Python/Flask, does a few different things:

   * It can chime the bells on the quarter hour in the style of [Big Ben](http://en.wikipedia.org/wiki/Westminster_Quarters).

   * It listens for pushed notes (events) from the PushBullet service (which in turn, can be scripted using IFTTT).
      * PushBullet notes of the form 'tune: &lt;melody&gt;' are played by the chimes.
      * PushBullet notes of the form 'song: &lt;name&gt;' are converted to the 'tune' protocol using a transcription dictionary.

   * There is a REST API so you can trigger tunes from other home automation systems on your local network (e.g. motion detectors)
      
   * There is a web interface to mute the bells, and to set a mute schedule (e.g. don't play the bells at night) (IN PROGRESS)

   * There is a web interface to play the bells from a phone (IN PROGRESS)


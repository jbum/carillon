/*  Carillon Driver for Arduino - Jim Bumgardner
    This provides a serial notation for playing a 9-note carillon.
*/

/**
Actual Notes:  D  E  F# G  A  B  C  D' E'
In C        :  G  A  B  C  D  E  F  G' A'
Note Number :  1  2  3  4  5  6  7  8  9   

spaces are ignored

Aa (Upper case followed by lowercase) is used to set delay in milliseconds - always provide both letters
   Upper case letter is 100s unit  (A=0, B=100, C=200, etc.)
   Lower case letter is 10s unit   (a=0, b=10, c=20)
   Example: Fa is 500 milliseconds, Fb is 510 milliseconds, Ta is 2 seconds
   Minimum delay is 50 ms

1-9 are note numbers  0 is a delay (each node value gets an implicit delay, unless in chord mode)
& puts us in chord mode (no delay til next 0, then all pins reset, and we go back into single mode)
In single note mode (the default), each note value gets an implicit delay.

Examples: 
# Hour chime, ala Big Ben
Ha 4 6 5 1 0 4 5 6 4 0 6 4 5 1 0 1 5 6 4 0 0 0 0 0 0
 
# 3 o' clock chimes - one chime every 4 seconds
Ha &481 0 0 &481 0 0 &481 0 0 
 
# 1/4 hour
Ha 6 5 4 1 0 0 0
 
# 1/2 hour
Ha 4 6 5 1 0 4 5 6 4 0 0 0
 
# 3/ 4 hour
Ha 6 4 5 1 0 1 5 6 4 0 6 5 4 1 0 0 0

# We're in the money
Be 6 0 8 0 0 6 7 0 8 0 0 0 0 0 0 0 6 0 8 0 0 6 7 0 8 0 0 0 0 0

# Baby it's cold outside
Be 4 0 6 5 4 0 8 0 0 0 0 0 5 0 7 6 5 0 8 0 0 0 0 0

# nobody home
Cf 1 1 6 0 6 0 6 6 6 6 6 0 6 0 0 0 0 0 6 6 0 0 0 6 5 6 0 5 0 0 0

# home on the range
Be 8 0 0 0 0 0 7 0 6 0 0 5 6 0 0 0 0 0 1 1 4 0 0 0 4 4 4 0 0 3 4 0 5 0  
**/

byte chordMode = 0;  // 1 = chord mode
int  noteLength = 250;

void setup()
{
  int x;
  for (x = 0; x < 9; ++x) {
    int pin = 5+x;
    pinMode(pin, OUTPUT);      // sets the digital pin as output
    digitalWrite(pin, LOW);
  }

  Serial.begin(9600);
  
}

void loop()
{
  while (Serial.available() ) {
    byte ch = Serial.read();
    Serial.write(ch); // echo to local term
    
    if (ch == '0') {
      if (chordMode) {
        delay(20);
        for (int x = 0; x < 9; ++x) {
          int pin = 5+x;
          digitalWrite(pin,LOW);
        }
        delay(noteLength-20); // !! subtract overhead
        chordMode = 0;
      } else {
        delay(noteLength); // !! subtract overhead
      }
    } else if (ch >= '1' && ch <= '9') {
      int pin = 5 + (ch - '1');
      digitalWrite(pin, HIGH);
      if (!chordMode) {
        delay(20);
        digitalWrite(pin, LOW);
        delay(noteLength-20); // !! subtractoverhead
      }
    } else if (ch >= 'A' && ch <= 'Z') { // first byte of note length
      noteLength = (ch - 'A') * 100;
    } else if (ch >= 'a' && ch <= 'z') { // second byte of note length
      noteLength += (ch - 'a') * 10;
      if (noteLength < 50) {
        noteLength = 50;
      }
      // Serial.write("nl="+noteLength);
    } else if (ch == '&') {
      chordMode = 1;
    } // ignore all others, including spaces

  } // end serial loop
}

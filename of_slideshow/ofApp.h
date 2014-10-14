#pragma once

#include "ofMain.h"
#include "ofxNetwork.h"

#define WINDOW_WIDTH 1024
#define WINDOW_HEIGHT 768

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void mousePressed(int x, int y, int button);
    
    ofImage current_picture;
    ofImage next_picture;
    int current_picture_index;
    ofDirectory picture_directory;
    
    ofTrueTypeFont font;
    string message;
    
    ofxUDPManager textMessageInput;
    ofxUDPManager toPython;
    
    bool message_trigger;
		
};

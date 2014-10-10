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
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);
    
    ofImage current_picture;
    ofImage next_picture;
    int current_picture_index;
    ofDirectory picture_directory;
    
    ofTrueTypeFont font;
    string message;
    
    ofxUDPManager textMessageInput;
		
};

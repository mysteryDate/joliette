#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){

    string path = "joliette_photos";
    ofDirectory dir(path);
    picture_directory.listDir(path);
    current_picture_index = 0;
    current_picture.loadImage(picture_directory.getPath(0));
    next_picture.loadImage(picture_directory.getPath(1));
    
    font.loadFont("shimmerbold_opentype.ttf", 30, true, true);
    
    textMessageInput.Create();
    textMessageInput.Bind(7011);
    textMessageInput.SetNonBlocking(true);
    message = "Hello";
    
    toPython.Create();
    toPython.Connect("127.0.0.1", 7012); // Assuming local machine for now
    toPython.SetNonBlocking(true);
    
    message_trigger = false;
    
}

//--------------------------------------------------------------
void ofApp::update(){

    int message_size = 100000;
    char textMessage[message_size];
    textMessageInput.Receive(textMessage, message_size);
    
    int currentTime = ofGetElapsedTimeMillis()/1000;
    if (currentTime % 3 == 0 and message_trigger and currentTime > 1) {
        // Copypasta from carte blanche project
        string message = "New message please!";
        int success = toPython.Send(message.c_str(), message.length());
        cout << success << endl;
        message_trigger = false;
    }
    if (currentTime % 2 == 0 and currentTime % 3 != 0){
        message_trigger = true;
    }
    
    if (textMessage[0] != 0) {
        message = textMessage;
    }
    
}

//--------------------------------------------------------------
void ofApp::draw(){

    int imgWidth = current_picture.width;
    int imgHeight = current_picture.height;
    float widthRatio = WINDOW_WIDTH / imgWidth;
    float heightRatio = WINDOW_HEIGHT / imgHeight;
    if (widthRatio < heightRatio) {
        widthRatio = heightRatio;
    }
    else
        heightRatio = widthRatio;
    current_picture.draw(0, 0, ofGetWindowWidth(), ofGetWindowHeight());
    font.drawString(message, 50, 50);
    
    stringstream reportStream;
    reportStream
    << "Framerate: " << ofToString((ofGetFrameRate())) << endl
    << "Time: " << ofToString(ofGetElapsedTimeMillis()/1000) << endl;
    ofDrawBitmapString(reportStream.str(), 100,600);
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){
    
    if (key == 'f' || key == 'F') {
        ofToggleFullscreen();
    }
}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

    current_picture_index++;
    if (current_picture_index == picture_directory.numFiles()) {
        current_picture_index = 0;
    }
    int next_picture_index = current_picture_index + 1;
    if (next_picture_index == picture_directory.numFiles()) {
        next_picture_index = 0;
    }
    current_picture = next_picture;
    next_picture.loadImage(picture_directory.getPath(current_picture_index));
}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){ 

}

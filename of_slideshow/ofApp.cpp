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
    
}

//--------------------------------------------------------------
void ofApp::update(){

}

//--------------------------------------------------------------
void ofApp::draw(){

    current_picture.draw(0, 0);
    font.drawString("Hello", 50, 50);
    
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){
    
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
    cout << current_picture_index;
    cout << picture_directory.numFiles();
    if (current_picture_index == picture_directory.numFiles()) {
        current_picture_index = 0;
    }
    current_picture.loadImage(picture_directory.getPath(current_picture_index));
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

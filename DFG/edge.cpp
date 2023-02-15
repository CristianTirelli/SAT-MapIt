#include "edge.h"

/************************************* EDGE *************************************/
edge::edge(int id, node* from, node* to, int distance, int latency)
{
	this->id = id;
	this->to = to;
  	this->from = from;
	this->distance = distance;
    this->latency = latency;

}

edge::~edge()
{
	
}

/******************* GET *******************/

int edge::getId(){
	return id;
}

int edge::getLatency(){
	return latency;
}

node* edge::getFrom(){
	return from;
}

node* edge::getTo(){
	return to;
}

int edge::getDistance(){
	return distance;
}

/******************* SET *******************/

void edge::setDistance(int d){
	distance = d;
}

void edge::setFrom(node* n){
	from = n;
}

void edge::setTo(node* n){
	to = n;
}

void edge::setLatency(int lat){
    latency = lat;
}
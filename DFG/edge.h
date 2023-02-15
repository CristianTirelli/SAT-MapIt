#ifndef EDGE_H_
#define EDGE_H_

#include "node.h"

class edge{
		int id;
		node* to;
		node* from;
		int distance;
        int latency;

	public:

		edge(int id, node *from, node *to, int distance, int latency = 1);
		virtual ~edge();

        /******************* GET *******************/
		int getId();
        int getLatency();
		node* getFrom();
		node* getTo();
		int getDistance();
        
        /******************* SET *******************/
		void setDistance(int d);
		void setFrom(node* n);
		void setTo(node* n);
        void setLatency(int lat);
};

#endif
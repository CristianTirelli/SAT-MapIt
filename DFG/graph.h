#ifndef GRAPH_H_
#define GRAPH_H_

#include <fstream> 

#include "llvm/IR/Value.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/Instructions.h"

#include "node.h"
#include "edge.h"
#include "utility.h"




namespace llvm{

	class graph{

		std::vector<node *> nodes;
		std::vector<edge *> edges;
		std::vector<constant* > constants;
		std::vector<node *> livein;
		std::vector<node *> liveout;
		std::vector<edge *> liveinedges;
		std::vector<edge *> liveoutedges;
		
		
	public:

		graph();
		virtual ~graph();

        /******************* ADD *******************/
		void addNode(node *n);
		void addEdge(edge* e);
		void addConstant(constant *c);
		void addLiveInNode(node* n);
		void addLiveOutNode(node* n);
		void addLiveInEdge(edge* e);
		void addLiveOutEdge(edge* e);

		/******************* GET *******************/
		node* getNode(Instruction* n);
		std::vector<node *> getNodes();
		std::vector<edge *> getEdges();
		std::vector<edge *> getAssociateEdges(node* n);
		std::vector<node *> getLiveInNodes();
		std::vector<node *> getLiveOutNodes();
		std::vector<constant *> getConstants();
		std::vector<node *> getSuccessors(node* n);
		std::vector<node *> getPredecessors(node* n);

		/******************* RMV *******************/
		void removeNode(node *n);
		void removeEdge(node *n);

		/******************* PRINT *******************/
		void printDot(std::string filename);
		void printNodes(std::string filename);
		void printEdges(std::string filename);
		void printConstants(std::string filename);
        void printLiveInNodes(std::string filename);
        void printLiveOutNodes(std::string filename);
		void printLiveInEdges(std::string filename);
		void printLiveOutEdges(std::string filename);
	};

}

#endif
#include "graph.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

/**************************** Graph ******************************************/
graph::graph(){

}

graph::~graph(){
	nodes.clear();
	edges.clear();
	constants.clear();
		
	livein.clear();
	liveout.clear();
	liveinedges.clear();
	liveoutedges.clear();
}

/******************* ADD *******************/

void graph::addNode(node *n){
	nodes.push_back(n);
}

void graph::addEdge(edge *a){
	edges.push_back(a);
}

void graph::addConstant(constant *c){
    constants.push_back(c);
}

void graph::addLiveInNode(node* n){
	livein.push_back(n);
}

void graph::addLiveOutNode(node* n){
	liveout.push_back(n);
}

void graph::addLiveInEdge(edge* e){
	liveinedges.push_back(e);
}

void graph::addLiveOutEdge(edge* e){
	liveoutedges.push_back(e);
}

/******************* GET *******************/

node* graph::getNode(Instruction* inst){
	for(auto node: nodes)
		if(dyn_cast<Instruction>(node->getInstruction()) == inst)
			return node;
	return nullptr;
}
std::vector<node *> graph::getNodes(){
	return nodes;
}

std::vector<edge *> graph::getEdges(){
	return edges;
}

std::vector<edge *> graph::getAssociateEdges(node* n){
	std::vector<edge *> associate_edges;
	for(auto e: edges){
		if(e->getFrom()->getId() == n->getId() || e->getTo()->getId() == n->getId()){
			if(std::find(associate_edges.begin(), associate_edges.end(), e) == associate_edges.end()){
				associate_edges.push_back(e);
			}
		}
	}

	for(auto e: liveinedges){
		if(e->getFrom()->getId() == n->getId() || e->getTo()->getId() == n->getId()){
			if(std::find(associate_edges.begin(), associate_edges.end(), e) == associate_edges.end()){
				associate_edges.push_back(e);
			}
		}
	}

	for(auto e: liveoutedges){
		if(e->getFrom()->getId() == n->getId() || e->getTo()->getId() == n->getId()){
			if(std::find(associate_edges.begin(), associate_edges.end(), e) == associate_edges.end()){
				associate_edges.push_back(e);
			}
		}
	}
		

	return associate_edges;
}

std::vector<node *> graph::getLiveInNodes(){
	return livein;
}

std::vector<node *> graph::getLiveOutNodes(){
	return liveout;
}

std::vector<constant *> graph::getConstants(){
	return constants;
}

std::vector<node *> graph::getSuccessors(node* n){
	std::vector<node *> succs;
	for(auto e: edges){
		if(e->getFrom()->getId() == n->getId()){
			if(std::find(succs.begin(), succs.end(), n) == succs.end()){
				succs.push_back(e->getTo());
			}
		}
	}
	return succs;
}

std::vector<node *> graph::getPredecessors(node* n){
	std::vector<node *> preds;
	for(auto e: edges){
		if(e->getTo()->getId() == n->getId()){
			if(std::find(preds.begin(), preds.end(), n) == preds.end()){
				preds.push_back(e->getFrom());
			}
		}
	}
	return preds;
}

/******************* PRINT *******************/

void graph::printDot(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_loop_graph.dot");
	dotFile.open(filename.c_str());
	dotFile << "digraph " << graphname << " { \n{\n compound=true;";

	//print nodes
	for (size_t i = 0; i < nodes.size(); i++){
		dotFile << "\n" << nodes[i]->getId() << " [color=black, label=\"" << nodes[i]->getId() << "  " << nodes[i]->getName() << "\"];\n";
	}

	//print edges
	for (size_t i = 0; i < edges.size(); i++){
		if (edges[i]->getFrom() != nullptr && edges[i]->getTo() != nullptr){
			if (edges[i]->getDistance() > 0)
			dotFile << edges[i]->getFrom()->getId() << " -> " << edges[i]->getTo()->getId() <<" [color=red]" << "\n";
			else
				dotFile << edges[i]->getFrom()->getId() << " -> " << edges[i]->getTo()->getId() << "\n";
		}else{ 
			errs()<< "ERROR on edge: " << edges[i] << "\n";
		}

	}
	
	//print constants
	for (size_t i = 0; i < constants.size(); i++){
		dotFile << "\n" << constants[i]->getId() << " [color=goldenrod1, label=\"" << constants[i]->getId() << " C_" << constants[i]->getImmediate() << "\"];\n";
	}

	//livein nodes
	for (size_t i = 0; i < livein.size(); i++){
		dotFile << "\n" << livein[i]->getId() << " [color=purple1, label=\"" << livein[i]->getId() << " " << livein[i]->getName() << "\"];\n";
	}
	
	//liveout nodes
	for (size_t i = 0; i < liveout.size(); i++){
		dotFile << "\n" << liveout[i]->getId() << " [color=dodgerblue1, label=\"" << liveout[i]->getId() << " " << liveout[i]->getName() << "\"];\n";
	}

	//print liveinedges
	for (size_t i = 0; i < liveinedges.size(); i++){
		if (liveinedges[i]->getFrom() != nullptr && liveinedges[i]->getTo() != nullptr)
			dotFile << liveinedges[i]->getFrom()->getId() << " -> " << liveinedges[i]->getTo()->getId() << " [color=purple1]" << "\n";
		else 
			errs()<< "ERROR on edge: " << liveinedges[i] << "\n";

	}
	
	//print liveoutedges
	for (size_t i = 0; i < liveoutedges.size(); i++){
		if (liveoutedges[i]->getFrom() != nullptr && liveoutedges[i]->getTo() != nullptr)
			dotFile << liveoutedges[i]->getFrom()->getId() << " -> " << liveoutedges[i]->getTo()->getId() << " [color=dodgerblue1]" << "\n";
		else 
			errs()<< "ERROR on edge: " << liveoutedges[i] << "\n";

	}
	
	//print constants edges
	for (size_t i = 0; i < constants.size(); i++){
		dotFile << constants[i]->getId() << " -> " << constants[i]->getNode()->getId() << " [color=goldenrod1]" << "\n";
	}
	
	dotFile << "\n}\n";

	dotFile << "\n}";
	dotFile.close();
}

void graph::printNodes(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_nodes");
	dotFile.open(filename.c_str());

	//print nodes 
	for (size_t i = 0; i < nodes.size(); i++){
		int id_LOp = -1;
		int id_ROp = -1;
		int opcode = nodes[i]->getOpcode();
		
		if(nodes[i] == nullptr){
			dotFile << "null ptr\n";
			continue;
		}
		
		if(nodes[i]->getLOp() != nullptr){
			id_LOp = nodes[i]->getLOp()->getId();
		}else{
			for(size_t j = 0; j < constants.size(); j++){
				if(constants[j]->getNode()->getId() == nodes[i]->getId())
					id_LOp = constants[j]->getId();
			}

			for(size_t j = 0; j < liveinedges.size(); j++){
				if(liveinedges[j]->getTo()->getId() == nodes[i]->getId())
					id_LOp = liveinedges[j]->getFrom()->getId();
			}
		}
		
		if(nodes[i]->getROp() != nullptr){
			id_ROp = nodes[i]->getROp()->getId();
		}else{
			for(size_t j = 0; j < constants.size(); j++){
				if(constants[j]->getNode()->getId() == nodes[i]->getId())
					id_ROp = constants[j]->getId();
			}

			for(size_t j = 0; j < liveinedges.size(); j++){
				if(liveinedges[j]->getTo()->getId() == nodes[i]->getId())
					id_ROp = liveinedges[j]->getFrom()->getId();
			}
		}
		
		if(nodes[i]->getPredicate() == nullptr){
		
			dotFile << nodes[i]->getId() << " " << nodes[i]->getInstructionName()<< " ";
			dotFile << id_LOp << " " << id_ROp << " " << "-1" << " " << opcode << "\n";
		
		}else{
			
			dotFile << nodes[i]->getId() << " " << nodes[i]->getInstructionName()<< " ";
			dotFile << id_LOp << " " << id_ROp << " " << nodes[i]->getPredicate()->getId() << " " << opcode << "\n";
		
		}
		
	}
	
	dotFile.close();
}

void graph::printEdges(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_edges");
	dotFile.open(filename.c_str());

	//print edges
	for (size_t i = 0; i < edges.size(); i++)
		dotFile << edges[i]->getFrom()->getId() << " " << edges[i]->getTo()->getId() << " " << edges[i]->getDistance() << " " << edges[i]->getLatency() <<  "\n";
	
	dotFile.close();
}

void graph::printConstants(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_constants");
	dotFile.open(filename.c_str());

	//print constants
	for (size_t i = 0; i < constants.size(); i++)
		dotFile << constants[i]->getId() << " " << constants[i]->getNode()->getId() << " " << constants[i]->getImmediate() << " " << constants[i]->getOpPos() << "\n";
	
	dotFile.close();
}

void graph::printLiveInNodes(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_liveinnodes");
	dotFile.open(filename.c_str());

	//print nodes 
	for (size_t i = 0; i < livein.size(); i++){
		dotFile << livein[i]->getId()<< "\n";
	}
	
	dotFile.close();
}

void graph::printLiveOutNodes(std::string filename){
	std::ofstream dotFile;
	std::string graphname = filename;
	filename.append("_liveoutnodes");
	dotFile.open(filename.c_str());

	//print nodes 
	for (size_t i = 0; i < liveout.size(); i++){
		dotFile << liveout[i]->getId()<< "\n";
	}
	
	dotFile.close();
}

void graph::printLiveInEdges(std::string filename){
	std::ofstream liveInFile;
	std::string edge = filename;
	
	edge.append("_livein_edges");
	liveInFile.open(edge.c_str());
	//print load nodes
	for (size_t i = 0; i < liveinedges.size(); i++){
		liveInFile << liveinedges[i]->getFrom()->getId() << " " << liveinedges[i]->getTo()->getId()  << " " << liveinedges[i]->getDistance() << " " << liveinedges[i]->getLatency() << "\n";
	}

	liveInFile.close();
}

void graph::printLiveOutEdges(std::string filename){
	std::ofstream liveOutFile;
	std::string edge = filename;
	
	edge.append("_liveout_edges");
	liveOutFile.open(edge.c_str());
	//print load nodes
	for (size_t i = 0; i < liveoutedges.size(); i++){
		liveOutFile << liveoutedges[i]->getFrom()->getId() << " " << liveoutedges[i]->getTo()->getId()  << " " << liveoutedges[i]->getDistance() << " " << liveoutedges[i]->getLatency() << "\n";
	}

	liveOutFile.close();
}

/******************* RMV *******************/

void graph::removeNode(node* n){
	//n should have only one pre
	if(getPredecessors(n).size() > 1){
		errs() << "Should have only one pred\n";
		return;
	}

	node* pre = getPredecessors(n)[0];
	
	std::vector<edge *> to_remove;
	//update successors assignment
	for(auto suc: getSuccessors(n)){
		if(suc->getLOp() == n){
			suc->setLOp(pre);
		}
		if(suc->getROp() == n){
			suc->setROp(pre);
		}
		if(suc->getPredicate() == n){
			suc->setPredicate(pre);
		}
	}

	//update edges
	for(auto e: getAssociateEdges(n)){
		if(e->getFrom()->getId() == n->getId()){
			e->setFrom(pre);
		}
		if(e->getTo()->getId() == n->getId()){
			//remove edge
			if(std::find(to_remove.begin(), to_remove.end(), e) == to_remove.end())
				to_remove.push_back(e);

		}
	}

	nodes.erase(std::remove(nodes.begin(), nodes.end(), n), nodes.end());
	for(auto e: to_remove){
		edges.erase(std::remove(edges.begin(), edges.end(), e), edges.end());
	}

}

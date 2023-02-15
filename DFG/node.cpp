#include "node.h"

/************************************ NODE ************************************/
node::node(int id, std::string name, llvm::Value* inst)
{	
	this->id = id;
	this->name = name;
	this->inst = inst;
    
	instruction_name = "None";
    l_op = nullptr;
    r_op = nullptr;
	predicate = nullptr;
	opcode = -10;
}

node::~node()
{
    operands.clear();
}

/******************* GET *******************/

llvm::Value *node::getInstruction(){
	return inst;
}

std::string node::getName(){
	return name;
}

int node::getId(){
	return id;
}

std::string node::getInstructionName(){
	return instruction_name;
}

node* node::getPredicate(){
	return predicate;
}

node* node::getLOp(){
	return l_op;
}

node* node::getROp(){
	return r_op;
}

int node::getOpcode(){
	return opcode;
}

/******************* SET *******************/

void node::setLOp(node* op){
	l_op = op;
}

void node::setROp(node* op){
	r_op = op;
}

void node::setPredicate(node* p){
	predicate = p;
}

void node::setName(std::string n){
	name = n;
}

void node::setInstructionName(std::string name){
	instruction_name = name;
}

void node::setOpcode(int op){
	opcode = op;
}

void node::swapOperands(){
	node *tmp = l_op;
	l_op = r_op;
	r_op = tmp;
}

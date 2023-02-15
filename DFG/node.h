#ifndef NODE_H_
#define NODE_H_

#include "llvm/IR/Value.h"
#include "llvm/IR/Instruction.h"

#include <string>
#include <vector>

//new node
class constant;
class node{

		int id;
		std::string name;
		llvm::Value* inst;
		std::string instruction_name;
		int opcode;

		node* l_op;
		node* r_op;
		node* predicate;
		//TODO: handle cases with more than 3 operands
		std::vector<node*> operands;

		public:
			
			node(int id, std::string name, llvm::Value* inst);
			virtual ~node();

			/******************* GET *******************/
			llvm::Value* getInstruction();
			std::string getName();
			int getId();
			std::string getInstructionName();
			node* getPredicate();
			node* getLOp();
			node* getROp();
			int getOpcode();

			/******************* SET *******************/
			void setLOp(node* l);
			void setROp(node* r);
			void setPredicate(node* p);
			void setName(std::string n);
			void setInstructionName(std::string name);
			void setOpcode(int op);
			//needed to handle some icmp and select cases
			void swapOperands();

	};
class constant{
	int id;
	node* inst;
	int immediate;
	int opPos; 
	//1 for right operand position 
	//0 for left operand position 
	
	public:

		constant(int id, node* inst, int immediate){this->inst = inst; this->immediate = immediate; this->id = id; opPos = 1;};
		virtual~constant(){};

		/******************* GET *******************/
		int getId(){return id;};
		node* getNode(){return inst;};
		int getImmediate(){return immediate;};
		int getOpPos(){return opPos;};

		/******************* SET *******************/
		void setImmediate(int c){immediate = c;};
		void setInstruction(node* n){inst = n;};
		void setOpPos(int p){opPos = p;};
};
#endif
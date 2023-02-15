#include "llvm/Pass.h"

#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/IR/DebugLoc.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/Analysis/LoopPass.h"

#include "llvm/IR/InstrTypes.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

#include "graph.h"

#include <string>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <limits>
#include <iterator>
#include <stack>
#include <algorithm>

#define DEBUG 0
int inn = 0;

using namespace llvm;

int nodeId = 0;
int edgeId = 0;
std::string flG;
namespace {
//custom Flow Graph structure
  struct DFG : public LoopPass {
    static char ID;
    DFG() : LoopPass(ID) {}

      void getAnalysisUsage(AnalysisUsage &AU) const override {
        AU.addRequired<LoopInfoWrapperPass>();
        AU.addPreserved<LoopInfoWrapperPass>();
        
        AU.setPreservesAll();
      }

    std::fstream& GotoLine(std::fstream& file, int num){
      file.seekg(std::ios::beg);
      for(int i=0; i < num - 1; ++i){
          file.ignore(std::numeric_limits<std::streamsize>::max(),'\n');
      }
      return file;
    }

    //Not the correct way to do it
    //NOTE: DO NOT MODIFY ANYTHING RELATED TO THE NODE ID
    int getDistance(node* from, node* to){

      if(from->getId() < to->getId())
        return 0;
      return 1;

    }

    void addNode(Instruction* inst, graph *g){
      node* n;
      std::fstream myfile;
      std::string name="";
      std::string instruction_name;
      raw_string_ostream rso(name);
      
      inst->print(rso);
      //Assign to each instruction the corrisponding C code, by appending to name the associate line of code
      //NOTE: When compiling with optimization eg -O3 this relation is not garanted
      //      To enable this feature the code should be compiled with debug information eg -g
      if (DILocation *Loc = inst->getDebugLoc()) {
          int Line = Loc->getLine();
          StringRef File = Loc->getFilename();
          StringRef Dir = Loc->getDirectory();
          //bool ImplicitCode = Loc->isImplicitCode();
          std::string line;
          myfile.open(Dir.str() + "/" + File.str());
          GotoLine(myfile, Line);
          getline(myfile,line);
          //strip from string \t chars
          line.erase(std::remove(line.begin(),line.end(),'\t'),line.end());
          name = name + "\n" + line;
          myfile.close();
      }

      if(inst->getOpcode() == Instruction::ICmp){
        if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OEQ
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UEQ
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_EQ)
				{
					instruction_name = "cmpEQ";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ONE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UNE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_NE)
				{
					instruction_name = "cmpNEQ";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OGT
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UGT
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SGT)
				{
					instruction_name = "cmpSGT";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_UGT)
				{
					instruction_name = "cmpUGT";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OGE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UGE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SGE)
				{
					instruction_name = "cmpSGEQ";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_UGE)
				{
					instruction_name = "cmpUGEQ";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OLT
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ULT
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SLT)
				{
					instruction_name = "cmpSLT";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_ULT)
				{
					instruction_name = "cmpULT";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OLE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ULE
				|| cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SLE)
				{
					instruction_name = "cmpSLEQ";
				}
				else if (cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_ULE)
				{
					instruction_name = "cmpULEQ";
				}
      }else{
        instruction_name = inst->getOpcodeName();
      }
      
      n = new node(nodeId++, name, dyn_cast<Value>(inst));
      n->setInstructionName(instruction_name);
      g->addNode(n);
      
    }

    void addDependency(Instruction* s_inst, graph *g){
    
      for(User *U: s_inst->users()){
        if (Instruction *d_inst = dyn_cast<Instruction>(U)) {
          node *destination, *source;
          edge* e;
          destination = g->getNode(d_inst);
          source = g->getNode(s_inst);
          
          if(source == nullptr or destination == nullptr){
            //errs() << "Probably some liveine or const value\n\t" << *s_inst << "\n\t" << *d_inst <<"\n";
            continue;
          }

          
          int distance = getDistance(source, destination);
          //errs() << "Distance of (" << n2->getId() << ", " << n1->getId() << ")= " << distance << "\n";
          e = new edge(edgeId++, source, destination, distance);
          g->addEdge(e);
        }
      }
    }

    
    //Adds livein values to the DFG
    //return vector only for debug, can remove later
    //TODO: Fix case pointer of pointer 
    std::vector<Value *> getLiveIn(Function* F, graph* g, Instruction* first_loop_inst){
      std::vector<Value *> livein;
      std::vector<node *> nodes = g->getNodes();
      node* source; 

      nodeId = nodeId + 10;

      for(node* n: nodes){
        Instruction *current_node_inst = dyn_cast<Instruction>(n->getInstruction());

        for (Use &operand_current_node : current_node_inst->operands()) {
          Value *v = operand_current_node.get();
          if(Instruction *operand_inst = dyn_cast<Instruction>(v)){//operand defined by instruction
            
            
            bool before = true;
            for(BasicBlock &B: *F){//iterate over all the bbs of the function
              for(Instruction &I: B){//and over all the instructions in the bbs
                if((&I == first_loop_inst ) || first_loop_inst == operand_inst)//stop when you get to the first loop instruction
                  before = false;

                if(&I == operand_inst && before && std::find(livein.begin(), livein.end(), &I) == livein.end() ){
                  source = new node(nodeId++, "LiveInInst", dyn_cast<Value>(&I));
                  //save livein dep
                  
                  for(User *U: dyn_cast<Value>(&I)->users()){
                    if (Instruction *succ = dyn_cast<Instruction>(U)) {
                      
                      node *destination;
                      edge* e;
                      destination = g->getNode(succ);

                      if(destination == nullptr)
                        continue;
                      
                      e = new edge(edgeId++, source, destination ,0);
                      g->addLiveInEdge(e);
                    }
                  }
                  g->addLiveInNode(source);
                  livein.push_back(dyn_cast<Value>(&I));
                }
              }
            }
          }else if(Argument *arg = dyn_cast<Argument>(operand_current_node)){//operand defined by function argument
            Value * varg = dyn_cast<Value>(arg);
            
            if(std::find(livein.begin(), livein.end(), varg) == livein.end() ){
              source = new node(nodeId++, "LiveInArg", varg);
              for(User *U: varg->users()){
                    if (Instruction *succ = dyn_cast<Instruction>(U)) {
                      node *destination;
                      edge* e;
                      destination = g->getNode(succ);
                      if(destination == nullptr) 
                        continue;
                      
                      e = new edge(edgeId++, source ,destination ,0);
                      g->addLiveInEdge(e);
                    }
                    
                  }
              
              g->addLiveInNode(source);
              
              livein.push_back(varg);
            }
          //stripPointerCasts takes care of bitcast function so I can forget about the isPointerTy 
          }else if(GlobalVariable *gbvar = dyn_cast<GlobalVariable>(operand_current_node->stripPointerCasts())){//operand defined by global variable
            //errs() << "gvar\n";
            //errs() << *operand_current_node << "\n";
            Value * varg = dyn_cast<Value>(gbvar);
            if(std::find(livein.begin(), livein.end(), varg) == livein.end() ){
              source = new node(nodeId++, "LiveInGVar", varg);
              bool has_reference = false;
              for(User *U: varg->users()){
                    if (Instruction *succ = dyn_cast<Instruction>(U)) {
                      has_reference = true;
                      node *destination;
                      edge* e;
                      destination = g->getNode(succ);
                      if(destination == nullptr)
                        continue;
                      
                      e = new edge(edgeId++, source ,destination ,0);
                      g->addLiveInEdge(e);
                    }
                  }
              if(has_reference){
                g->addLiveInNode(source);
              }
              
              livein.push_back(varg);
            }
          }
        }
      }
      return livein;

    }

    //Adds liveout values to the DFG
    //return vector only for debug, can remove later
    std::vector<Instruction*> getLiveOut(Function* F, graph* g, Instruction* lastInst){

      std::vector<Instruction*> liveout;
      std::vector<node*> nodes = g->getNodes();
      node* destination; 
      edge* e;
      nodeId = nodeId + 10;

      for(node* n: nodes){
        Instruction *curr = dyn_cast<Instruction>(n->getInstruction());
        for(User *U: curr->users()){
          if (Instruction *succ = dyn_cast<Instruction>(U)) {
            if(g->getNode(succ) == nullptr && std::find(liveout.begin(), liveout.end(), curr) == liveout.end() && succ != lastInst){
              destination = new node(nodeId++, "LiveOut", dyn_cast<Value>(succ));
              e = new edge(edgeId++, n, destination, 0);
              //errs() << *succ << " liveout di " << *curr << '\n';
              g->addLiveOutNode(destination);
              liveout.push_back(succ);
              g->addLiveOutEdge(e);
            }
          }
        }
      }

      return liveout;

      
    }

    //Save operands assignment of the IR
    //They are used by SAT-MapIt to generate the correct instruction
    void assignOperands(graph *g){

      std::vector<node*> nodes = g->getNodes();
      for(auto n: nodes){
        Instruction *curr = dyn_cast<Instruction>(n->getInstruction());
        int n_ops = curr->getNumOperands();
        if(n_ops > 3){
          errs() << "More than 3 operands for inst " << n->getName() << "\nTo handle\n";
          continue;
        }else if(n_ops == 3 && curr->getOpcode() == Instruction::Select){

          SelectInst *curr_sel = dyn_cast<SelectInst>(curr);
          node* tmp;
          n->setPredicate(g->getNode(dyn_cast<Instruction>(curr_sel->getCondition())));
          //I don't care if tmp is a nullptr since I'll handle this case in the printNodes function
          tmp = g->getNode(dyn_cast<Instruction>(curr_sel->getTrueValue()));
          n->setLOp(tmp);
          tmp = g->getNode(dyn_cast<Instruction>(curr_sel->getFalseValue()));
          n->setROp(tmp);
          
        }else if(n_ops == 3 && curr->getOpcode() == Instruction::GetElementPtr){
          //TODO: check this
          node* tmp;
          tmp = g->getNode(dyn_cast<Instruction>(curr->getOperand(n_ops - 1)));
          n->setROp(tmp);
          
        }else if(n_ops == 2){
          n->setLOp(g->getNode(dyn_cast<Instruction>(curr->getOperand(0))));
          n->setROp(g->getNode(dyn_cast<Instruction>(curr->getOperand(1))));

        }else if (n_ops == 1){
          //errs() << "1 operand inst " << n->getName() << "\n";
          n->setLOp(g->getNode(dyn_cast<Instruction>(curr->getOperand(0))));

        }else if(curr->getOpcode() == Instruction::Br){
          BranchInst *cbr = dyn_cast<BranchInst>(curr);
            if (cbr->isConditional()){
              node* tmp;
              tmp = g->getNode(dyn_cast<Instruction>(cbr->getCondition()));
              n->setROp(tmp); 
            }
        }else{
          errs() << "No assignment for instuction" << n->getName() << "\n";
          continue;
        }

      }

    }

    //Adds constants values to the DFG
    void addConstants(graph* g){
      std::vector<node *> nodes = g->getNodes();
      constant* c;
      nodeId = nodeId + 10; //+10 just for debugging purpose can ca the usual nodeId++
      for(auto n: nodes){
        Instruction* inst = dyn_cast<Instruction>(n->getInstruction());
        //if constant is used in icmp to set the flag for a br then add a livein instead
        if (inst->getOpcode() == Instruction::ICmp){
          
          //if(g->getSuccessors(n).size() == 1)
          //{
          //  node *source;
          //  node *destination;
          //  edge *e;
          //  source = new node(nodeId++, "LiveInConstBr", dyn_cast<Value>(inst));
          //  destination = g->getNode(inst);
          //  e = new edge(edgeId++, source, destination, 0);
          //  g->addLiveInNode(source);
          //  g->addLiveInEdge(e);
          //  continue;
          //}
          //else{
          //  errs() << "Handle icmp with more than one succ\n";
          //  exit(0);
          //}
          
        }
        
        if(inst != nullptr && inst->getOpcode() != Instruction::GetElementPtr && !isa<BranchInst>(inst) ){
          for(int i = 0; i < (int) inst->getNumOperands(); i++){
            if (ConstantInt *CI = dyn_cast<ConstantInt>(inst->getOperand(i))){
              if ((int) CI->getSExtValue() > 4096 || (int) CI->getSExtValue() < - 4097){
                //if the constant is too big it cannot be put as in
                //the immediate fields of the CGRA_WORD, so we put it
                //in a register (like a livein var)
                node *source;
                node *destination;
                edge *e;
                source = new node(nodeId++, "LiveInConst", dyn_cast<Value>(inst));
                destination = g->getNode(inst);
                e = new edge(edgeId++, source, destination, 0);
                g->addLiveInNode(source);
                g->addLiveInEdge(e);
              }else if (inst->getOpcode() == Instruction::ICmp && g->getSuccessors(n).size() == 1){
                //TODO: check taht succ is a br instruction
                node *source;
                node *destination;
                edge *e;
                source = new node(nodeId++, "LiveInConstBr", dyn_cast<Value>(inst));
                destination = g->getNode(inst);
                e = new edge(edgeId++, source, destination, 0);
                g->addLiveInNode(source);
                g->addLiveInEdge(e);
                
              }else{
                //Comment everything ecxept the following two line
                //if IS is disabled
                c = new constant(nodeId++, n, (int) CI->getSExtValue());
                g->addConstant(c);
              }

              
              //errs() << "Adding constant for node : " << *n->getInstruction();
            }
          }
        }
      }
    }

    //Check what kind of br is assigned to node n 
    bool isLess(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_ULT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OLT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ULT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SLT){
            return true;
          }

      return false;
    }

    //Check what kind of br is assigned to node n 
    bool isLessEqual(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OLE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ULE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SLE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_ULE){
            return true;
          }

      return false;
    }

    //Check what kind of br is assigned to node n 
    bool isGreater(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OGT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UGT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SGT
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_UGT){
            return true;
          }

      return false;
    }

    //Check what kind of br is assigned to node n 
    bool isGreaterEqual(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OGE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_UGE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UGE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_SGE){
            return true;
          }

      return false;
    }

    //Check what kind of br is assigned to node n 
    bool isEqual(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_OEQ
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UEQ
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_EQ){
            return true;
          }

      return false;
    }

    //Check what kind of br is assigned to node n 
    bool isNotEqual(node* n){
      Instruction *inst = dyn_cast<Instruction>(n->getInstruction());
      
      if(cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_ONE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::FCMP_UNE
          || cast<CmpInst>(inst)->getPredicate() == llvm::CmpInst::ICMP_NE){
            return true;
          }

      return false;
    }

    //Adapt IR to the ISA of the CGRA (EPFL ISA)
    //TODO: Distinguish between unsigned and signd operations
    //      for now they are all considered signed, but the ISA needs to 
    //      be extended to support also unsigned operations
    //TODO: Fix case pointer of pointer
    void instructionSelection(graph* g){

      std::vector<node *> nodes = g->getNodes();
      std::vector<edge *> edges = g->getEdges();

      std::vector<node *> new_nodes;
      std::vector<edge *> new_edges;

      std::vector<node *> node_to_delete;
      std::vector<edge *> edge_to_delete;
    
      for(auto n: nodes){
        
        Instruction* inst = dyn_cast<Instruction>(n->getInstruction());
        //errs() << "Doing " << inst->getOpcodeName() << "\n";
        switch(inst->getOpcode()){
          case Instruction::Add:
            n->setOpcode(SADD);
            break;
          case Instruction::Sub:
            n->setOpcode(SSUB);
            break;
          case Instruction::Mul:
            n->setOpcode(SMUL);
            break;
          case Instruction::Shl:
            n->setOpcode(SLT);
            break;
          case Instruction::LShr:
            n->setOpcode(SRT);
            break;
          case Instruction::AShr:
            n->setOpcode(SRT);
            break;
          case Instruction::And:
            n->setOpcode(LAND);
            break;
          case Instruction::Or:
            n->setOpcode(LOR);
            break;
          case Instruction::Xor:
            n->setOpcode(LXOR);
            break;
          case Instruction::FAdd:
            n->setOpcode(FXP_ADD);
            break;
          case Instruction::FSub:
            n->setOpcode(FXP_SUB);
            break;
          case Instruction::FDiv:
            n->setOpcode(FXP_DIV);
            break;
          case Instruction::FMul:
            n->setOpcode(FXP_MUL);
            break;
          case Instruction::Load:
            n->setOpcode(LWI);
            break;
          case Instruction::Store:
            n->setOpcode(SWI);
            break;
          case Instruction::Trunc:
          {	
            if(g->getPredecessors(n).size() > 1){
              //should not happen, just a safety check
              errs() << "Trunc with more then 1 pred\n";
              break;
            }


            node_to_delete.push_back(n);
            break;
          }
          case Instruction::SExt:
          {
            if(g->getPredecessors(n).size() > 1){
              //should not happen, just a safety check
              errs() << "Trunc with more then 1 pred\n";
              break;
            }
            
            node_to_delete.push_back(n);
            break;
          }
          case Instruction::Select:
            //n->setOpcode(BSFA);
            //don't do anything since it's going to be set, when handling the icmp instr
            break;
          case Instruction::ZExt:{

            if(g->getPredecessors(n).size() > 1){
              //should not happen, just a safety check
              errs() << "Trunc with more then 1 pred\n";
              break;
            }

            node_to_delete.push_back(n);
            break;
          }
          case Instruction::PHI:
            n->setOpcode(MV);
            break;
          case Instruction::GetElementPtr:{
            //TODO:: Handle matrix and array of pointers etc
            
            //multiple way to handle this. The base address could retrived by making a load
            //this would reduce the register pressure but on average it will probably be not the best
            //solution, that's why for now we don't care about register pressure and we store the address in a register
            //maybe the can be also handled in the backend

            //getelemntptr node is going to be replaced by one node that compute the offset and 
            //one that compute offset + base address
            //
            // node1 = 4 * index 
            // node2 = base_addr + node1
            // node2 will have a livein that is addr and an incoming edge that is node1
            // n is going to be replaced by node 2 (so that only one assignment needs to be changed)
            
            
            node* offset;
            edge* offset_edge;
            std::vector<edge *> associate_edges = g->getAssociateEdges(n);
            std::vector<node *> livein_nodes = g->getLiveInNodes();

            n->setOpcode(SADD);
            n->setName("add");
            n->setInstructionName("add");

            offset = new node(nodeId++,"offset", nullptr);
            offset->setOpcode(SMUL);
            offset->setInstructionName("mul");
            offset->setLOp(n->getROp());
            n->setROp(offset);
            constant* c;
            c = new constant(nodeId++, offset, 4);//i*4 should be 1,2 or 4 but for now in the ISA there is only load word
            g->addConstant(c);
            g->addNode(offset);

            //livein edges do not change. need to fix only edge going in n and 
            for(auto e: associate_edges){
              if(e->getTo()->getId() == n->getId()){
                bool found = false;
                for(auto ln: livein_nodes){
                  if(ln->getId() == e->getFrom()->getId()){
                    found = true;
                  }
                }
                if(!found)
                  e->setTo(offset);
              }
            }

            offset_edge = new edge(edgeId++, offset, n, 0);
            g->addEdge(offset_edge);


            //TODO: the address can also be computed from an Inst (ie pointer of pointer)
            //must handle also this case in the future
            
            break;
        }
          case Instruction::Br:{
            //Should be solved from the icmp
            //Only need to handle unconditional branches 
            //NOT HANDLED RIGHT NOW, need to find possible problematic cases
            BranchInst *cbr = dyn_cast<BranchInst>(inst);
            if (cbr->isUnconditional()){
              errs() << "Unconditional jumps not handled rigth now\n";
              break;
            }else{
              //Should not happen
              if(dyn_cast<Instruction>(cbr->getCondition())->getOpcode() != Instruction::ICmp){
                errs() << "Not using iCMP condition\n" << *cbr->getCondition() << "\n";
                break;
              }
            }
            break;
        }
          case Instruction::ICmp:{

            //TODO: need to divide in case where icmp is used by only one br, icmp used by br and inst, br used by inst
            //CHECK IF YOU CAN LEAVE THE ICMP AND ALWAYS USE A SUB INST INSTEAD (wih this sometimes you will have the same number
            // of nodes, so no reduction by compressing the instruction)
            //if (g->getSuccessors(n).size() > 1){
            //  errs() << "TODO Handle\n";
            //  for(auto t: g->getSuccessors(n)){
            //    errs() << "Succ of icmp " << t->getName() << "\n";
            //  }
            //  break;
            //}

            std::string op;
            int cmpopcode = -1;
            if (isEqual(n))
            {
              op = "beq";
              cmpopcode = BEQ;
            }
            else if (isNotEqual(n))
            {
              op = "bne";
              cmpopcode = BNE;
            }
            else if (isGreater(n))
            {
              op = "bgt";
              cmpopcode = BGT; 
            }
            else if (isGreaterEqual(n))
            {
              op = "bge";
              cmpopcode = BGE;
            }
            else if (isLess(n))
            {
              op = "blt";
              cmpopcode = BLT;
            }
            else if (isLessEqual(n))
            {
              op = "ble";
              cmpopcode = BLE;
            }
            
            if(cmpopcode != -1){
              
              if(g->getSuccessors(n).size() == 1 
                && dyn_cast<Instruction>(g->getSuccessors(n)[0]->getInstruction())->getOpcode() == Instruction::Br)
              {
                //Don't have to add another node, I can modify icmp and then remove the br node
                n->setOpcode(cmpopcode);
                n->setInstructionName(op);
                node_to_delete.push_back(g->getSuccessors(n)[0]);
                //Don't have to modify the assignments since the br node is removed and compacted with the icmp that already has a proper assignment (or at least should have)
              }else if(g->getSuccessors(n).size() == 1 
                && dyn_cast<Instruction>(g->getSuccessors(n)[0]->getInstruction())->getOpcode() == Instruction::Select)
                {
                  n->setInstructionName("sub");
                  n->setOpcode(SSUB);
                  Instruction *suc_inst = dyn_cast<Instruction>(g->getSuccessors(n)[0]->getInstruction());
                  node *succ_node = g->getNode(suc_inst);
                  if(succ_node == nullptr){
                    errs() << "Node should be in DFG\n";
                    exit(0);
                  }

                  if(isEqual(n) || isNotEqual(n))
                      {
                      //eq and neq
                        succ_node->setInstructionName("bzfa");
                        succ_node->setOpcode(BZFA);
                  }else if (isLess(n) || isGreater(n)){
                    //l and g
                    succ_node->setInstructionName("bsfa");
                    succ_node->setOpcode(BSFA);
                  }else if(isGreaterEqual(n) || isLessEqual(n)){
                    //ge and le
                    errs() << "Fix icmp ge and le\n";
                  }


              }else{

                n->setInstructionName("sub");
                n->setOpcode(SSUB);

                for(auto succ_node: g->getSuccessors(n)){
                  Instruction *succ_inst = dyn_cast<Instruction>(succ_node->getInstruction());
                  if(succ_inst->getOpcode() == Instruction::Select){
                    if(isLess(n) || isGreater(n)){
                      errs() << "less or greater\n";
                      succ_node->setOpcode(BSFA);
                      succ_node->setInstructionName("bsfa");
                    }else if(isEqual(n) || isNotEqual(n)){
                      succ_node->setOpcode(BZFA);
                      succ_node->setInstructionName("bzfa");
                    }else{
                      errs() << "Handle <= and >= cases, probably due to unoptimized code";
                    }
                  }else{
                    //In all the other cases you should add nodes such that
                    //you can use the flag as data in a register
                    if(isLess(n) || isGreater(n)){
                      //create nodes  to check the flags
                      node *n1;
                      constant *c1, *c2;

                      n1 = new node(nodeId++,"bsfa", nullptr);
                      n1->setOpcode(BSFA);
                      n1->setInstructionName("bsfa");
                      n1->setPredicate(n);
                      
                      c1 = new constant(nodeId++, n1, 0);
                      c2 = new constant(nodeId++, n1, 1);

                        //less 
                      if(isLess(n)){
                        
                        c2->setOpPos(0);
                        //greater 
                        }else if(isGreater(n)){
                        c1->setOpPos(0); 
                        
                        }else{
                        errs() << "Should not be in this if case (<, >)\n";
                      }
                      g->addNode(n1);
                      g->addConstant(c1);
                      g->addConstant(c2);
                      
                      //update dependencies

                      for(auto e: g->getAssociateEdges(n)){
                        if(e->getFrom()->getId() == n->getId() && dyn_cast<Instruction>(e->getTo()->getInstruction())->getOpcode() != Instruction::Select){
                          e->setFrom(n1);
                          if(e->getTo()->getLOp() != nullptr && e->getTo()->getLOp()->getId() == n->getId()){
                            e->getTo()->setLOp(n1);
                          }
                          if(e->getTo()->getROp() != nullptr && e->getTo()->getROp()->getId() == n->getId()){
                            e->getTo()->setROp(n1);
                          }
                          if(e->getTo()->getPredicate() != nullptr && e->getTo()->getPredicate()->getId() == n->getId()){
                            e->getTo()->setPredicate(n1);
                          }
                        }
                      }

                      edge *e1;
                      e1 = new edge(edgeId++, n, n1, 0);
                      
                      g->addEdge(e1);
                    }else if(isEqual(n) || isNotEqual(n)){
                      //create nodes  to check the flags
                      node *n1;
                      constant *c1, *c2;

                      n1 = new node(nodeId++,"bzfa", nullptr);
                      n1->setOpcode(BZFA);
                      n1->setInstructionName("bzfa");
                      n1->setPredicate(n);
                      
                      c1 = new constant(nodeId++, n1, 0);
                      c2 = new constant(nodeId++, n1, 1);
                      //actually I don't need the following if cases, since 
                      //icmp fix the operands according to == or !=
                      //(basically position of c1 and c2 can be fixed from the start)
                      //not equal to zero
                      if(isNotEqual(n)){
                        c1->setOpPos(0);
                      //equal to zero
                      }else if(isEqual(n))
                              {
                        c2->setOpPos(0);
                      }else{
                        errs() << "Should not be in this if case (==, !=)\n";
                      }
                      
                      g->addNode(n1);
                      g->addConstant(c1);
                      g->addConstant(c2);
                      
                      //update dependencies
                      for(auto e: g->getAssociateEdges(n)){
                        if(e->getFrom()->getId() == n->getId() && dyn_cast<Instruction>(e->getTo()->getInstruction())->getOpcode() != Instruction::Select){
                          e->setFrom(n1);
                        }
                      }

                      edge *e1;
                      e1 = new edge(edgeId++, n, n1, 0);
                      
                      g->addEdge(e1);
                    }else{
                      errs() << "Handle <= and >= cases, probably due to unoptimized code";
                    }
                    
                  }


                }
                //TODO check if all those cases are necessary
                //<= can be done with > and a swap of the operands in the next instruction
                //Add nodes and leave br ins becomes beq
                

                //if <= or >= add two nodes to check each flag and one node to
                // do the or between them
                //else just add one node that check one of those (depending on which flag)
                /*
                if (isLessEqual(n) || isGreaterEqual(n))
                  {
                    errs() << "le or ge\n";

                    //create nodes  to check the flags
                    node *n1, *n2;
                    constant *c1, *c2;
                    constant *c3, *c4;

                    n1 = new node(nodeId++,"bsfa", nullptr);
                    n1->setOpcode(BSFA);
                    n1->setInstructionName("bsfa");
                    n1->setPredicate(n);

                    n2 = new node(nodeId++,"bzfa", nullptr);
                    n2->setOpcode(BZFA);
                    n2->setInstructionName("bzfa");
                    n2->setPredicate(n);
                    
                    //constants for sign flag
                    //need to distinguish between less and greater
                    //if less then output constant should be 1
                    //if greate then outputconstant should be 0
                    // beq instruction will always compare with 1
                    //we fix the jump instruction to compare with 1
                    //could be made variable (beq with 1 or 0) depending
                    //on if less or greater                   
                    c1 = new constant(nodeId++, n1, 0);
                    c2 = new constant(nodeId++, n1, 1);
                    //less equal
                    if(isLessEqual(n))
                      {
                        
                        c2->setOpPos(0);
                    //greater equal
                    }else if(isGreaterEqual(n))
                    {

                      c1->setOpPos(0); 
                    }else{
                      errs() << "Should not be in this if case (<=, >=)\n";
                    }

                    //constants for zero flag
                    //if zero flag is set 1 should be in the outreg
                    //left operand is output so c4 is set to zero
                    c3 = new constant(nodeId++, n2, 0);
                    c4 = new constant(nodeId++, n2, 1);
                    c4->setOpPos(0);

                    g->addNode(n1);
                    g->addNode(n2);
                    g->addConstant(c1);
                    g->addConstant(c2);
                    g->addConstant(c3);
                    g->addConstant(c4);
                    

                    //create or node
                    node *n3;
                    n3 = new node(nodeId++,"or", nullptr);
                    n3->setOpcode(LOR);
                    n3->setInstructionName("lor");
                    
                    n3->setLOp(n1);
                    n3->setROp(n2);

                    g->addNode(n3);
                    //update dependencies

                    for(auto e: g->getAssociateEdges(n)){
                      if(e->getFrom()->getId() == n->getId()){
                        e->setFrom(n3);
                      }
                    }

                    edge *e1, *e2, *e3, *e4;
                    e1 = new edge(edgeId++, n, n1, 0);
                    e2 = new edge(edgeId++, n, n2, 0);
                    e3 = new edge(edgeId++, n1, n3, 0);
                    e4 = new edge(edgeId++, n2, n3, 0);
                    
                    g->addEdge(e1);
                    g->addEdge(e2);
                    g->addEdge(e3);
                    g->addEdge(e4);

                    
                  }else if (isEqual(n) || isNotEqual(n))
                  {
                    errs() << "eq or neq\n";

                    //create nodes  to check the flags
                    node *n1;
                    constant *c1, *c2;

                    n1 = new node(nodeId++,"bzfa", nullptr);
                    n1->setOpcode(BZFA);
                    n1->setInstructionName("bzfa");
                    n1->setPredicate(n);
                    
                    c1 = new constant(nodeId++, n1, 0);
                    c2 = new constant(nodeId++, n1, 1);
                    //not equal to zero
                    if(isNotEqual(n)){
                      c1->setOpPos(0);
                    //equal to zero
                    }else if(isEqual(n))
                            {
                      c2->setOpPos(0);
                    }else{
                      errs() << "Should not be in this if case (==, !=)\n";
                    }
                    
                    g->addNode(n1);
                    g->addConstant(c1);
                    g->addConstant(c2);
                    
                    //update dependencies
                    for(auto e: g->getAssociateEdges(n)){
                      if(e->getFrom()->getId() == n->getId()){
                        e->setFrom(n1);
                      }
                    }

                    edge *e1;
                    e1 = new edge(edgeId++, n, n1, 0);
                    
                    g->addEdge(e1);

                    
                  }else if (isLess(n) || isGreater(n)){
                    errs() << "lt or gt\n";

                    //create nodes  to check the flags
                    node *n1;
                    constant *c1, *c2;

                    n1 = new node(nodeId++,"bsfa", nullptr);
                    n1->setOpcode(BSFA);
                    n1->setInstructionName("bsfa");
                    n1->setPredicate(n);
                    
                    c1 = new constant(nodeId++, n1, 0);
                    c2 = new constant(nodeId++, n1, 1);

                      //less 
                    if(isLess(n)){
                      
                      c2->setOpPos(0);
                      //greater 
                      }else if(isGreater(n)){
                      c1->setOpPos(0); 
                      
                      }else{
                      errs() << "Should not be in this if case (<, >)\n";
                    }
                    g->addNode(n1);
                    g->addConstant(c1);
                    g->addConstant(c2);
                    
                    //update dependencies

                    for(auto e: g->getAssociateEdges(n)){
                      if(e->getFrom()->getId() == n->getId()){
                        e->setFrom(n1);
                      }
                    }

                    edge *e1;
                    e1 = new edge(edgeId++, n, n1, 0);
                    
                    g->addEdge(e1);
                    
                  }*/
                  

              }
            }
            break;
          }
          default:
            errs() << "Instruction not supported or not defined in the ISA..." << inst->getOpcodeName()<< "\n";
            break;

        }
      }
      //Remove
      for(auto n: node_to_delete){
        //Do not use if n must be sub with another node
        g->removeNode(n);
      }
      
    }


    //TODO: Add Pragma and run pass only on pragma
    //      Check that the loop can generate only a DFG
    //      and not a CFG
    //NOTE: If the IS line is commented, some adjustments needs
    //      to be made in the addConstants function
    bool runOnLoop(Loop *L, LPPassManager &LPM) override {
      

      graph *g;
      
      Instruction *lastInst;
      Instruction *firstInst = nullptr;

      std::string name="";
      std::string filename;
      
      std::vector<BasicBlock *> bbs = L->getBlocks();
      inn++;
      nodeId = 0;
      edgeId = 0;
      filename = L->getBlocks()[0]->getParent()->getName().str() + std::to_string(inn);
      g = new graph();
      flG = filename;

      //Create all the nodes; each instruction is a node
      for (int i = 0; i < (int) bbs.size(); i++){
        for (BasicBlock::iterator inst = bbs[i]->begin(); inst != bbs[i]->end(); ++inst){
          addNode(&(*inst), g);
          lastInst = &(*inst);
          if(firstInst == nullptr)
            firstInst = &(*inst);
        }
      }
      

      //Generate DFG
      for (int i = 0; i < (int) bbs.size(); i++)
        for (BasicBlock::iterator inst = bbs[i]->begin(); inst != bbs[i]->end(); ++inst)
          addDependency(&(*inst), g);
      
      
      //Constants must be added after node and edge creation
      addConstants(g);

      std::vector<Value*> livein = getLiveIn(L->getBlocks()[0]->getParent(), g, firstInst);
      std::vector<Instruction*> liveout = getLiveOut(L->getBlocks()[0]->getParent(), g, lastInst);
      assignOperands(g);

      //Comment the following line to disable InstructionSelection
      //The files produced, can still be used by SAT-MapIt, but the 
      //assembly will be invalid
      instructionSelection(g);
      
      g->printDot(filename);

      g->printNodes(filename);
      g->printEdges(filename);

      g->printLiveInNodes(filename);
      g->printLiveOutNodes(filename);
		  
		  g->printConstants(filename);
		  g->printLiveInEdges(filename);
		  g->printLiveOutEdges(filename);


      delete g;
      
      return false;
        
    }
  };
}  

char DFG::ID = 0;
static RegisterPass<DFG> X("printDFG", "Extract the DFG of a loop",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);

static RegisterStandardPasses Y(
    PassManagerBuilder::EP_EarlyAsPossible,
    [](const PassManagerBuilder &Builder,
       legacy::PassManagerBase &PM) { PM.add(new DFG()); });
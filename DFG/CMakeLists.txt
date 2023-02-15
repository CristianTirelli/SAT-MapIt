add_llvm_library( LLVMDFG MODULE
  DFG.cpp
  node.cpp
  edge.cpp
  graph.cpp

  PLUGIN_TOOL
  opt
  )
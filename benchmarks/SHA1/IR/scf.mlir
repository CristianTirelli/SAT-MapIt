module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  func.func @SHA1(%arg0: memref<?xi32>) attributes {llvm.linkage = #llvm.linkage<external>} {
    %c80 = arith.constant 80 : index
    %c16 = arith.constant 16 : index
    %c1 = arith.constant 1 : index
    %c-3_i32 = arith.constant -3 : i32
    %c-8_i32 = arith.constant -8 : i32
    %c-14_i32 = arith.constant -14 : i32
    %c-16_i32 = arith.constant -16 : i32
    scf.for %arg1 = %c16 to %c80 step %c1 {
      %0 = arith.index_cast %arg1 : index to i32
      %1 = arith.addi %0, %c-3_i32 : i32
      %2 = arith.index_cast %1 : i32 to index
      %3 = memref.load %arg0[%2] : memref<?xi32>
      %4 = arith.addi %0, %c-8_i32 : i32
      %5 = arith.index_cast %4 : i32 to index
      %6 = memref.load %arg0[%5] : memref<?xi32>
      %7 = arith.xori %3, %6 : i32
      %8 = arith.addi %0, %c-14_i32 : i32
      %9 = arith.index_cast %8 : i32 to index
      %10 = memref.load %arg0[%9] : memref<?xi32>
      %11 = arith.xori %7, %10 : i32
      %12 = arith.addi %0, %c-16_i32 : i32
      %13 = arith.index_cast %12 : i32 to index
      %14 = memref.load %arg0[%13] : memref<?xi32>
      %15 = arith.xori %11, %14 : i32
      memref.store %15, %arg0[%arg1] : memref<?xi32>
    }
    return
  }
}

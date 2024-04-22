module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  func.func @SHA1(%arg0: memref<?xi32>) attributes {llvm.linkage = #llvm.linkage<external>} {
    %c80 = arith.constant 80 : index
    %c16 = arith.constant 16 : index
    %c1 = arith.constant 1 : index
    %c-3_i32 = arith.constant -3 : i32
    %c-8_i32 = arith.constant -8 : i32
    %c-14_i32 = arith.constant -14 : i32
    %c-16_i32 = arith.constant -16 : i32
    cf.br ^bb1(%c16 : index)
  ^bb1(%0: index):  // 2 preds: ^bb0, ^bb2
    %1 = arith.cmpi slt, %0, %c80 : index
    cf.cond_br %1, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    %2 = arith.index_cast %0 : index to i32
    %3 = arith.addi %2, %c-3_i32 : i32
    %4 = arith.index_cast %3 : i32 to index
    %5 = memref.load %arg0[%4] : memref<?xi32>
    %6 = arith.addi %2, %c-8_i32 : i32
    %7 = arith.index_cast %6 : i32 to index
    %8 = memref.load %arg0[%7] : memref<?xi32>
    %9 = arith.xori %5, %8 : i32
    %10 = arith.addi %2, %c-14_i32 : i32
    %11 = arith.index_cast %10 : i32 to index
    %12 = memref.load %arg0[%11] : memref<?xi32>
    %13 = arith.xori %9, %12 : i32
    %14 = arith.addi %2, %c-16_i32 : i32
    %15 = arith.index_cast %14 : i32 to index
    %16 = memref.load %arg0[%15] : memref<?xi32>
    %17 = arith.xori %13, %16 : i32
    memref.store %17, %arg0[%0] : memref<?xi32>
    %18 = arith.addi %0, %c1 : index
    cf.br ^bb1(%18 : index)
  ^bb3:  // pred: ^bb1
    return
  }
}


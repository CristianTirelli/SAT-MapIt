module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  func.func @GSM(%arg0: memref<?xi32>) -> i32 attributes {llvm.linkage = #llvm.linkage<external>} {
    %c40 = arith.constant 40 : index
    %c0 = arith.constant 0 : index
    %c1 = arith.constant 1 : index
    %c32767_i32 = arith.constant 32767 : i32
    %c-32768_i32 = arith.constant -32768 : i32
    %c0_i32 = arith.constant 0 : i32
    cf.br ^bb1(%c0, %c0_i32 : index, i32)
  ^bb1(%0: index, %1: i32):  // 2 preds: ^bb0, ^bb10
    %2 = arith.cmpi slt, %0, %c40 : index
    cf.cond_br %2, ^bb2, ^bb11
  ^bb2:  // pred: ^bb1
    %3 = memref.load %arg0[%0] : memref<?xi32>
    %4 = arith.cmpi slt, %3, %c0_i32 : i32
    %5 = arith.cmpi eq, %3, %c-32768_i32 : i32
    cf.cond_br %4, ^bb3, ^bb8
  ^bb3:  // pred: ^bb2
    cf.cond_br %5, ^bb4, ^bb5
  ^bb4:  // pred: ^bb3
    cf.br ^bb6(%c32767_i32 : i32)
  ^bb5:  // pred: ^bb3
    %6 = arith.subi %c0_i32, %3 : i32
    cf.br ^bb6(%6 : i32)
  ^bb6(%7: i32):  // 2 preds: ^bb4, ^bb5
    cf.br ^bb7
  ^bb7:  // pred: ^bb6
    cf.br ^bb9(%7 : i32)
  ^bb8:  // pred: ^bb2
    cf.br ^bb9(%3 : i32)
  ^bb9(%8: i32):  // 2 preds: ^bb7, ^bb8
    cf.br ^bb10
  ^bb10:  // pred: ^bb9
    %9 = arith.cmpi sgt, %8, %1 : i32
    %10 = arith.select %9, %8, %1 : i32
    %11 = arith.addi %0, %c1 : index
    cf.br ^bb1(%11, %10 : index, i32)
  ^bb11:  // pred: ^bb1
    return %1 : i32
  }
}


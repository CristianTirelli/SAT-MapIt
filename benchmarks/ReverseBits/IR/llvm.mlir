module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<"dlti.endianness", "little">, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  llvm.func @ReverseBits(%arg0: i32, %arg1: i32) -> i32 {
    %0 = llvm.mlir.constant(0 : index) : i64
    %1 = llvm.mlir.constant(1 : index) : i64
    %2 = llvm.mlir.constant(1 : i32) : i32
    %3 = llvm.mlir.constant(0 : i32) : i32
    %4 = llvm.sext %arg1 : i32 to i64
    llvm.br ^bb1(%0, %3, %arg0 : i64, i32, i32)
  ^bb1(%5: i64, %6: i32, %7: i32):  // 2 preds: ^bb0, ^bb2
    %8 = llvm.icmp "slt" %5, %4 : i64
    llvm.cond_br %8, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    %9 = llvm.shl %6, %2  : i32
    %10 = llvm.and %7, %2  : i32
    %11 = llvm.or %9, %10  : i32
    %12 = llvm.lshr %7, %2  : i32
    %13 = llvm.add %5, %1  : i64
    llvm.br ^bb1(%13, %11, %12 : i64, i32, i32)
  ^bb3:  // pred: ^bb1
    llvm.return %6 : i32
  }
}


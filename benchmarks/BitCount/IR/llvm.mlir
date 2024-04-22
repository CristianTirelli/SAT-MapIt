module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  llvm.func @BitCount(%arg0: i64) -> i32 {
    %0 = llvm.mlir.constant(-1 : i64) : i64
    %1 = llvm.mlir.constant(1 : i32) : i32
    %2 = llvm.mlir.constant(0 : i64) : i64
    %3 = llvm.mlir.constant(0 : i32) : i32
    %4 = llvm.mlir.undef : i32
    %5 = llvm.icmp "eq" %arg0, %2 : i64
    %6 = llvm.icmp "ne" %arg0, %2 : i64
    llvm.cond_br %6, ^bb1(%3, %arg0 : i32, i64), ^bb3
  ^bb1(%7: i32, %8: i64):  // 2 preds: ^bb0, ^bb2
    %9 = llvm.add %7, %1  : i32
    %10 = llvm.add %8, %0  : i64
    %11 = llvm.and %8, %10  : i64
    %12 = llvm.icmp "ne" %11, %2 : i64
    llvm.cond_br %12, ^bb2(%7, %8 : i32, i64), ^bb4(%9 : i32)
  ^bb2(%13: i32, %14: i64):  // pred: ^bb1
    %15 = llvm.add %14, %0  : i64
    %16 = llvm.and %14, %15  : i64
    %17 = llvm.add %13, %1  : i32
    llvm.br ^bb1(%17, %16 : i32, i64)
  ^bb3:  // pred: ^bb0
    %18 = llvm.select %5, %3, %4 : i1, i32
    llvm.br ^bb4(%18 : i32)
  ^bb4(%19: i32):  // 2 preds: ^bb1, ^bb3
    llvm.return %19 : i32
  }
}


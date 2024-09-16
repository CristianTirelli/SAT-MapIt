module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  func.func @BitCount(%arg0: i64) -> i32 attributes {llvm.linkage = #llvm.linkage<external>} {
    %c-1_i64 = arith.constant -1 : i64
    %c1_i32 = arith.constant 1 : i32
    %c0_i64 = arith.constant 0 : i64
    %c0_i32 = arith.constant 0 : i32
    %0 = llvm.mlir.undef : i32
    %1 = arith.cmpi eq, %arg0, %c0_i64 : i64
    %2 = arith.cmpi ne, %arg0, %c0_i64 : i64
    %3 = scf.if %2 -> (i32) {
      %4:3 = scf.while (%arg1 = %c0_i32, %arg2 = %arg0) : (i32, i64) -> (i32, i32, i64) {
        %5 = arith.addi %arg1, %c1_i32 : i32
        %6 = arith.addi %arg2, %c-1_i64 : i64
        %7 = arith.andi %arg2, %6 : i64
        %8 = arith.cmpi ne, %7, %c0_i64 : i64
        scf.condition(%8) %5, %arg1, %arg2 : i32, i32, i64
      } do {
      ^bb0(%arg1: i32, %arg2: i32, %arg3: i64):
        %5 = arith.addi %arg3, %c-1_i64 : i64
        %6 = arith.andi %arg3, %5 : i64
        %7 = arith.addi %arg2, %c1_i32 : i32
        scf.yield %7, %6 : i32, i64
      }
      scf.yield %4#0 : i32
    } else {
      %4 = arith.select %1, %c0_i32, %0 : i32
      scf.yield %4 : i32
    }
    return %3 : i32
  }
}

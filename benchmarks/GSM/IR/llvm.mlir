module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  llvm.func @GSM(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: i64, %arg3: i64, %arg4: i64) -> i32 {
    %0 = llvm.mlir.undef : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)>
    %1 = llvm.insertvalue %arg0, %0[0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %2 = llvm.insertvalue %arg1, %1[1] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %3 = llvm.insertvalue %arg2, %2[2] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %4 = llvm.insertvalue %arg3, %3[3, 0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %5 = llvm.insertvalue %arg4, %4[4, 0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %6 = llvm.mlir.constant(40 : index) : i64
    %7 = llvm.mlir.constant(0 : index) : i64
    %8 = llvm.mlir.constant(1 : index) : i64
    %9 = llvm.mlir.constant(32767 : i32) : i32
    %10 = llvm.mlir.constant(-32768 : i32) : i32
    %11 = llvm.mlir.constant(0 : i32) : i32
    llvm.br ^bb1(%7, %11 : i64, i32)
  ^bb1(%12: i64, %13: i32):  // 2 preds: ^bb0, ^bb5
    %14 = llvm.icmp "slt" %12, %6 : i64
    llvm.cond_br %14, ^bb2, ^bb6
  ^bb2:  // pred: ^bb1
    %15 = llvm.getelementptr %arg1[%12] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    %16 = llvm.load %15 : !llvm.ptr -> i32
    %17 = llvm.icmp "slt" %16, %11 : i32
    %18 = llvm.icmp "eq" %16, %10 : i32
    llvm.cond_br %17, ^bb3, ^bb5(%16 : i32)
  ^bb3:  // pred: ^bb2
    llvm.cond_br %18, ^bb5(%9 : i32), ^bb4
  ^bb4:  // pred: ^bb3
    %19 = llvm.sub %11, %16  : i32
    llvm.br ^bb5(%19 : i32)
  ^bb5(%20: i32):  // 3 preds: ^bb2, ^bb3, ^bb4
    %21 = llvm.icmp "sgt" %20, %13 : i32
    %22 = llvm.select %21, %20, %13 : i1, i32
    %23 = llvm.add %12, %8  : i64
    llvm.br ^bb1(%23, %22 : i64, i32)
  ^bb6:  // pred: ^bb1
    llvm.return %13 : i32
  }
}


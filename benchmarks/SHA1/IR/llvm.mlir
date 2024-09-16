module attributes {dlti.dl_spec = #dlti.dl_spec<#dlti.dl_entry<f80, dense<128> : vector<2xi32>>, #dlti.dl_entry<i64, dense<64> : vector<2xi32>>, #dlti.dl_entry<i1, dense<8> : vector<2xi32>>, #dlti.dl_entry<i8, dense<8> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr, dense<64> : vector<4xi32>>, #dlti.dl_entry<f64, dense<64> : vector<2xi32>>, #dlti.dl_entry<f16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i16, dense<16> : vector<2xi32>>, #dlti.dl_entry<i32, dense<32> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<271>, dense<32> : vector<4xi32>>, #dlti.dl_entry<!llvm.ptr<272>, dense<64> : vector<4xi32>>, #dlti.dl_entry<f128, dense<128> : vector<2xi32>>, #dlti.dl_entry<!llvm.ptr<270>, dense<32> : vector<4xi32>>, #dlti.dl_entry<"dlti.stack_alignment", 128 : i32>, #dlti.dl_entry<"dlti.endianness", "little">>, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128", llvm.target_triple = "x86_64-unknown-linux-gnu", "polygeist.target-cpu" = "x86-64", "polygeist.target-features" = "+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87", "polygeist.tune-cpu" = "generic"} {
  llvm.func @SHA1(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: i64, %arg3: i64, %arg4: i64) {
    %0 = llvm.mlir.undef : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)>
    %1 = llvm.insertvalue %arg0, %0[0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %2 = llvm.insertvalue %arg1, %1[1] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %3 = llvm.insertvalue %arg2, %2[2] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %4 = llvm.insertvalue %arg3, %3[3, 0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %5 = llvm.insertvalue %arg4, %4[4, 0] : !llvm.struct<(ptr, ptr, i64, array<1 x i64>, array<1 x i64>)> 
    %6 = llvm.mlir.constant(80 : index) : i64
    %7 = llvm.mlir.constant(16 : index) : i64
    %8 = llvm.mlir.constant(1 : index) : i64
    %9 = llvm.mlir.constant(-3 : i32) : i32
    %10 = llvm.mlir.constant(-8 : i32) : i32
    %11 = llvm.mlir.constant(-14 : i32) : i32
    %12 = llvm.mlir.constant(-16 : i32) : i32
    llvm.br ^bb1(%7 : i64)
  ^bb1(%13: i64):  // 2 preds: ^bb0, ^bb2
    %14 = llvm.icmp "slt" %13, %6 : i64
    llvm.cond_br %14, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    %15 = llvm.trunc %13 : i64 to i32
    %16 = llvm.add %15, %9  : i32
    %17 = llvm.sext %16 : i32 to i64
    %18 = llvm.getelementptr %arg1[%17] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    %19 = llvm.load %18 : !llvm.ptr -> i32
    %20 = llvm.add %15, %10  : i32
    %21 = llvm.sext %20 : i32 to i64
    %22 = llvm.getelementptr %arg1[%21] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    %23 = llvm.load %22 : !llvm.ptr -> i32
    %24 = llvm.xor %19, %23  : i32
    %25 = llvm.add %15, %11  : i32
    %26 = llvm.sext %25 : i32 to i64
    %27 = llvm.getelementptr %arg1[%26] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    %28 = llvm.load %27 : !llvm.ptr -> i32
    %29 = llvm.xor %24, %28  : i32
    %30 = llvm.add %15, %12  : i32
    %31 = llvm.sext %30 : i32 to i64
    %32 = llvm.getelementptr %arg1[%31] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    %33 = llvm.load %32 : !llvm.ptr -> i32
    %34 = llvm.xor %29, %33  : i32
    %35 = llvm.getelementptr %arg1[%13] : (!llvm.ptr, i64) -> !llvm.ptr, i32
    llvm.store %34, %35 : i32, !llvm.ptr
    %36 = llvm.add %13, %8  : i64
    llvm.br ^bb1(%36 : i64)
  ^bb3:  // pred: ^bb1
    llvm.return
  }
}


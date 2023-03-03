; ModuleID = 'Reverse_bits.c'
source_filename = "Reverse_bits.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

; Function Attrs: nofree norecurse nosync nounwind readnone ssp uwtable
define i32 @ReverseBits(i32 %index, i32 %NumBits) local_unnamed_addr #0 {
entry:
  %cmp6.not = icmp eq i32 %NumBits, 0
  br i1 %cmp6.not, label %for.end, label %for.body

for.body:                                         ; preds = %entry, %for.body
  %rev.09 = phi i32 [ %or, %for.body ], [ 0, %entry ]
  %i.08 = phi i32 [ %inc, %for.body ], [ 0, %entry ]
  %index.addr.07 = phi i32 [ %shr, %for.body ], [ %index, %entry ]
  %shl = shl i32 %rev.09, 1
  %and = and i32 %index.addr.07, 1
  %or = or i32 %shl, %and
  %shr = lshr i32 %index.addr.07, 1
  %inc = add nuw i32 %i.08, 1
  %exitcond.not = icmp eq i32 %inc, %NumBits
  br i1 %exitcond.not, label %for.end, label %for.body, !llvm.loop !6

for.end:                                          ; preds = %for.body, %entry
  %rev.0.lcssa = phi i32 [ 0, %entry ], [ %or, %for.body ]
  ret i32 %rev.0.lcssa
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind readnone ssp uwtable willreturn
define i32 @main() local_unnamed_addr #1 {
entry:
  ret i32 0
}

attributes #0 = { nofree norecurse nosync nounwind readnone ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nofree norecurse nosync nounwind readnone ssp uwtable willreturn "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 12, i32 3]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 14.0.0 (https://github.com/llvm/llvm-project.git 5c77ed0330c47ad8fa4b229bceb6c33c76536961)"}
!6 = distinct !{!6, !7, !8}
!7 = !{!"llvm.loop.mustprogress"}
!8 = !{!"llvm.loop.unroll.disable"}

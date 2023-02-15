; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

; Function Attrs: nounwind ssp uwtable
define i32 @main(i32 %argc, i8** nocapture readnone %argv) local_unnamed_addr #0 {
entry:
  %call = tail call i64 @time(i64* null) #3
  %conv = trunc i64 %call to i32
  tail call void @srand(i32 %conv) #3
  ret i32 1
}

declare void @srand(i32) local_unnamed_addr #1

declare i64 @time(i64*) local_unnamed_addr #1

; Function Attrs: nofree norecurse nosync nounwind readonly ssp uwtable
define zeroext i16 @isqrt32(i32* nocapture readonly %in_ptr) local_unnamed_addr #2 {
entry:
  %0 = load i32, i32* %in_ptr, align 4, !tbaa !6
  br label %while.body

while.body:                                       ; preds = %entry, %while.body
  %result.024 = phi i16 [ 0, %entry ], [ %spec.select, %while.body ]
  %mask.023 = phi i16 [ 16384, %entry ], [ %1, %while.body ]
  %or22 = or i16 %result.024, %mask.023
  %conv3 = zext i16 %or22 to i32
  %mul = mul nuw i32 %conv3, %conv3
  %cmp5.not = icmp ugt i32 %mul, %0
  %spec.select = select i1 %cmp5.not, i16 %result.024, i16 %or22
  %1 = lshr i16 %mask.023, 1
  %tobool.not = icmp ult i16 %mask.023, 2
  br i1 %tobool.not, label %cleanup, label %while.body, !llvm.loop !10

cleanup:                                          ; preds = %while.body
  ret i16 %spec.select
}

attributes #0 = { nounwind ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #2 = { nofree norecurse nosync nounwind readonly ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 12, i32 3]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 14.0.0 (https://github.com/llvm/llvm-project.git 5c77ed0330c47ad8fa4b229bceb6c33c76536961)"}
!6 = !{!7, !7, i64 0}
!7 = !{!"int", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C/C++ TBAA"}
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.mustprogress"}
!12 = !{!"llvm.loop.unroll.disable"}

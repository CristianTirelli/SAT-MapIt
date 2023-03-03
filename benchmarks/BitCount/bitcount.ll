; ModuleID = 'bitcount.c'
source_filename = "bitcount.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

@.str = private unnamed_addr constant [3 x i8] c"%d\00", align 1

; Function Attrs: nofree norecurse nosync nounwind readnone ssp uwtable
define i32 @bit_count(i64 %x) local_unnamed_addr #0 {
entry:
  %cmp = icmp eq i64 %x, 0
  br i1 %cmp, label %cleanup, label %do.body

do.body:                                          ; preds = %entry, %do.body
  %x.addr.0 = phi i64 [ %and, %do.body ], [ %x, %entry ]
  %n.0 = phi i32 [ %inc, %do.body ], [ 0, %entry ]
  %inc = add nuw nsw i32 %n.0, 1
  %sub = add nsw i64 %x.addr.0, -1
  %and = and i64 %sub, %x.addr.0
  %cmp1.not = icmp eq i64 %and, 0
  br i1 %cmp1.not, label %cleanup, label %do.body, !llvm.loop !6

cleanup:                                          ; preds = %do.body, %entry
  %retval.0 = phi i32 [ 0, %entry ], [ %inc, %do.body ]
  ret i32 %retval.0
}

; Function Attrs: nofree nounwind ssp uwtable
define i32 @main() local_unnamed_addr #1 {
entry:
  %call1 = tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) getelementptr inbounds ([3 x i8], [3 x i8]* @.str, i64 0, i64 0), i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @printf(i8* nocapture noundef readonly, ...) local_unnamed_addr #2

attributes #0 = { nofree norecurse nosync nounwind readnone ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nounwind ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #2 = { nofree nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }

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

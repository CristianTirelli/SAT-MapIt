; ModuleID = 'sha.c'
source_filename = "sha.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

; Function Attrs: nofree norecurse nosync nounwind readonly ssp uwtable
define i32 @sha1(i32* nocapture readonly %W) local_unnamed_addr #0 {
entry:
  br label %for.body

for.cond.cleanup:                                 ; preds = %for.body
  %add10 = shl nsw i32 %add5, 1
  %add11 = add nsw i32 %add10, %A.037
  %add12 = add nsw i32 %add11, %or9
  %add13 = add nsw i32 %add12, %C.039
  %add14 = add nsw i32 %add13, %D.040
  ret i32 %add14

for.body:                                         ; preds = %entry, %for.body
  %indvars.iv = phi i64 [ 0, %entry ], [ %indvars.iv.next, %for.body ]
  %E.041 = phi i32 [ 0, %entry ], [ %D.040, %for.body ]
  %D.040 = phi i32 [ 0, %entry ], [ %C.039, %for.body ]
  %C.039 = phi i32 [ 0, %entry ], [ %or9, %for.body ]
  %B.038 = phi i32 [ 0, %entry ], [ %A.037, %for.body ]
  %A.037 = phi i32 [ 0, %entry ], [ %add5, %for.body ]
  %shl = shl i32 %A.037, 5
  %shr = ashr i32 %A.037, 27
  %or = or i32 %shl, %shr
  %and = and i32 %C.039, %B.038
  %neg = xor i32 %B.038, -1
  %and1 = and i32 %D.040, %neg
  %arrayidx = getelementptr inbounds i32, i32* %W, i64 %indvars.iv
  %0 = load i32, i32* %arrayidx, align 4, !tbaa !6
  %or2 = add i32 %or, 1518500249
  %add = add i32 %or2, %and
  %add3 = add i32 %add, %and1
  %add4 = add i32 %add3, %E.041
  %add5 = add i32 %add4, %0
  %shl7 = shl i32 %B.038, 30
  %shr8 = ashr i32 %B.038, 2
  %or9 = or i32 %shl7, %shr8
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, 20
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !10
}

; Function Attrs: nofree nosync nounwind readnone ssp uwtable
define i32 @main() local_unnamed_addr #1 {
entry:
  ret i32 0
}

attributes #0 = { nofree norecurse nosync nounwind readonly ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }

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

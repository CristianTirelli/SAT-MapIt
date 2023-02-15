; ModuleID = 'sha.c'
source_filename = "sha.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

; Function Attrs: nofree norecurse nosync nounwind ssp uwtable
define void @sha_transform(i32* nocapture %W) local_unnamed_addr #0 {
entry:
  br label %for.body

for.cond.cleanup:                                 ; preds = %for.body
  ret void

for.body:                                         ; preds = %entry, %for.body
  %indvars.iv = phi i64 [ 16, %entry ], [ %indvars.iv.next, %for.body ]
  %0 = add nsw i64 %indvars.iv, -3
  %arrayidx = getelementptr inbounds i32, i32* %W, i64 %0
  %1 = load i32, i32* %arrayidx, align 4, !tbaa !6
  %2 = add nsw i64 %indvars.iv, -8
  %arrayidx3 = getelementptr inbounds i32, i32* %W, i64 %2
  %3 = load i32, i32* %arrayidx3, align 4, !tbaa !6
  %xor = xor i32 %3, %1
  %4 = add nsw i64 %indvars.iv, -14
  %arrayidx6 = getelementptr inbounds i32, i32* %W, i64 %4
  %5 = load i32, i32* %arrayidx6, align 4, !tbaa !6
  %xor7 = xor i32 %xor, %5
  %6 = add nsw i64 %indvars.iv, -16
  %arrayidx10 = getelementptr inbounds i32, i32* %W, i64 %6
  %7 = load i32, i32* %arrayidx10, align 4, !tbaa !6
  %xor11 = xor i32 %xor7, %7
  %arrayidx13 = getelementptr inbounds i32, i32* %W, i64 %indvars.iv
  store i32 %xor11, i32* %arrayidx13, align 4, !tbaa !6
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, 80
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !10
}

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: nofree nosync nounwind readnone ssp uwtable
define i32 @main() local_unnamed_addr #2 {
entry:
  %W = alloca [80 x i32], align 16
  %0 = bitcast [80 x i32]* %W to i8*
  call void @llvm.lifetime.start.p0i8(i64 320, i8* nonnull %0) #3
  br label %for.body.i

for.body.i:                                       ; preds = %for.body.i, %entry
  %indvars.iv.i = phi i64 [ 16, %entry ], [ %indvars.iv.next.i, %for.body.i ]
  %1 = add nsw i64 %indvars.iv.i, -3
  %arrayidx.i = getelementptr inbounds [80 x i32], [80 x i32]* %W, i64 0, i64 %1
  %2 = load i32, i32* %arrayidx.i, align 4, !tbaa !6
  %3 = add nsw i64 %indvars.iv.i, -8
  %arrayidx3.i = getelementptr inbounds [80 x i32], [80 x i32]* %W, i64 0, i64 %3
  %4 = load i32, i32* %arrayidx3.i, align 4, !tbaa !6
  %xor.i = xor i32 %4, %2
  %5 = add nsw i64 %indvars.iv.i, -14
  %arrayidx6.i = getelementptr inbounds [80 x i32], [80 x i32]* %W, i64 0, i64 %5
  %6 = load i32, i32* %arrayidx6.i, align 4, !tbaa !6
  %xor7.i = xor i32 %xor.i, %6
  %7 = add nsw i64 %indvars.iv.i, -16
  %arrayidx10.i = getelementptr inbounds [80 x i32], [80 x i32]* %W, i64 0, i64 %7
  %8 = load i32, i32* %arrayidx10.i, align 4, !tbaa !6
  %xor11.i = xor i32 %xor7.i, %8
  %arrayidx13.i = getelementptr inbounds [80 x i32], [80 x i32]* %W, i64 0, i64 %indvars.iv.i
  store i32 %xor11.i, i32* %arrayidx13.i, align 4, !tbaa !6
  %indvars.iv.next.i = add nuw nsw i64 %indvars.iv.i, 1
  %exitcond.not.i = icmp eq i64 %indvars.iv.next.i, 80
  br i1 %exitcond.not.i, label %sha_transform.exit, label %for.body.i, !llvm.loop !10

sha_transform.exit:                               ; preds = %for.body.i
  call void @llvm.lifetime.end.p0i8(i64 320, i8* nonnull %0) #3
  ret i32 0
}

attributes #0 = { nofree norecurse nosync nounwind ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { argmemonly mustprogress nofree nosync nounwind willreturn }
attributes #2 = { nofree nosync nounwind readnone ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
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

; ModuleID = 'stringsearch.c'
source_filename = "stringsearch.c"
target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-apple-macosx12.3.0"

@lowervec = local_unnamed_addr global <{ [256 x i8], [745 x i8] }> <{ [256 x i8] c"\00\01\02\03\04\05\06\07\08\09\0A\0B\0C\0D\0E\0F\10\11\12\13\14\15\16\17\18\19\1A\1B\1C\1D\1E\1F !\22#$%&'()*+,-./0123456789:;<=>?@abcdefghijklmnopqrstuvwxyz[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\7F\80\81\82\83\84\85\86\87\88\89\8A\8B\8C\8D\8E\8F\90\91\92\93\94\95\96\97\98\99\9A\9B\9C\9D\9E\9F\A0\A1\A2\A3\A4\A5\A6\A7\A8\A9\AA\AB\AC\AD\AE\AF\B0\B1\B2\B3\B4\B5\B6\B7\B8\B9\BA\BB\BC\BD\BE\BF\C0\C1\C2\C3\C4\C5\C6\C7\C8\C9\CA\CB\CC\CD\CE\CF\D0\D1\D2\D3\D4\D5\D6\D7\D8\D9\DA\DB\DC\DD\DE\DF\E0\E1\E2\E3\E4\E5\E6\E7\E8\E9\EA\EB\EC\ED\EE\EF\F0\F1\F2\F3\F4\F5\F6\F7\F8\F9\FA\FB\FC\FD\FE\FF", [745 x i8] zeroinitializer }>, align 16

; Function Attrs: nofree norecurse nosync nounwind readonly ssp uwtable
define i32 @stringsearch(i32 %patlen, i32 %skip2, i8* nocapture readonly %pattern) local_unnamed_addr #0 {
entry:
  %sub = add i32 %patlen, -1
  %cmp21 = icmp sgt i32 %patlen, 1
  br i1 %cmp21, label %for.body.lr.ph, label %for.end

for.body.lr.ph:                                   ; preds = %entry
  %idxprom424 = zext i32 %sub to i64
  %arrayidx5 = getelementptr inbounds i8, i8* %pattern, i64 %idxprom424
  %0 = load i8, i8* %arrayidx5, align 1, !tbaa !6
  %idxprom6 = sext i8 %0 to i64
  %arrayidx7 = getelementptr inbounds [1001 x i8], [1001 x i8]* bitcast (<{ [256 x i8], [745 x i8] }>* @lowervec to [1001 x i8]*), i64 0, i64 %idxprom6
  %1 = load i8, i8* %arrayidx7, align 1, !tbaa !6
  %wide.trip.count = zext i32 %sub to i64
  br label %for.body

for.body:                                         ; preds = %for.body.lr.ph, %for.body
  %indvars.iv = phi i64 [ 0, %for.body.lr.ph ], [ %indvars.iv.next, %for.body ]
  %i.023 = phi i32 [ 0, %for.body.lr.ph ], [ %inc, %for.body ]
  %skip2.addr.022 = phi i32 [ %skip2, %for.body.lr.ph ], [ %skip2.addr.1, %for.body ]
  %arrayidx = getelementptr inbounds i8, i8* %pattern, i64 %indvars.iv
  %2 = load i8, i8* %arrayidx, align 1, !tbaa !6
  %idxprom1 = sext i8 %2 to i64
  %arrayidx2 = getelementptr inbounds [1001 x i8], [1001 x i8]* bitcast (<{ [256 x i8], [745 x i8] }>* @lowervec to [1001 x i8]*), i64 0, i64 %idxprom1
  %3 = load i8, i8* %arrayidx2, align 1, !tbaa !6
  %cmp9 = icmp eq i8 %3, %1
  %4 = xor i32 %i.023, -1
  %sub12 = add i32 %4, %patlen
  %skip2.addr.1 = select i1 %cmp9, i32 %sub12, i32 %skip2.addr.022
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %inc = add nuw nsw i32 %i.023, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond.not, label %for.end, label %for.body, !llvm.loop !9

for.end:                                          ; preds = %for.body, %entry
  %skip2.addr.0.lcssa = phi i32 [ %skip2, %entry ], [ %skip2.addr.1, %for.body ]
  ret i32 %skip2.addr.0.lcssa
}

; Function Attrs: nofree nosync nounwind readonly ssp uwtable
define i32 @main() local_unnamed_addr #1 {
entry:
  ret i32 0
}

attributes #0 = { nofree norecurse nosync nounwind readonly ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readonly ssp uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 12, i32 3]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 14.0.0 (https://github.com/llvm/llvm-project.git 5c77ed0330c47ad8fa4b229bceb6c33c76536961)"}
!6 = !{!7, !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C/C++ TBAA"}
!9 = distinct !{!9, !10, !11}
!10 = !{!"llvm.loop.mustprogress"}
!11 = !{!"llvm.loop.unroll.disable"}

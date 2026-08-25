# 284_USER_tab_delimiter_rejection.spec
# Edge Case: Horizontal TAB (\t) used instead of Space (0x20) as token delimiter
# Expected: IRC protocol strictly mandates 0x20 spaces. Line with TAB command fails command lookup (421).
CLIENTS C1

C1 SEND USER	ali406	0	*	:Ali406 Smith
C1 EXPECT 421 * Unknown command.

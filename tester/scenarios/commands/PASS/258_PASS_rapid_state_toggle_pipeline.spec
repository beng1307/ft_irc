# 258_PASS_rapid_state_toggle_pipeline.spec
# Adversarial Attack: Toggling PASS valid/invalid state repeatedly in a single pipeline
CLIENTS C1

C1 SEND_RAW PASS 1234\r\nNICK PassToggle\r\nPASS wrong1\r\nPASS 1234\r\nPASS wrong2\r\nUSER passtoggle 0 * :Toggle\r\n
C1 EXPECT 464 * :Password incorrect
C1 EXPECT 464 * :Password incorrect

# Registration must be blocked because the last PASS before USER was invalid
C1 SEND JOIN #test
C1 EXPECT 451 * :You have not registered

# 264_PASS_interleaved_failed_pass_and_restricted_commands.spec
# Adversarial Probe: Interleaving invalid PASS attempts with restricted commands to probe state leakage
CLIENTS C1

C1 SEND PASS wrong1
C1 EXPECT 464 * :Password incorrect

C1 SEND JOIN #secret
C1 EXPECT 451 * :You have not registered

C1 SEND PASS wrong2
C1 EXPECT 464 * :Password incorrect

C1 SEND MODE #secret +k secretkey
C1 EXPECT 451 * :You have not registered

C1 SEND PASS wrong3
C1 EXPECT 464 * :Password incorrect

C1 SEND TOPIC #secret :hacked
C1 EXPECT 451 * :You have not registered

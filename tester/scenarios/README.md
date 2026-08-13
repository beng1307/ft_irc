# IRC scenario catalog

Every spec starts with a short comment describing its contract. This index is
the central map of the executable integration coverage. Run all suites with
`../run_scenarios`, or select a spec by its filename fragment.

## Registration

| Spec | Coverage |
| --- | --- |
| `registration/01_pass_failure.spec` | Wrong password returns `464`; later identity commands do not register the client. |
| `registration/02_fragmentation.spec` | A fragmented nickname is buffered until the complete IRC line arrives. |
| `registration/11_parameter_errors.spec` | Missing parameters for PASS, NICK, and USER; errors do not disconnect the client. |
| `registration/12_duplicate_nick_recovery.spec` | Duplicate nickname rejection and recovery with a new nickname. |
| `registration/13_command_case_and_fragmentation.spec` | Case-insensitive commands and multiple fragmented lines. |

## Messaging

| Spec | Coverage |
| --- | --- |
| `messaging/03_basic_registration_and_privmsg.spec` | Two registered clients exchange a direct private message. |
| `messaging/14_negative_targets.spec` | Unknown nick/channel and missing PRIVMSG parameters. |
| `messaging/15_recipient_isolation.spec` | Direct messages reach only their recipient; channel messages reach members. |

## Channels

| Spec | Coverage |
| --- | --- |
| `channels/membership/04_channel_join_and_broadcast.spec` | Channel creation, join notifications, and channel message broadcast. |
| `channels/membership/16_part_and_rejoin.spec` | PART, membership removal, broadcast, and rejoin. |
| `channels/membership/17_kick_cleanup.spec` | Kicked users lose channel access but keep their TCP connection. |
| `channels/modes/06_channel_key.spec` | Key-protected channel rejects a missing key and accepts the correct key. |
| `channels/modes/07_channel_limit.spec` | User limit rejects an extra member and accepts a raised limit. |
| `channels/modes/09_channel_operator_privs.spec` | Operator grant and operator-only KICK behavior. |
| `channels/modes/18_mode_queries_and_removal.spec` | MODE query plus removal of invite, key, limit, topic, and operator modes. |
| `channels/modes/19_mode_errors.spec` | Non-operator, non-member, missing-argument, and unknown-mode errors. |
| `channels/invite-topic/05_invite_and_kick.spec` | Invite-only access, invitation, JOIN, and KICK flow. |
| `channels/invite-topic/08_channel_topic.spec` | Topic restriction rejects regular users and allows the operator. |
| `channels/invite-topic/20_invite_errors.spec` | INVITE authorization and target/channel error paths. |
| `channels/invite-topic/21_topic_query_and_persistence.spec` | Topic query, restriction, empty topic, and persistence after rejoin. |

## Lifecycle and transport

| Spec | Coverage |
| --- | --- |
| `lifecycle/10_client_disconnect.spec` | QUIT broadcast, disconnect detection, and remaining-client liveness. |
| `lifecycle/22_abrupt_close_and_reconnect.spec` | Abrupt peer close, continued service, and nick reuse after reconnect. |
| `lifecycle/23_pause_and_bounded_flood.spec` | Suspended client, bounded channel flood, and resumed delivery. |

All scenarios are grouped by protocol area and included in the recursive
all-tests run.

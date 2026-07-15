# Recovery

Persist each attempt and next retry time. Retry a transient provider per configuration,
then try fallbacks. If all are temporarily unavailable, transition to
`WAITING_FOR_PROVIDER`, persist, wait five minutes by default, probe, and resume the
same operation; `null` maximum cycles means continue until cancellation. Compare candidate
diff hashes, requirements, findings, test results, changed files, and commit hashes to
detect no progress; exhaust configured providers before `BLOCKED_BY_NO_PROGRESS`.

# Candidate commit lifecycle

After deterministic completion checks, the controller stages only allowed project files
and creates one phase candidate commit. It creates a detached review worktree from that
exact SHA. When review requires changes, it preserves evidence, uses the original
implementation worktree for fixes, validates them, and performs `git commit --amend`.
Every new SHA receives a new detached review. Immediately before merge, require:
approved SHA equals phase branch HEAD, clean implementation worktree, unchanged reviewed
diff, valid base relation, passing required tests, and approval referencing that SHA.

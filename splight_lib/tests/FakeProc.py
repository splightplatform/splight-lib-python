import sys

action = sys.argv[1]

if action == 'exit_ok':
    sys.exit(0)
elif action == 'exit_fail':
    sys.exit(1)
elif action == 'run_forever':
    while True:
        pass
else:
    sys.exit(1)
